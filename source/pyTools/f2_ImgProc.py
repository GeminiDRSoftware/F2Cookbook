#! /usr/bin/env python
#    2017-Feb-09  RAShaw.astro@gmail.com

#import sys
import copy
import glob
import yaml
from pyraf import iraf
from pyraf.iraf import gemini
from pyraf.iraf import f2
from pyraf.iraf import gemtools, gnirs, niri
import fileSelect as fs

# Transform python list to comma-separated IRAF filelist string
def flistToStr(prefix, fileList):
    return ','.join(str(prefix+x) for x in fileList)

# Create a generator to transform a lengthly list into N chunks
def chunks(inList, chunkSize):
    n = max(1, chunkSize)
    return (inList[i:i+n] for i in xrange(0, len(inList), n))

def f2_ImgProc():
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
    with open('imgTaskPars.yml','r') as yf:
        pars = yaml.load(yf)

    # Observing Configurations
    with open('imgObsConfig.yml','r') as yf:
        qd = yaml.load(yf)

    print ("=== Creating MasterCals ===")
    print (" --Creating Flat-field MasterCals--")
    # Set the task parameters, beginning with the F2 keyword translation.
    gnirs.nsheaders.unlearn()
    gnirs.nsheaders('f2')
    f2.f2prepare.unlearn()
    prepPars = pars['f2prepPars']
    gemtools.gemexpr.unlearn()
    gemtools.gemextn.unlearn()
    niri.niflat.unlearn()
    niflatPars = pars['niflatPars']

    qs = qd['Y']
    qs['Texp'] = 3
    prepPars['outprefix'] = 'd'
    # The following generates an SQL template to contain the list of short dark
    # exposures to process.
    SQL = fs.createQuery('dark', qs)
    shortDarks = fs.fileListQuery(dbFile, SQL, qs)
    prepPars['outprefix'] = 'd'
    f2.f2prepare(flistToStr('',shortDarks), **prepPars)
    prepPars['outprefix'] = 'p'
        
    # Create the GCAL flat-field and BPM for all filters except Ks
    for filt in ['Y','J','H']:
        print 'Creating flat for filter: ', filt
        qs = qd[filt]
        qs['GCALflat'] = 'GCALflat_' + filt
        qs['Texp'] = qs['Texp_flat']
        lampsOn = fs.fileListQuery(dbFile, fs.createQuery('lampsOn', qs), qs)
        lampsOff = fs.fileListQuery(dbFile, fs.createQuery('lampsOff', qs), qs)
        calFiles = lampsOn + lampsOff
        if len(lampsOn) > 1 and len(lampsOff) > 1:
            f2.f2prepare(flistToStr('',calFiles), **prepPars)
            niflatPars.update({'darks':flistToStr('d',shortDarks)})
            niflatPars.update({'lampsoff':flistToStr('p',lampsOff)})
            niri.niflat(flistToStr('p',lampsOn), flatfile=qs['GCALflat'],
                                    **niflatPars)
        else:
            print 'Insufficient input files for filter: ', filt
        iraf.imdelete('pS*.fits')

    print (" -- Creating Dark MasterCals --")
    gemtools.gemcombine.unlearn()
    darkCombPars = pars['gemcombinePars']
    prepPars['bpm'] = 'MCflat_J_bpm.pl'
    # Iterate over exposure times used in science/calibration exposures.
    durations = [120, 60, 15, 8]
    qs = qd['J']
    qs['dateObs'] = '2013-10-20:2013-11-30'
    for t in durations:
        qs['Texp'] = t
        MCdark = 'MCdark_' + str(int(t))
        darkFiles = fs.fileListQuery(dbFile, fs.createQuery('dark', qs), qs)
        if len(darkFiles) > 1:
            f2.f2prepare(flistToStr('', darkFiles), **prepPars)
            gemtools.gemcombine(flistToStr('p', darkFiles), MCdark,
                                **darkCombPars)
        iraf.imdelete('pS*.fits')

    print (" -- Creating Ks Flat-Field --")
    filt = 'Ks'
    qs = qd[filt]
    GCALflat = 'GCALflat_' + filt
    qs.update({
        'MCdark': 'MCdark_' + str(int(qs['Texp_flat'])),
        'GCALflat': GCALflat,
        'MCbpm': GCALflat + '_bpm'
    })
    qs['MCdark'] = 'MCdark_' + str(int(qs['Texp_flat']))
    prepPars['bpm'] = 'GCALflat_J_bpm.pl'
    flatCombPars = copy.deepcopy(darkCombPars)
    flatCombPars.update({
        'statsec':'[350:1750,350:1750]',
        'bpmfile':'GCALflat_J_bpm.pl'
    })
    gemtools.gemarith.unlearn()
    gemarithPars = pars['gemarithPars']
    gemtools.gemexpr.unlearn()
    gemexprPars = pars['gemexprPars']
    flatComb = qs['GCALflat'] + '_comb'

    qs['DateObs'] = '2013-11-29'
    lampsOff = fs.fileListQuery(dbFile, fs.createQuery('lampsOff', qs), qs)
    f2.f2prepare(flistToStr('',lampsOff), **prepPars)
    for f in lampsOff:
        gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f, **gemarithPars)
    gemtools.gemcombine(flistToStr('dp', lampsOff), flatComb, **flatCombPars)

    # Use the mean for the normalization constant
    flatCombSect = flatComb+'.fits[1][350:1750,350:1750]'
    iraf.imstat(flatCombSect,fields='mean,stddev,min,max,midpt')
    mean_Ks = 21894.

    # Adopt the J-band BPM and replace bad pixels in normalized flat
    iraf.copy('GCALflat_J_bpm.pl',qs['MCbpm'])
    gemtools.gemexpr('(b > 0) ? 1 : a/'+mean_Ks, GCALflat, flatComb,
                     'MCbpm', **gemexprPars)

    # Clean up
    iraf.imdelete('dS2013*.fits,pS2013*.fits,dpS2013*.fits')

    print ("=== Science Processing ===")
    print (" -- Creating Sky Images --")
    # Set task parameters for first & second invocation of nireduce.
    niri.nireduce.unlearn()
    darkProcPars = pars['nireducePars']
    flatProcPars = copy.deepcopy(darkProcPars)
    flatProcPars.update({
        'outprefix':'f',
        'fl_dark':'no',
        'fl_flat':'yes',
    })
    skyProcPars = copy.deepcopy(flatProcPars)
    skyProcPars.update({
        'outprefix':'s',
        'fl_dark':'no',
        'fl_flat':'no',
        'fl_sky':'yes',
        'fl_autosky':'yes'
    })
    niri.nisky.unlearn()
    niskyPars = pars['niskyPars']
    flatCombPars.update({
        'statsec':'[350:1750,350:1750]',
        'scale':'mean',
    })
    skyCombPars = copy.deepcopy(flatCombPars)
    skyCombPars.update({
        'lthreshold':0.
    })

    # Set the calibration information and the list of science exposures for each filter.
    for filt,qs in qd.iteritems():
        qs.update({
            'DateObs':'2013-11-21',
            'Object':'W0413-4750%',
            'ObsType':'OBJECT',
            'Texp':qs['Texp_sci'],
            'MCdark':'MCdark_'+str(int(qs['Texp_sci'])),
            'MCsky':'Sky_'+filt,
            'MCflat':'GCALflat_'+filt,
            'MCbpm':'GCALflat_'+filt+'_bpm'
        })
        qs['sciFiles'] = fs.fileListQuery(dbFile,
                                          fs.createQuery('sciImg', qs), qs)
    # Perform basic reductions: dark & flat corrections, create sky/combine sky
    for filt,qs in qd.iteritems():
        print 'Creating sky for filter: ', filt
        darkProcPars.update({
            'darkimage':qs['MCdark'],
            'outprefix':filt+'d'
        })
        i = 0
        for sciFiles in chunks(qs['sciFiles'], ditherCycle):
            f2.f2prepare(flistToStr('', sciFiles), **prepPars)
            niri.nireduce(flistToStr('p', sciFiles), **darkProcPars)
            # nsheaders sets nisky.statsec = '[350:1750,350:1750]'
            i += 1
            outImage = qs['MCsky'] + '-' + str(i)
            niri.nisky (flistToStr(filt+'dp', sciFiles), outimage=outImage,
                        **niskyPars)
            # Apply flat-field to the sky frame
            flatProcPars['flatimage'] = qs['MCflat']
            niri.nireduce (qs['MCsky']+'-'+str(i), **flatProcPars)
            iraf.imdelete('pS*.fits')
        if i > 1:
            gemtools.gemcombine('f'+qs['MCsky']+'-*', qs['MCsky'], **skyCombPars)
        else:
            iraf.imrename('f'+qs['MCsky']+'-1','f'+qs['MCsky'])

    print (" -- Processing Science images --")
    gemtools.imcoadd.unlearn()
    imcoaddPars = pars['imcoaddPars']
    ditherCycle = 9
    for filt,qs in qd.iteritems():
        print 'Creating science image for filter: ', filt
        flatProcPars['flatimage'] = qs['MCflat']
        imcoaddPars['badpixfile'] = qs['MCbpm']
        prefix = filt + 'dp'
        i = 0
        for sciFiles in chunks(qs['sciFiles'],ditherCycle):
            i += 1
            niri.nireduce(flistToStr(prefix, sciFiles), **flatProcPars)
            skyProcPars['skyimage'] = 'f'+qs['MCsky'] + '-' + str(i)
            niri.nireduce(flistToStr('f'+prefix, sciFiles), **skyProcPars)
            outFile = qs['Object'][:-1] + '_' + filt + '-' + str(i)
            gemtools.imcoadd(flistToStr('sf'+prefix, sciFiles),
                             outimage=outFile, **imcoaddPars)
        iraf.delete('*_mag,*_cen,*_pos,*_trn,*badpix.pl')
        iraf.imdel('*_avg.fits,*_mag.fits,*_med.fits,*_trn.fits')

    for filt in qd.iteritems():
        iraf.imdelete(filt+'dpS*')
        iraf.imdelete('f'+filt+'dpS*')
        iraf.imdelete('sf'+filt+'dpS*')

    print (" -- Combining Dither Sets --")
    skyCombPars['zero'] = 'median'
    for filt in ['H','Ks']:
        qs = qd[filt]
        outFile = qs['Object'][:-1] + '_' + filt
        inFiles = outFile + '-*'
        gemtools.gemcombine(inFiles, outFile, **flatCombPars)

    print ("=== Finished Calibration Processing ===")

if __name__ == "__main__":
    f2_ImgProc()
