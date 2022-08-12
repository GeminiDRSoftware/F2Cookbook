#!/usr/bin/env python
import os, yaml
import numpy as np
from pyraf import iraf
from pyraf.iraf import images, onedspec, gemini
from pyraf.iraf import gemtools, gnirs, f2
from astropy.table import Table, Row, unique
from astropy.io import fits
#---------------------------------------------------------------------
class Observation(Row):
    def __init__(self, table, fname):
        if fname not in table['File']:
            raise ValueError('{} not found in Observation Log'.format(fname))
        self._table = table
        self._index = np.argmax(table['File']==fname)

    def __getitem__(self, item):
        return self._table[item][self._index]

class ObsLog(object):
    def __init__(self, fname):
        # Load observation log and strip trailing spaces from string fields
        obslog = fname if isinstance(fname, Table) else Table.read(fname)
        obslog = obslog[obslog['use_me']]
        obslog = obslog[np.logical_or(obslog['Disperser'] != 'Open',
                                      obslog['ObsType'] == 'DARK')]
        for col in obslog.colnames:
            try:
                obslog[col] = [v.strip() for v in obslog[col]]
            except AttributeError:
                pass
        self.table = obslog

    def __getitem__(self, fname):
        # Return table row for a specific filename
        return Observation(self.table, fname)

    def query(self, qd):
        # Return obslog rows that match all requirements
        # Deal with date ranges but don't alter the query dictionary
        try:
            date1, date2 = str(qd['Date']).split(':')
        except ValueError:  # Only one date
            good = self.table['Date'] == str(qd['Date'])
        except KeyError:  # No date constraint
            good = np.array([True] * len(self.table))
        else:
            good = np.logical_and(self.table['Date'] >= date1,
                                  self.table['Date'] <= date2)
        # Specific observation range
        if 'first' in qd:
            good &= self.table['File'] >= qd['first']
        if 'last' in qd:
            good &= self.table['File'] <= qd['last']
        # Other constraints
        good &= np.logical_and.reduce([self.table[k]==v for k,v in qd.items()
                                       if (k in self.table.colnames and
                                           k != 'Date')])
        return self.table[good]

    def file_query(self, qd):
        # Return a list of filenames matching the query
        return list(self.query(qd)['File'])
#---------------------------------------------------------------------
def filelist(prefix, fileList):
    # Transform python list to comma-separated string
    return ','.join(str(prefix+f) for f in fileList)

def merge_dicts(dict1, dict2, allow_new=True):
    # Merge two dicts, optionally allowing/forbidding new keys
    d = dict1.copy()
    d.update({k: v for k, v in dict2.items() if (allow_new or k in dict1)})
    return d

def get_pars(*tasks):
    # Unlearn tasks and read parameters from yaml file, returning dicts
    with open('mosTaskPars.yml', 'r') as yf:
        pars = yaml.safe_load(yf)
    pkg_dict = {'f2': f2, 'ns': gnirs, 'ge': gemtools}
    for task in tasks:
        pkg = pkg_dict.get(task[:2], onedspec)
        getattr(getattr(pkg, task), 'unlearn')()
    return [pars[task] for task in tasks]

def apply_fitcoords(infile, telFile, database):
    # Copy header keywords from one frame to another
    gemtools.gemhedit.upfile = ''
    gemtools.gemhedit(infile+'[0]', 'NSFITCOO', 'N/A',
                      'UT Time stamp for NSFITCOORDS')
    os.rename(infile+'.fits', 'f'+infile+'.fits')
    infile = 'f'+infile+'[SCI]'
    gemtools.gemhedit(infile, 'FCDB', database, '')
    gemtools.gemhedit(infile, 'FCFIT1','f'+telFile+'_SCI_1_lamp', '')
    gemtools.gemhedit(infile, 'FCX1', 1, '')
    images.imutil.imgets(infile, 'naxis1')
    nx = images.imutil.imgets.value
    gemtools.gemhedit(infile, 'FCX2', nx, '')
    gemtools.gemhedit(infile, 'FCNX', nx, '')

def make_contiguous_lists(files):
    # Turn a list of input files into multiple lists of contiguously-named ones
    lists = []
    this_list = [files.pop(0)]
    while files:
        next_item = files.pop(0)
        if (next_item[:10] == this_list[-1][:10] and
            int(next_item[-4:]) == int(this_list[-1][-4:])+1):
            this_list.append(next_item)
        else:
            lists.append(this_list)
            this_list = [next_item]
    lists.append(this_list)
    return lists

def check_cals(input_dict):
    # Check that calibration files exist
    all_ok = True
    for k1, v1 in input_dict.items():
        for k2, v2 in v1.items():
            if k2 not in ('input', 'slitim', 'bpm'):
                fname = v2 if '.' in v2 else v2+'.fits'
                if not (os.path.exists(fname) or fname.startswith('S20')):
                    all_ok = False
                    print "{} does not exist (used for {})".format(fname, k1)
    if not all_ok:
        exit(1)
#----------------------------------------------------------------------
#---- DON'T EDIT ABOVE THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ----
#----------------------------------------------------------------------

#----------------------- DARKS: See Section 6.3 -----------------------
def selectDarks(obslog):
    # Make a dict: key=output dark file; value=input files
    dark_dict = {}
    qd = {'ObsType': 'DARK'}
    exptimes = set(obslog.query(qd)['Texp'])
    for t in exptimes:
        darkFiles = obslog.file_query(merge_dicts(qd, {'Texp': t}))
        outfile = 'MCdark_'+str(int(t))
        dark_dict[outfile] = {'input': darkFiles}
    return dark_dict

def reduceDarks(dark_dict):
    prepPars, combPars = get_pars('f2prepare', 'gemcombine')
    for outfile, file_dict in dark_dict.items():
        darkFiles = file_dict['input']
        for f in darkFiles:
            f2.f2prepare(f, **prepPars)
        if len(darkFiles) > 1:
            gemtools.gemcombine(filelist('p', darkFiles), outfile, **combPars)
        else:
            iraf.imrename('p'+darkFiles[0], outfile)
    iraf.imdelete('pS*.fits')

#----------------------- FLATS: See Section 6.4 -----------------------
def selectFlats(obslog):
    # key=(output flat, output bpm); value=[dark, [input files]]
    ls_flat_dict = {}
    mos_flat_dict = {}
    qd = {'ObsType': 'FLAT', 'GCAL Shutter': 'OPEN'}
    params = ('Texp', 'Disperser', 'Mask', 'Filter')
    flatConfigs = unique(obslog.query(qd)[params])
    for config in flatConfigs:
        t, grism, mask, filt = config
        config_dict = dict(zip(params, config))
        flatFiles = sorted(obslog.file_query(merge_dicts(qd, config_dict)))
        # This format for MCdark files is suitable for nightly darks
        file_dict = {'dark': 'MCdark_'+str(int(t)),
                     'bpm': 'MCbpm_{}_{}.pl'.format(grism, filt)}

        if 'pix-slit' in mask:
            # Long-slit flat (for standard) -- create BPM
            outfile = '_'.join(['MCflat', grism, filt])
            file_dict['input'] = flatFiles
            ls_flat_dict[outfile] = file_dict.copy()
        else:
            # Find groups of flats and combine each group
            for infiles in make_contiguous_lists(flatFiles):
                file_dict['input'] = infiles
                seq = infiles[0]
                if len(infiles) > 1:
                    seq += "_"+infiles[-1][-4:]
                outfile = 'flat_'+seq
                slitFile = 'slits_'+seq
                mos_flat_dict[outfile] = merge_dicts(file_dict,
                                                     {'slitim': slitFile})
    return ls_flat_dict, mos_flat_dict

#-------------------- LS FLATS: See Section 6.4.1 ----------------------
def reduceLSFlats(flat_dict):
    prepPars, cutPars, arithPars, flatPars, combPars = get_pars('f2prepare',
                                'f2cut', 'gemarith', 'nsflat', 'gemcombine')
    for outfile, file_dict in flat_dict.items():
        darkFile = file_dict['dark']
        bpmFile = file_dict['bpm']
        flatFiles = file_dict['input']
        for f in flatFiles:
            f2.f2prepare(f, **prepPars)
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)
            f2.f2cut('dp'+f, **cutPars)
        flatPars.update({'flatfile': outfile, 'bpmfile': bpmFile})
        gnirs.nsflat(filelist('cdp', flatFiles), **flatPars)
    iraf.imdelete('pS*.fits,dpS*.fits,cdpS*.fits')

#------------------- MOS FLATS: See Section 6.4.2 ---------------------
def reduceMOSFlats(flat_dict):
    prepPars, cutPars, arithPars, flatPars, combPars, sdistPars = get_pars('f2prepare',
                                                                           'f2cut', 'gemarith', 'nsflat', 'gemcombine', 'nssdist')
    for outfile, file_dict in flat_dict.items():
        darkFile = file_dict['dark']
        bpmFile = file_dict['bpm']
        slitFile = file_dict['slitim']
        refImage = file_dict.get('reference', '')
        flatFiles = file_dict['input']
        nsflat_inputs = filelist('cdp', flatFiles)
        for f in flatFiles:
            f2.f2prepare(f, **merge_dicts(prepPars, {'bpm': bpmFile}))
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)
        if not refImage:
            if len(flatFiles) > 1:
                # Stack images and use this to make reference
                gemtools.gemcombine(filelist('dp', flatFiles), 'stack', **combPars)
                cutPars.update({'gradimage': 'stack', 
                                'refimage': '', 'outslitim': slitFile})
                f2.f2cut('stack', outimages='cut_'+outfile, **cutPars)
                # Use the cut stack as a reference for individual images
                cutPars.update({'gradimage': '', 'refimage': 'cut_'+outfile})
                f2.f2cut(filelist('dp', flatFiles), **cutPars)
            else:
                # If only one image, use it to cut itself and ensure it
                # has an appropriate name
                cutPars.update({'gradimage': 'dp'+flatFiles[0],
                                'refimage': '', 'outslitim': slitFile})
                f2.f2cut(filelist('dp', flatFiles), outimages='cut_'+outfile,
                         **cutPars)
                nsflat_inputs = 'cut_'+outfile
            gnirs.nssdist(slitFile, **sdistPars)
        else:
            cutPars.update({'gradimage': '', 'refimage': refImage})
            f2.f2cut(filelist('dp', flatFiles), **cutPars)

        flatPars.update({'flatfile': outfile, 'bpmfile': ''})
        gnirs.nsflat(nsflat_inputs, **flatPars)

        iraf.imdelete('stack.fits')
    iraf.imdelete('pS*.fits,dpS*.fits,cdpS*.fits')

#------------------------ ARCS: See Section 6.5 -----------------------
def selectArcs(obslog):
    with open('mosTargets.yml', 'r') as yf:
        config = yaml.safe_load(yf)

    ls_arc_dict = {}
    mos_arc_dict = {}
    arcFiles = obslog.file_query({'ObsType': 'ARC'})
    params = ('Texp', 'Disperser', 'Mask', 'Filter')
    # Do not stack arcs; reduce each separately
    for f in arcFiles:
        t, grism, mask, filt = obslog[f][params]
        file_dict = {'dark': 'MCdark_'+str(int(t)),
                     'bpm': 'MCbpm_{}_{}'.format(grism, filt),
                     'input': [f]}
        outfile = 'arc_'+f

        possible_flats = obslog.file_query({'ObsType': 'FLAT',
                                            'GCAL Shutter': 'CLOSED',
                                            'Texp': t})
        for flat in possible_flats:
            if flat[:10] == f[:10] and abs(int(flat[10:])-int(f[10:])) == 1:
                file_dict['dark'] = flat
                break

        if 'pix-slit' in mask:
            file_dict['flat'] = 'MCflat_{}_{}'.format(grism, filt)
            ls_arc_dict[outfile] = file_dict.copy()
        else:
            for sci_dict in config.values():
                if sci_dict.get('arc') == outfile:
                    # Use the same flat for this arc as the science frame
                    # it's going to calibrate
                    flatFile = sci_dict['flat']
                    file_dict['flat'] = flatFile
                    file_dict['slits'] = flatFile.replace('flat_', 'slits_')
                    file_dict['reference'] = 'cut_'+flatFile
                    mos_arc_dict[outfile] = file_dict.copy()
                    break
    return ls_arc_dict, mos_arc_dict

def reduceArcs(arc_dict):
    prepPars, arithPars, redPars, fitcrdPars, transPars = get_pars('f2prepare',
                                                                             'gemarith', 'nsreduce', 'nsfitcoords', 'nstransform')
    for outfile, file_dict in arc_dict.items():
        (wavePars,) = get_pars('nswavelength')
        darkFile = file_dict['dark']
        flatFile = file_dict.get('flat')
        slitsFile = file_dict.get('slits')
        refFile = file_dict.get('reference', '')
        bpmFile = file_dict['bpm']
        arcFiles = file_dict['input']
        for f in arcFiles:
            f2.f2prepare(f, **merge_dicts(prepPars, {'bpm': bpmFile}))
            # K-band arcs may have a single exposure to remove thermal emission
            # so that exposure will need to be prepared
            if darkFile.startswith('S20'):
                f2.f2prepare(darkFile, **merge_dicts(prepPars, {'bpm': bpmFile}))
                darkFile = 'p'+darkFile
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)
        # Flatfields not required for arcs
        if flatFile:
            redPars.update({'fl_flat': 'yes', 'flatimage': flatFile})
        else:
            redPars['fl_flat'] = 'no'
        redPars['refimage'] = refFile
        gnirs.nsreduce(filelist('dp', arcFiles), **redPars)
        if len(arcFiles) > 1:
            arc = 'tmp_'+outfile
            gemcombine(filelist('rdp', arcFiles), arc, **arithPars)
        else:
            arc = 'rdp'+arcFiles[0]
        if slitsFile:
            gnirs.nsfitcoords(arc, sdisttransf=slitsFile, **fitcrdPars)
            gnirs.nstransform('f'+arc, **transPars)
            iraf.imdelete(arc+',f'+arc)
            arc = 'tf'+arc
            wavePars.update({'step': 5})
        gnirs.nswavelength(arc, outspectra=outfile, **wavePars)
        iraf.imdelete(arc)
    iraf.imdelete('*pS*.fits,dpS*.fits')

#---------------------- TARGETS: See Section 6.6 ----------------------
def selectTargets(obslog):
    # Configuation file: see Section 5.2.1
    with open('mosTargets.yml', 'r') as yf:
        config = yaml.safe_load(yf)

    # key=output file; value=[dark, flat, bpm, arc, [input files]]
    std_dict = {}
    # key=output file; value=[dark, flat, bpm, arc, telluric, [input files]]
    sci_dict = {}
    qd = {'ObsType': 'OBJECT'}
    for outfile, pars in config.items():
        infiles = obslog.file_query(merge_dicts(qd, pars))
        t, grism, filt, mask = obslog[infiles[0]]['Texp', 'Disperser',
                                                  'Filter', 'Mask']
        file_dict = {'dark': pars.get('dark', 'MCdark_'+str(int(t))),
                     'bpm': pars.get('bpm', 'MCbpm_{}_{}'.format(grism, filt)),
                     'flat': pars.get('flat', 'MCflat_{}_{}'.format(grism, filt)),
                     'arc': pars['arc'],
                     'input': infiles}
        try:
            file_dict['telluric'] = pars['telluric']
        except KeyError:  # standard
            std_dict[outfile] = file_dict.copy()
        else:
            flatFile = file_dict['flat']
            file_dict.update({'slits': flatFile.replace('flat_', 'slits_'),
                              'reference': 'cut_'+flatFile})
            sci_dict[outfile] = file_dict.copy()
    return std_dict, sci_dict

def reduceStandards(std_dict):
    (prepPars, arithPars, fitcooPars, transPars, extrPars, redPars,
     combPars) = get_pars('f2prepare', 'gemarith', 'nsfitcoords', 
                          'nstransform', 'nsextract', 'nsreduce', 'nscombine')
    redPars['fl_sky'] = 'yes'
    combPars['fl_cross'] = 'yes'

    # Reopen configuation file for additional task parameters
    with open('mosTargets.yml', 'r') as yf:
        config = yaml.safe_load(yf)

    for outfile, file_dict in std_dict.items():
        darkFile = file_dict['dark']
        flatFile = file_dict['flat']
        arcFile = file_dict['arc']
        prepPars['bpm'] = file_dict['bpm']
        stdFiles = file_dict['input']
        for f in stdFiles:
            f2.f2prepare(f, **prepPars)
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)

        # Pull in any additional parameters from config (e.g., skyrange)
        pars = merge_dicts(redPars, config[outfile].get('nsreduce', {}))
        gnirs.nsreduce(filelist('dp', stdFiles), flatimage=flatFile, **pars)
        gnirs.nscombine(filelist('rdp', stdFiles), output=outfile, **combPars)

        gnirs.nsfitcoords(outfile, lamptransf=arcFile, **fitcooPars)
        gnirs.nstransform('f'+outfile, **transPars)
        gnirs.nsextract('tf'+outfile, **extrPars)
        iraf.imdelete('f'+outfile+',tf'+outfile)
    iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

def reduceScience(sci_dict):
    (prepPars, arithPars, fitcooPars, transPars, extrPars, redPars, combPars,
     telPars) = get_pars('f2prepare', 'gemarith', 'nsfitcoords', 'nstransform',
                          'nsextract', 'nsreduce', 'nscombine', 'nstelluric')
    redPars['fl_sky'] = 'yes'

    # Reopen configuation file for additional task parameters
    with open('mosTargets.yml', 'r') as yf:
        config = yaml.safe_load(yf)

    for outfile, file_dict in sci_dict.items():
        prepPars['bpm'] = file_dict['bpm']
        darkFile = file_dict['dark']
        flatFile = file_dict['flat']
        refFile = file_dict['reference']
        slitsFile = file_dict['slits']
        arcFile = file_dict['arc']
        telFile = file_dict['telluric']
        sciFiles = file_dict['input']

        for f in sciFiles:
            f2.f2prepare(f, **prepPars)            
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)

        # Pull in any additional parameters from config (e.g., skyrange)
        redPars.update({'flatimage': flatFile, 'refimage': refFile})
        pars = merge_dicts(redPars, config[outfile].get('nsreduce', {}))
        gnirs.nsreduce(filelist('dp', sciFiles), **pars)

        # If nodding off slit, you need to select only the on-source frames!
        sciFiles = [f for f in sciFiles if abs(obslog[f]['Dec Offset']) < 20]
        gnirs.nscombine(filelist('rdp', sciFiles), output=outfile, **combPars)

        fitcooPars.update({'lamptransf': arcFile, 'sdisttransf': slitsFile,
                           'lxorder': 2})
        gnirs.nsfitcoords(outfile, **fitcooPars)
        transPars['reference'] = 'xtf'+telFile
        gnirs.nstransform('f'+outfile, **transPars)

        # Pull in any additional parameters from config (e.g., trace)
        pars = merge_dicts(extrPars, config[outfile].get('nsextract', {}))
        gnirs.nsextract('tf'+outfile, **pars)
        gnirs.nstelluric('xtf'+outfile, 'xtf'+telFile, **telPars)
        iraf.imdelete('f'+outfile+',tf'+outfile)
    iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

def reduceABBAScience(sci_dict):
    (prepPars, arithPars, fitcooPars, transPars, extrPars, redPars, combPars,
     nscombPars, telPars) = get_pars('f2prepare', 'gemarith', 'nsfitcoords', 'nstransform',
                          'nsextract', 'nsreduce', 'gemcombine', 'nscombine', 'nstelluric')
    redPars['fl_sky'] = 'yes'

    # Reopen configuation file for additional task parameters
    with open('mosTargets.yml', 'r') as yf:
        config = yaml.safe_load(yf)

    for outfile, file_dict in sci_dict.items():
        prepPars['bpm'] = file_dict['bpm']
        darkFile = file_dict['dark']
        flatFile = file_dict['flat']
        refFile = file_dict['reference']
        slitsFile = file_dict['slits']
        arcFile = file_dict['arc']
        telFile = file_dict['telluric']
        sciFiles = file_dict['input']

        for f in sciFiles:
            f2.f2prepare(f, **prepPars)            
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)

        # Pull in any additional parameters from config (e.g., skyrange)
        redPars.update({'flatimage': flatFile, 'refimage': refFile})
        pars = merge_dicts(redPars, config[outfile].get('nsreduce', {}))
        gnirs.nsreduce(filelist('dp', sciFiles), **pars)

        # Make A and B stacks and subtract
        gemtools.gemoffsetlist.unlearn()
        gemtools.gemoffsetlist(filelist('rdp', sciFiles),
                               reffile='rdp'+sciFiles[0], distance=1.,
                               age='INDEF',
                               targetlist='targetlist', offsetlist='offsetlist',
                               wcs_source='none')
        gemtools.gemcombine('@targetlist', 'Apos', **combPars)
        gemtools.gemcombine('@offsetlist', 'Bpos', **combPars)
        gemtools.gemarith('Apos', '-', 'Bpos', outfile, **arithPars)
        iraf.delete('targetlist,offsetlist')
        images.imutil.imgets('Bpos[0]', 'xoffset')
        xoffset = float(images.imutil.imgets.value)
        images.imutil.imgets('Bpos[0]', 'yoffset')
        yoffset = float(images.imutil.imgets.value)
        iraf.imdelete('Apos,Bpos')

        fitcooPars.update({'lamptransf': arcFile, 'sdisttransf': slitsFile,
                           'lxorder': 2})
        gnirs.nsfitcoords(outfile, **fitcooPars)
        transPars['reference'] = 'xtf'+telFile
        gnirs.nstransform('f'+outfile, **transPars)
        # Pull in any additional parameters from config (e.g., trace)
        pars = merge_dicts(extrPars, config[outfile].get('nsextract', {}))

        # Make inverted image and give it the correct offsets so
        # nscombine will shift it onto the positive image
        if abs(xoffset) < 20:
            negfile = 'neg_tf'+outfile
            gemtools.gemarith('tf'+outfile, '*', -1, negfile, **arithPars)
            gemtools.gemhedit(negfile+'[0]', 'XOFFSET', xoffset, '')
            gemtools.gemhedit(negfile+'[0]', 'YOFFSET', yoffset, '')
            nscombPars['boundary'] = 'constant'
            gnirs.nscombine('tf'+outfile+','+negfile, **nscombPars)
            gnirs.nsextract('tf'+outfile+'_comb', outspectra='xtf'+outfile,
                            **pars)
        else:
            gnirs.nsextract('tf'+outfile, **pars)
        gnirs.nstelluric('xtf'+outfile, 'xtf'+telFile, **telPars)
        iraf.imdelete('f'+outfile+',tf'+outfile)
    iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

#------------------ FLUX CALIBRATION: See Section 6.8 -----------------
def fluxCalibrate(sciFile, telFile, spectrum=None,
                  teff=None, jmag=None, hmag=None, kmag=None):

    # Wavelength (um), Flux density (W/m^2/um) for JHK (Hewett et al. 2006)
    zeropoints = ((1.25, 2.94e-9), (1.63, 1.14e-9), (2.20, 3.89e-10))

    # Need a spectrum, or a blackbody temp and a magnitude
    if spectrum is None and (teff is None or not (jmag or hmag or kmag)):
        print "Cannot produce model spectrum for "+telFile
        return

    gemtools.gemarith.unlearn()
    (contPars,) = get_pars('continuum')

    telluric = fits.open('xtf'+telFile+'.fits')
    texp_tel = telluric[0].header['EXPTIME']
    sci_ext = [hdu.header.get('EXTNAME', '') for hdu in telluric].index('SCI')
    tel_spec = telluric[sci_ext].data
    tel_head = telluric[sci_ext].header
    # Do wavelength in microns
    waves = 1e-4*(tel_head['CRVAL1']+tel_head['CD1_1']*(np.arange(len(tel_spec))
                                                        -tel_head['CRPIX1']+1))

    if spectrum:
        data = np.loadtxt(spectrum)  # Must be IRTF Spectral Library format
        model_spec = np.interp(waves, data[:,0], data[:,1])
    else:
        model_spec = 1.0/(waves**5 * (np.exp(14404./(waves*teff))-1))

    # Normalize spectrum according to magnitude
    for mag, (weff, f0) in zip([jmag,hmag,kmag], zeropoints):
        if mag:
            windex = np.argmin(abs(waves-weff))
            flux_spec = np.median(model_spec[max(windex-10,0):windex+10])
            model_spec *= 1e10*f0*10**(-0.4*mag) / flux_spec
            break

    # Telluric-correct the telluric standard (approximate)
    gemtools.gemarith('xtf'+sciFile, '/', 'axtf'+sciFile, 'tmp_atmos')
    atmos = fits.open('tmp_atmos.fits', mode='update')
    sensfunc = tel_spec / (atmos[1].data * model_spec)
    atmos[1].data = sensfunc
    atmos.flush()
    
    # Fit sensitivity function
    onedspec.continuum('tmp_atmos[SCI]', 'sensfunc', **contPars)

    science = fits.open('axtf'+sciFile+'.fits')
    texp_sci = science[0].header['EXPTIME']

    sensfunc = fits.open('sensfunc.fits')[0].data * 1e10 * (texp_sci/texp_tel)

    for hdu in science:
        if hdu.header.get('EXTNAME') == 'SCI':
            hdu.data /= sensfunc
        elif hdu.header.get('EXTNAME') == 'VAR':
            hdu.data /= sensfunc**2
    science.writeto('flux_'+sciFile+'.fits')

    iraf.imdelete('tmp_atmos,sensfunc')


########################################################################
def reduce_mos():
    global obslog
    iraf.imtype = 'fits'
    rawpath = get_pars('f2prepare')[0]['rawpath']
    # Get observations log and remove unwanted files
    obslog = ObsLog(os.path.join(rawpath, 'obslog.fits'))

    gnirs.nsheaders('f2')

    dark_dict = selectDarks(obslog)
    reduceDarks(dark_dict)

    ls_flat_dict, mos_flat_dict = selectFlats(obslog)
    reduceLSFlats(ls_flat_dict)
    # Here's how to remove entries in a reduction dictionary
    #del mos_flat_dict['flat_S20190809S0107_0111']  # too bright
    #del mos_flat_dict['flat_S20190809S0126']       # too bright
    #del mos_flat_dict['flat_S20190702S0693']       # not required
    #del mos_flat_dict['flat_S20190701S0100']       # not required
    check_cals(mos_flat_dict)
    reduceMOSFlats(mos_flat_dict)
    
    ls_arc_dict, mos_arc_dict = selectArcs(obslog)
    reduceArcs(ls_arc_dict)
    reduceArcs(mos_arc_dict)

    std_dict, sci_dict = selectTargets(obslog)
    reduceStandards(std_dict)
    reduceScience(sci_dict)
    # If you want to call nstelluric separately
    #(telPars,) = get_pars('nstelluric')
    #gnirs.nstelluric('xtfS5_K', 'xtfHD152602K', **telPars)

if __name__ == '__main__':
    reduce_mos()

