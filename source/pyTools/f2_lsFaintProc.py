#! /usr/bin/env python
#    2017-Jan-11  RAShaw.astro@gmail.com

#import sys
import copy
import glob
import yaml
from pyraf import iraf
from pyraf.iraf import gemini
from pyraf.iraf import gemtools, gnirs, niri
from pyraf.iraf import f2
import fileSelect as fs

# Transform python list to comma-separated IRAF filelist string
def flistToStr(prefix, fileList):
    return ','.join(str(prefix+x) for x in fileList)

def f2_LSproc():
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

    print ("### Begin Processing F2/Longslit Images ###")
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

    # Standard Star Attributes
    with open('stdStar.yml','r') as yf:
        stdStar = yaml.load(yf)
    
    print ("=== Creating MasterCals ===")
    print (" --Creating Dark MasterCal--")
    # Set the task parameters, beginning with the F2 keyword translation.
    gnirs.nsheaders.unlearn()
    gnirs.nsheaders('f2')
    f2.f2prepare.unlearn()
    prepPars = pars['f2prepPars']
    gemtools.gemcombine.unlearn()
    darkCombPars = pars['gemcombinePars']
    # Iterate over exposure times used in science/calibration exposures.
    qs = qd['JH']
    for t in qd['Durations']['T_exp']:
        qs['T_exp'] = t
        suffix = '_' + str(int(t))
        # The following SQL generates the list of full-frame files to process.
        SQL = fs.createQuery('dark', qs)
        darkFiles = fs.fileListQuery(dbFile, SQL, qs)
        if len(darkFiles) > 1:
            for f in darkFiles:
                f2.f2prepare(f, **prepPars)
            gemtools.gemcombine(flistToStr('p', darkFiles), 'MCdark'+suffix,
                                **darkCombPars)

    # Clean up.
    iraf.imdelete('pS*.fits')

    print (" -- Creating GCAL Spectral Flat-Field MasterCals --")
    # Select on any date, then set task parameters.
    qs.update({'DateObs':'*'})
    gemtools.gemexpr.unlearn()
    gemtools.gemextn.unlearn()
    gemtools.gemarith.unlearn()
    gemarithPars = pars['gemarithPars']
    f2.f2cut.unlearn()
    f2cutPars = pars['f2cutPars']
    gnirs.nsflat.unlearn()
    nsflatPars = pars['nsflatPars']
    # There is only one exposure duration for flats.
    darkFile = 'MCdark' + '_4'
    flatFiles = fs.fileListQuery(dbFile, fs.createQuery('gcalFlat', qs), qs)
    if len(flatFiles) > 1:
        for f in flatFiles:
            f2.f2prepare(f, **prepPars)
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f,
                              **gemarithPars)
            f2.f2cut('dp'+f, **f2cutPars)
        # Now sum the flats and remove the response.
        gnirs.nsflat(flistToStr('cdp',flatFiles), flatfile='MCflat',
                                **nsflatPars)
    # Clean up.
    iraf.imdelete('pS*.fits,dpS*.fits')

    print (" -- Creating Wavelength MasterCals --")
    # Set task parameters.
    prepPars.update({'bpm':'MCflat_bpm.pl'})
    gnirs.nsreduce.unlearn()
    arcProcPars = pars['nsreducePars']
    # Arc name mapping
    with open('lamps.yml','r') as yf:
        lamps = yaml.load(yf)

    # Process Arc exposures; we're not combining them.
    darkFile = 'MCdark_15'
    qs.update({'DateObs':'2014-11-07:2014-12-04'})
    arcFiles = fs.fileListQuery(dbFile, fs.createQuery('arc', qs), qs)
    arcs = lamps['arcs']
    if len(arcFiles) > 0:
        for f in arcFiles:
            f2.f2prepare(f, **prepPars)
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f,
                              **gemarithPars)
            gnirs.nsreduce('dp'+f, outimages=arcs['dp'+f], **arcProcPars)

    # Now derive the dispersion solution.
    gnirs.nswavelength.unlearn()
    nswavePars = pars['nswavePars']
    for f in arcs.values():
        gnirs.nswavelength(f, **nswavePars)

    print (" -- Processing Standard Star exposures --")
    stdProcPars = copy.deepcopy(arcProcPars)
    stdProcPars.update({'outimages':'','fl_sky':'yes'})
    gnirs.nscombine.unlearn()
    stdCombPars = pars['nscombinePars']
    darkFile = 'MCdark_5'

    for t,sPars in stdStar.iteritems():
        qs.update({'Object':t, 'DateObs':sPars['date']})
        stdFiles = fs.fileListQuery(dbFile, fs.createQuery('std', qs), qs)
        if len(stdFiles) > 0:
            stdProcPars['skyrange'] = sPars['skyrange']
            for f in stdFiles:
                f2.f2prepare(f, **prepPars)
                gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f,
                                  **gemarithPars)
            gnirs.nsreduce(flistToStr('dp', stdFiles), **stdProcPars)
            gnirs.nscombine(flistToStr('rdp', stdFiles),
                            output=sPars['outFile'], **stdCombPars)

    # Clean up.
    iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

    gnirs.nsfitcoords.unlearn()
    nsfitcrdPars = pars['nsfitcrdPars']
    gnirs.nstransform.unlearn()
    nstransPars = pars['nstransPars']
    gnirs.nsextract.unlearn()
    nsextrPars = pars['nsextrPars']

    for t,sPars in stdStar.iteritems():
        inFile = sPars['outFile']
        arcFile = sPars['arcFile']
        gnirs.nsfitcoords(inFile, lamptransf=arcFile, **nsfitcrdPars)
        gnirs.nstransform (inFile, **nstransPars)
        gnirs.nsextract('t'+inFile, **extrPars)
        # Condition the output images to exclude spurious extreme values
        iraf.imreplace('xtf'+inFile+'.fits[1][1:160], 0.)

    print ("=== Processing Science Files ===")
    print (" -- Performing Basic Processing --")

    # Set task parameters.
    sciProcPars = copy.deepcopy(stdProcPars)
    sciCombPars = pars['nscombinePars']
    sciCombPars.update({'tolerance':1.0,'fl_cross':'no','fl_shiftint':'yes'})
    darkFile = 'MCdark_300'
    qs.update({'Object':'WISE 0350-56','ObsType':'OBJECT'})
    gemtools.gemexpr.unlearn()

    # Use the observing log to separate the observing sequences
    # Two consecutive observing epochs on 2014-11-07
    qs.update({'DateObs':'2014-11-07'})
    imgEnd = 'S20141107S0234'
    sciFiles = fs.fileListQuery(dbFile, fs.createQuery('sciSpec', qs), qs)
    sf = {'ep1':sciFiles[:sciFiles.index(imgEnd)+1]}
    sf['ep2'] = sciFiles[sciFiles.index(imgEnd)+1:]

    # One observing epoch on 2014-12-04
    qs.update({'DateObs':'2014-12-04'})
    sf['ep3'] = fs.fileListQuery(dbFile, fs.createQuery('sciSpec', qs), qs)

    for ep, sciFiles in sf.iteritems():
        if len(sciFiles) > 0:
            for f in sciFiles:
                f2.f2prepare(f, **prepPars)
                gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f,
                                  **gemarithPars)
            gnirs.nsreduce(flistToStr('dp', sciFiles), **sciProcPars)
            outFile = 'WISE_0350-56_' + ep
            gnirs.nscombine(flistToStr('rdp', sciFiles), output=outFile,
                                       **sciCombPars)
            iraf.imreplace(outFile+'.fits[1]',-30.,upper=-30.)
            iraf.imreplace(outFile+'.fits[1]',30.,lower=30.)

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
    for e in epoch:
        ep = wise[e]
        inFile = ep['inFile']
        telFile = ep['telluric']
        gnirs.nstelluric('xtf'+inFile, telFile, **nstelluricPars)

    # Process the Standard Star
    print (" -- Derive the Flux calibration --")

    # Process the science targets.

    print ("=== Finished Calibration Processing ===")

if __name__ == "__main__":
    f2_LSproc()
