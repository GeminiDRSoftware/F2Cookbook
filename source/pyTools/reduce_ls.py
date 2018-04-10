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
            date1, date2 = qd['Date'].split(':')
        except ValueError:  # Only one date
            good = self.table['Date'] == qd['Date']
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
    with open('lsTaskPars.yml', 'r') as yf:
        pars = yaml.load(yf)
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
#----------------------------------------------------------------------
#---- DON'T EDIT ABOVE THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ----
#----------------------------------------------------------------------

#----------------------- DARKS: See Section 4.3 -----------------------
def selectDarks(obslog):
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

#----------------------- FLATS: See Section 5.4 -----------------------
def selectFlats(obslog):
    flat_dict = {}
    qd = {'ObsType': 'FLAT'}
    params = ('Texp', 'Disperser')
    flatConfigs = unique(obslog.query(qd)[params])
    for config in flatConfigs:
        t, grism = config
        config_dict = dict(zip(params, config))
        flatFiles = obslog.file_query(merge_dicts(qd, config_dict))
        outfile = 'MCflat_'+grism
        flat_dict[outfile] = {'dark': 'MCdark_'+str(int(t)),
                              'bpm': 'MCbpm_'+grism+'.pl',
                              'input': flatFiles}
    return flat_dict

def reduceFlats(flat_dict):
    prepPars, arithPars, cutPars, flatPars = get_pars('f2prepare', 'gemarith',
                                                      'f2cut', 'nsflat')
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

#------------------------ ARCS: See Section 5.5 -----------------------
def selectArcs(obslog):
    arc_dict = {}
    arcFiles = obslog.file_query({'ObsType': 'ARC'})
    params = ('Texp', 'Disperser')
    # Do not stack arcs; reduce each separately
    for f in arcFiles:
        t, grism = obslog[f][params]
        outfile = 'arc_'+f
        arc_dict[outfile] = {'dark': 'MCdark_'+str(int(t)),
                             'flat': 'MCflat_'+grism,
                             'bpm': 'MCbpm_'+grism,
                             'input': [f]}
    return arc_dict

def reduceArcs(arc_dict):
    prepPars, arithPars, redPars, wavePars = get_pars('f2prepare', 'gemarith',
                                                    'nsreduce', 'nswavelength')
    for outfile, file_dict in arc_dict.items():
        darkFile = file_dict['dark']
        prepPars['bpm'] = file_dict['bpm']
        flatFile = file_dict['flat']
        arcFiles = file_dict['input']
        for f in arcFiles:
            f2.f2prepare(f, **prepPars)
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)
        # Flatfields not required for arcs
        if flatFile:
            redPars.update({'fl_flat': 'yes', 'flatimage': flatFile})
        else:
            redPars['fl_flat'] = 'no'
        gnirs.nsreduce(filelist('dp', arcFiles), **redPars)
        if len(arcFiles) > 1:
            gemcombine(filelist('rdp', arcFiles), 'tmp_'+outfile, **arithPars)
            gnirs.nswavelength('tmp_'+outfile, outspectra=outfile, **wavePars)
        else:
            gnirs.nswavelength('rdp'+arcFiles[0], outspectra=outfile,
                               **wavePars)
    iraf.imdelete('*pS*.fits,dpS*.fits')

#---------------------- TARGETS: See Section 5.6 ----------------------
def selectTargets(obslog):
    # Configuation file: see Section 5.2.1
    with open('lsTargets.yml', 'r') as yf:
        config = yaml.load(yf)

    std_dict = {}
    sci_dict = {}
    qd = {'ObsType': 'OBJECT'}
    for outfile, pars in config.items():
        infiles = obslog.file_query(merge_dicts(qd, pars))
        t, grism = obslog[infiles[0]]['Texp', 'Disperser']
        file_dict = {'dark': pars.get('dark', 'MCdark_'+str(int(t))),
                     'bpm': pars.get('bpm', 'MCbpm_'+grism),
                     'flat': pars.get('flat', 'MCflat_'+grism),
                     'arc': pars['arc'],  # Must be specified
                     'input': infiles}
        try:
            telFile = pars['telluric']
        except KeyError:  # No telluric => treat as a standard
            std_dict[outfile] = file_dict
        else:
            sci_dict[outfile] = merge_dicts(file_dict, {'telluric': telFile})
    return std_dict, sci_dict

def reduceStandards(std_dict):
    (prepPars, arithPars, fitcooPars, transPars, extrPars, redPars,
     combPars) = get_pars('f2prepare', 'gemarith', 'nsfitcoords', 
                          'nstransform', 'nsextract', 'nsreduce', 'nscombine')
    redPars['fl_sky'] = 'yes'
    combPars['fl_cross'] = 'yes'

    # Reopen configuation file for additional task parameters
    with open('lsTargets.yml', 'r') as yf:
        config = yaml.load(yf)

    for outfile, file_dict in std_dict.items():
        darkFile = file_dict['dark']
        prepPars['bpm'] = file_dict['bpm']
        flatFile = file_dict['flat']
        arcFile = file_dict['arc']
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

#------------------ SCIENCE TARGETS: See Section 5.7 ------------------
def reduceScience(sci_dict):
    (prepPars, arithPars, fitcooPars, transPars, extrPars, redPars, combPars,
     telPars) = get_pars('f2prepare', 'gemarith', 'nsfitcoords', 'nstransform',
                          'nsextract', 'nsreduce', 'nscombine', 'nstelluric')
    redPars['fl_sky'] = 'yes'

    # Reopen configuation file for additional task parameters
    with open('lsTargets.yml', 'r') as yf:
        config = yaml.load(yf)

    for outfile, file_dict in sci_dict.items():
        darkFile = file_dict['dark']
        prepPars['bpm'] = file_dict['bpm']
        flatFile = file_dict['flat']
        arcFile = file_dict['arc']
        telFile = file_dict['telluric']
        sciFiles = file_dict['input']
        for f in sciFiles:
            f2.f2prepare(f, **prepPars)            
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)

        # Pull in any additional parameters from config (e.g., skyrange)
        pars = merge_dicts(redPars, config[outfile].get('nsreduce', {}))
        gnirs.nsreduce(filelist('dp', sciFiles), flatimage=flatFile, **pars)
        gnirs.nscombine(filelist('rdp', sciFiles), output=outfile, **combPars)

        #gnirs.nsfitcoords(outfile, lamptransf=arcFile, **nsfitcrdPars)
        apply_fitcoords(outfile, telFile, fitcooPars['database'])
        gnirs.nstransform('f'+outfile, **transPars)

        # Pull in any additional parameters from config (e.g., trace)
        pars = merge_dicts(extrPars, config[outfile].get('nsextract', {}))
        gnirs.nsextract('tf'+outfile, **pars)
        gnirs.nstelluric('xtf'+outfile, 'xtf'+telFile, **telPars)
        iraf.imdelete('f'+outfile+',tf'+outfile)
    iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

#------------------ FLUX CALIBRATION: See Section 5.8 -----------------
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
def reduce_ls():
    iraf.imtype = 'fits'
    rawpath = get_pars('f2prepare')[0]['rawpath']
    # Get observations log and remove unwanted files
    obslog = ObsLog(os.path.join(rawpath, 'obslog.fits'))

    gnirs.nsheaders('f2')

    #dark_dict = nightlyDarks(obslog)
    dark_dict = selectDarks(obslog)
    reduceDarks(dark_dict)
    flat_dict = selectFlats(obslog)
    reduceFlats(flat_dict)
    arc_dict = selectArcs(obslog)
    reduceArcs(arc_dict)
    std_dict, sci_dict = selectTargets(obslog)
    reduceStandards(std_dict)
    sci_dict = {k:v for k,v in sci_dict.items() if k=='epoch2'}
    reduceScience(sci_dict)

    for outfile in sci_dict.keys():
        fluxCalibrate(outfile, 'HD30526', 'F7V_HD126660.txt', hmag=8.537)

if __name__ == '__main__':
    reduce_ls()

