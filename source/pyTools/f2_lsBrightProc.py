#! /usr/bin/env python
#    2017-Feb-24  RAShaw.astro@gmail.com

import copy
import os.path
import yaml
from pyraf import iraf
from pyraf.iraf import gemini
from pyraf.iraf import gemtools, gnirs, niri
from pyraf.iraf import f2
import fileSelect as fs

def flistToStr(prefix, fileList):
    '''Create a comma-separated string of file names (with a prefix)
        from a python list.
        '''
    return ','.join(str(prefix+x) for x in fileList)

def f2_lsBrightProc():
    '''
    FLAMINGOS-2 Data Reduction Cookbook companion script to the chapter:
       "Reduction of F2 Longslit Spectra with PyRAF"

    PyRAF script to:
    Process F2 spectra for WISE J035000.32-565830.2, in program GS-2014B-Q-17.

    The names for the relevant header keywords and their expected values are
    described in the DRC chapter entitled "Supplementary Material"

    Perform the following starting in the parent work directory:
        cd /path/to/work_directory

    Place this fileSelect.py module in your work directory. Now execute this
    script from the unix prompt:
        python F2_LSproc.py
    '''

    print ("### Begin Processing F2/Longslit Spectra ###")
    print ("###")

    # This whole example depends upon first having built an sqlite3 database of metadata:
    #    cd ./raw
    #    python obslog.py obsLog.sqlite3
    # Path to raw exposures
    rawpath = './raw/'
    # Observing log database
    dbFile = rawpath + 'obsLog.sqlite3'
    iraf.imtype = 'fits'

    # Configuration parameters:
    # IRAF Task Parameters
    with open('lsTaskPars.yml','r') as yf:
        pars = yaml.load(yf)

    # Observing Configurations
    with open('obsConfig.yml','r') as yf:
        qd = yaml.load(yf)

    print ("=== Creating MasterCals ===")
    print (" --Creating Dark MasterCals--")
    # Set the task parameters, beginning with the F2 keyword translation.
    gnirs.nsheaders.unlearn()
    gnirs.nsheaders('f2')
    f2.f2prepare.unlearn()
    prepPars = pars['f2prepPars']
    gemtools.gemcombine.unlearn()
    darkCombPars = pars['gemcombinePars']
    # Iterate over exposure times used in science/calibration exposures.
    qs = qd['JH']
    for t in [4,5,6,10,15,30,40,80]:
        qs['T_exp'] = t
        MCdark = 'MCdark_' + str(t)
        darkFiles = fs.fileListQuery(dbFile, fs.createQuery('dark', qs), qs)
        if len(darkFiles) > 1:
            f2.f2prepare(flistToStr('', darkFiles), **prepPars)
            gemtools.gemcombine(flistToStr('p', darkFiles), MCdark,
                                **darkCombPars)
            iraf.imdelete('pS*.fits')
        else:
            print 'No Dark images available for Texp: ', t

    print (" -- Creating GCAL Spectral Flat-Field MasterCals --")
    gemtools.gemexpr.unlearn()
    gemtools.gemextn.unlearn()
    gemtools.gemarith.unlearn()
    gemarithPars = pars['gemarithPars']
    f2.f2cut.unlearn()
    f2cutPars = pars['f2cutPars']
    gnirs.nsflat.unlearn()
    nsflatPars = pars['nsflatPars']
    for g,qs in qd.iteritems():
        qs['Texp'] = qs['Texp_flat']
        MCdark = 'MCdark_' + str(int(qs['Texp']))
        # and now the flats...
        flatFiles = fs.fileListQuery(dbFile, fs.createQuery('gcalFlat', qs), qs)
        if len(flatFiles) > 1:
            f2.f2prepare(flistToStr('', flatFiles), **prepPars)
            for f in flatFiles:
                gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f,
                              **gemarithPars)
            f2.f2cut(flistToStr('dp', flatFiles), **f2cutPars)
            # Remove the response
            nsflatPars.update({
                'bpmfile': qs['MCbpm'],
                'flattitle': 'GCAL Flat: ' + g
            })
            gnirs.nsflat(flistToStr('cdp',flatFiles), flatfile=qs['MCflat'],
                                **nsflatPars)
        iraf.imdelete('pS*.fits,dpS*.fits,cdpS*.fits')

    print (" -- Creating Wavelength MasterCals --")
    # Set task parameters.
    prepPars.update({'bpm':'MCflat_bpm.pl'})
    gnirs.nsreduce.unlearn()
    arcProcPars = pars['nsreducePars']
    # Arc name mapping
    with open('lamps.yml','r') as yf:
        lamps = yaml.load(yf)

    arcs = lamps['arcs']
    # Process Arc exposures; we're not combining them.
    for g,qs in qd.iteritems():
        prepPars.update({'bpm':qs['MCbpm']})
        # Create the dark for the arc exposure duration.
        qs['Texp'] = qs['Texp_arc']
        MCdark = 'MCdark_' + str(int(qs['Texp']))
        arcFiles = fs.fileListQuery(dbFile, fs.createQuery('arc', qs), qs)
        arcs = lamps['arcs']
        if len(arcFiles) > 0:
            f2.f2prepare(flistToStr('', arcFiles), **prepPars)
            arcProcPars['flatimage'] = qs['MCflat']
            for f in arcFiles:
                gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f,
                                  **gemarithPars)
                gnirs.nsreduce('dp'+f, outimages=arcs['dp'+f], **arcProcPars)
            iraf.imdelete('pS*.fits,dpS*.fits')

    # Now derive the dispersion solution.
    gnirs.nswavelength.unlearn()
    nswavePars = pars['nswavePars']
    for f in ['Ar_JH_061','Ar_HK_067']:
        gnirs.nswavelength(f, **nswavePars)

    print (" -- Processing Target exposures --")
    # Target metadata
    with open('targets.yml','r') as yf:
        targets = yaml.load(yf)

    targProcPars = copy.deepcopy(arcProcPars)
    targProcPars.update({
        'outimages':'',
        'fl_sky':'yes'
    })
    gnirs.nscombine.unlearn()
    targCombPars = pars['nscombinePars']
    prepPars['bpm'] = 'MCbpm_JH.pl'

    for t,sPars in targets.iteritems():
        print 'Processing target: ', t
        for g,qs in qd.iteritems():
            qs.update({'Object':t})
            targType = sPars['type']
            targFiles = fs.fileListQuery(dbFile, fs.createQuery(targType, qs), qs)
            if len(targFiles) > 0:
                targProcPars.update({
                    'skyrange': sPars['skyrange'],
                    'flatimage': qs['MCflat']
                })
                f2.f2prepare(flistToStr('', targFiles), **prepPars)
                MCdark = sPars['darkFile'][g]
                for f in targFiles:
                    gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f,
                                      **gemarithPars)
                targProcPars['flatimage'] = qs['MCflat']
                gnirs.nsreduce(flistToStr('dp', targFiles), **targProcPars)
                outFile = qs['Object'][:-1] + '_' + g
                if len(targFiles) > 1:
                    gnirs.nscombine(flistToStr('rdp', targFiles),
                                               output=outFile, **targCombPars)
                else:
                    iraf.imrename(flistToStr('rdp', targFiles), outFile)

    # Clean up.
    iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

    gnirs.nsfitcoords.unlearn()
    nsfitcrdPars = pars['nsfitcrdPars']
    gnirs.nstransform.unlearn()
    nstransPars = pars['nstransPars']
    gnirs.nsextract.unlearn()
    targExtrPars = pars['nsextrPars']

############# Got to here...
    for t,sPars in stdStar.iteritems():
        inFile = sPars['outFile']
        arcFile = sPars['arcFile']
        gnirs.nsfitcoords(inFile, lamptransf=arcFile, **nsfitcrdPars)
        gnirs.nstransform (inFile, **nstransPars)
        gnirs.nsextract('t'+inFile, **extrPars)

    ### End of basic processing. Continue with advanced processing.

    print (" -- Performing Extraction --")
    # Set task parameters.
   # Target name mapping
    with open('wise.yml','r') as yf:
        wise = yaml.load(yf)

    sciExtrPars = copy.deepcopy(stdExtrPars)
    sciExtrPars.update({'line':425,'upper':8,'lower':-8,'background':'median'})
    gnirs.telluric.unlearn()
    nstelluricPars = pars['nstelluricPars']
    epoch = ['ep2','ep1','ep3']
    for e in epoch:
        ep = wise[e]
        inFile = ep['inFile']
        arcFile = ep['arcFile']
        gnirs.nsfitcoords(inFile, lamptransf=arcFile, **nsfitcrdPars)
        gnirs.nstransform ('f'+inFile, **nstransPars)
        sciExtrPars['trace] = ep['trace']
        inFile = ep['inFile']
        gnirs.nsextract('tf'+inFile, **sciExtrPars)

    print (" -- Performing Telluric Correction --")
    # Set task parameters.
    gnirs.nstelluric.unlearn()
    nstelluricPars = pars['nstelluricPars']

    target = 'xtfJ0126-5505'
    std = 'xtfHIP6546'
    for g in qd:
        inFile = target + '_' + g
        telFile = std + '_' + g
        gnirs.nstelluric(inFile, telFile, **nstelluricPars)

    print ("=== Finished Calibration Processing ===")

if __name__ == "__main__":
    f2_LSproc()
