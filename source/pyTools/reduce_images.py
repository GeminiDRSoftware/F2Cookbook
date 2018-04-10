#!/usr/bin/env python
import os, yaml
import numpy as np
from pyraf import iraf
from pyraf.iraf import gemini
from pyraf.iraf import gemtools, niri, f2, gnirs
from astropy.table import Table, Row, unique
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
    # Merge two dicts; possibly prevent new keys being added
    d = dict1.copy()
    d.update({k: v for k, v in dict2.items() if (k in dict1 or allow_new)})
    return d

def get_pars(*tasks):
    # Unlearn tasks and read parameters from yaml file, returning dicts
    with open('imgTaskPars.yml', 'r') as yf:
        pars = yaml.load(yf)
    pkg_dict = {'f2': f2, 'ni': niri, 'ge': gemtools}
    for task in tasks:
        pkg = pkg_dict.get(task[:2], iraf)
        getattr(getattr(pkg, task), 'unlearn')()
    return [pars[task] for task in tasks]

#----------------------------------------------------------------------
#---- DON'T EDIT ABOVE THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ----
#----------------------------------------------------------------------

#----------------------- DARKS: See Section 4.3 -----------------------
def nightlyDarks(obslog):
    dark_dict = {}
    qd = {'ObsType': 'DARK'}
    configs = unique(obslog.query(qd)['Date', 'Texp'])
    for (date, t) in configs:
        darkFiles = obslog.file_query(merge_dicts(qd, {'Date': date,
                                                       'Texp': t}))
        outfile = 'MCdark_'+date.replace('-','')+'_'+str(int(t))
        dark_dict[outfile] = {'input': darkFiles}
    return dark_dict

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
            gemtools.gemcombine(filelist('p', darkFiles), outfile,
                                **combPars)
        else:
            iraf.imrename('p'+darkFiles[0], outfile)
    iraf.imdelete('pS*.fits')

#----------------------- FLATS: See Section 4.4 -----------------------
def selectGcalFlats(obslog):
    # First we need to select the shortest darks
    qd = {'ObsType': 'DARK'}
    tshort = min(obslog.query(qd)['Texp'])
    shortDarks = obslog.file_query(merge_dicts(qd, {'Texp': tshort}))

    flat_dict = {}
    qd = {'ObsType': 'FLAT'}
    params = ('Filter', 'Texp')
    flatConfigs = unique(obslog.query(qd)[params])
    for config in flatConfigs:
        filt, t = config
        config_dict = dict(zip(params, config))
        # K/Ks-band flats are made differently
        if filt.startswith('K'):
            lampsOn = obslog.file_query(merge_dicts(qd, config_dict))
            lampsOff = obslog.file_query({'ObsType': 'DARK', 'Texp': t})
        else:
            config_dict['GCAL Shutter'] = 'OPEN'
            lampsOn = obslog.file_query(merge_dicts(qd, config_dict))
            config_dict['GCAL Shutter'] = 'CLOSED'
            lampsOff = obslog.file_query(merge_dicts(qd, config_dict))
        outfile = 'MCflat_'+filt
        flat_dict[outfile] = {'bpm': 'MCbpm_'+filt+'.pl',
                              'lampsOn': lampsOn, 'lampsOff': lampsOff,
                              'shortDarks': shortDarks}
    return flat_dict

def selectSkyFlats(obslog):
    # First we need to select the shortest darks
    qd = {'ObsType': 'DARK'}
    tshort = min(obslog.query(qd)['Texp'])
    shortDarks = obslog.file_query(merge_dicts(qd, {'Texp': tshort}))

    flat_dict = {}
    qd = {'Object': 'Twilight'}
    params = ('Filter', 'Texp')
    flatConfigs = unique(obslog.query(qd)[params])
    for config in flatConfigs:
        filt, t = config
        config_dict = dict(zip(params, config))
        lampsOn = obslog.file_query(merge_dicts(qd, config_dict))
        lampsOff = obslog.file_query({'ObsType': 'DARK', 'Texp': t})
        outfile = 'MCflat_'+filt
        flat_dict[outfile] = {'bpm': 'MCbpm_'+filt+'.pl',
                              'lampsOn': lampsOn, 'lampsOff': lampsOff,
                              'shortDarks': shortDarks}
    return flat_dict

def reduceFlats(flat_dict, gcal=True):
    prepPars, flatPars = get_pars('f2prepare', 'niflat')
    prepPars['fl_nonlinear'] = 'no'        # Fudge to fix (slightly)
    flatPars['key_nonlinear'] = 'SATURATI' # over-exposed flats
    if not gcal:
        # Set parameters for sky flats
        flatPars.update({'fl_rmstars': 'yes', 'scale': 'median'})
    for outfile, file_dict in flat_dict.items():
        bpmFile = file_dict['bpm']
        lampsOn = file_dict['lampsOn']
        lampsOff = file_dict['lampsOff']
        shortDarks = file_dict['shortDarks']
        # Don't waste time trying to re-prepare files
        for f in shortDarks+lampsOn+lampsOff:
            if not os.path.exists('p'+f+'.fits'):
                f2.f2prepare(f, **prepPars)
        flatPars.update({'darks': filelist('p', shortDarks),
                           'lampsoff': filelist('p', lampsOff),
                           'flatfile': outfile, 'bpmfile': bpmFile})
        niri.niflat(filelist('p', lampsOn), **flatPars)
    iraf.imdelete('pS*.fits')

#---------------------- TARGETS: See Section 4.5 ----------------------
def selectTargets(obslog):
    # Configuation file: see Section 4.2.1
    with open('imgTargets.yml', 'r') as yf:
        targets = yaml.load(yf)

    sci_dict = {}
    qd = {'ObsClass': 'science'}
    for outfile, pars in targets.items():
        sciFiles = obslog.file_query(merge_dicts(qd, pars))
        t, filt = obslog[sciFiles[0]]['Texp', 'Filter']
        file_dict = {'dark': pars.get('dark', 'MCdark_'+str(int(t))),
                     'bpm': pars.get('bpm', 'MCbpm_'+filt),
                     'flat': pars.get('flat', 'MCflat_'+filt),
                     'sky': pars.get('sky', 'self')}
        try:
            groupsize = pars['groupsize']
        except:
            sci_dict[outfile] = merge_dicts(file_dict, {'input': sciFiles})
        else:
            index = 1
            while len(sciFiles) > 0:
                sci_dict['{}_{:03d}'.format(outfile, index)] = merge_dicts(
                    file_dict, {'input': sciFiles[:groupsize]})
                del sciFiles[:groupsize]
                index += 1

    # Create list of sky frames used in reduction
    sky_list = [v['sky'] for v in sci_dict.values()]
    # Make a reduction dict of bespoke skies
    sky_dict = {k: v for k, v in sci_dict.items() if k in sky_list}
    # And then remove these from the science reduction dict
    sci_dict = {k: v for k, v in sci_dict.items() if k not in sky_list}
    return sky_dict, sci_dict

def reduceSkies(sky_dict):
    prepPars, arithPars, skyPars, redPars = get_pars('f2prepare', 'gemarith',
                                                     'nisky', 'nireduce')
    for outfile, file_dict in sky_dict.items():
        darkFile = file_dict['dark']
        prepPars['bpm'] = file_dict['bpm']
        flatFile = file_dict['flat']
        skyFiles = file_dict['input']
        for f in skyFiles:
            f2.f2prepare(f, **prepPars)
            gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)
        # Make (non-flatfielded) sky
        skyPars['outimage'] = 'nf_'+outfile
        niri.nisky(filelist('dp', skyFiles), **skyPars)
        # Flatfield
        redPars.update({'flatimage': flatFile, 'outimage': outfile})
        niri.nireduce('nf_'+outfile, **redPars)
        iraf.imdelete('nf_'+outfile)
    iraf.imdelete('pS*.fits')

def reduceScience(sci_dict):
    prepPars, arithPars, redPars, coaddPars = get_pars('f2prepare', 'gemarith',
                                                       'nireduce', 'imcoadd')
    for outfile, file_dict in sci_dict.items():
        darkFile = file_dict['dark']
        bpmFile = file_dict['bpm']
        flatFile = file_dict['flat']
        skyFile = file_dict['sky']
        sciFiles = file_dict['input']
        prepPars['bpm'] = bpmFile
        if skyFile == 'self':
            # Make the sky (also leaves dark-subtracted files on disk)
            skyFile = outfile+'_sky'
            reduceSkies({skyFile: file_dict})
        else:
            for f in skyFiles:
                f2.f2prepare(f, **prepPars)
                gemtools.gemarith('p'+f, '-', darkFile, 'dp'+f, **arithPars)

        # Flatfield
        redPars.update({'outprefix': 'f', 'fl_sky': 'no',
                        'flatimage': flatFile})
        niri.nireduce(filelist('dp', sciFiles), **redPars)
        imcoadd_infiles = filelist('fdp', sciFiles)

        # Sky-subtract if required
        if skyFile != 'none':
            redPars.update({'outprefix': 'r', 'fl_flat': 'no',
                            'fl_sky': 'yes', 'skyimage': skyFile})
            niri.nireduce(filelist('fdp', sciFiles), **redPars)
            imcoadd_infiles = filelist('rfdp', sciFiles)

        coaddPars.update({'badpixfile': bpmFile, 'outimage': outfile})
        gemtools.imcoadd(imcoadd_infiles, **coaddPars)
    iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits,rfdpS*.fits,fdpS*.fits')

def coaddScience(sci_dict):
    (coaddPars,) = get_pars('imcoadd')
    for outfile, file_dict in sci_dict.items():
        sciFiles = file_dict['input']
        prefix = 'fdp' if file_dict['sky'] == 'none' else 'rfdp'
        coaddPars.update({'badpixfile': file_dict['bpm'],
                          'outimage': outfile})
        gemtools.imcoadd(filelist(prefix, sciFiles), **coaddPars)
                           

########################################################################
def reduce_images():
    iraf.imtype = 'fits'
    rawpath = get_pars('f2prepare')[0]['rawpath']
    # Get observations log and remove unwanted files
    obslog = ObsLog(os.path.join(rawpath, 'obslog.fits'))

    gnirs.nsheaders('f2')

    dark_dict = selectDarks(obslog)
    reduceDarks(dark_dict)
    flat_dict = selectGcalFlats(obslog)
    reduceFlats(flat_dict)
    flat_dict = selectSkyFlats(obslog)
    reduceFlats(flat_dict, gcal=False)
    sky_dict, sci_dict = selectTargets(obslog)
    reduceSkies(sky_dict)
    reduceScience(sci_dict)


if __name__ == '__main__':
    reduce_images()
