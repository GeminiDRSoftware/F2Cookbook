#!/usr/bin/env python
# RAShaw.astro@gmail.com 2017-Jan-22
import os, sys
import argparse
from astropy.io import fits
from astropy.table import Table

# Mapping of data header keywords to DB field names and DB types
KW_MAP = [('OBJECT',   'Object'),
          ('FILTER',   'Filter'),
          ('GRISM',    'Disperser'),
          ('OBSID',    'ObsID'),
          ('EXPTIME',  'Texp'),
          ('DATE-OBS', 'Date'),
          ('TIME-OBS', 'Time'),
          ('RA',       'RA'),
          ('DEC',      'Dec'),
          ('RAOFFSET', 'RA Offset'),
          ('DECOFFSE', 'Dec Offset'),
          ('OBSTYPE',  'ObsType'),
          ('OBSCLASS', 'ObsClass'),
          ('READMODE', 'Read Mode'),
          ('LNRS',     'Reads'),
          ('COADDS',   'Coadds'),
          ('MASKNAME', 'Mask'),
          ('MASKTYPE', 'MaskType'),
          ('DECKER',   'Decker'),
          ('GCALSHUT', 'GCAL Shutter'),
          ('PA',       'PA'),
          ('GRWLEN',   'Wavelength'),
          ('AIRMASS',  'Airmass'),
]

def obsLog(args):
    """Construct an observation log from header keywords in FITS files."""

    descr_text = 'Construct an observation log from a directory of data files'
    parser = argparse.ArgumentParser(description=descr_text)
    parser.add_argument('dbFile', type=str, help='Name of file to create')
    args = parser.parse_args()

    colnames = ['File'] + [kw[1] for kw in KW_MAP]
    table_data = dict([(c, []) for c in colnames])
    fileList = [f for f in os.listdir('.') if f.startswith('S')
                and f.endswith('.fits') and len(f)==19]
    for fname in fileList:
        hd0 = fits.open(fname)[0].header
        for kw, c in KW_MAP:
            table_data[c].append(hd0.get(kw, ''))
        table_data['File'].append(fname.replace('./','').replace('.fits',''))

    # Tweak some data
    table_data['Filter'] = [f.split('_')[0] for f in table_data['Filter']]
    table_data['Disperser'] = [f.split('_')[0] for f in table_data['Disperser']]

    t = Table(names=colnames, data=[table_data[c] for c in colnames])
    t['use_me'] = [True] * len(t)

    if os.path.exists(args.dbFile):
        os.remove(args.dbFile)
    t.write(args.dbFile, format='fits')

if __name__ == '__main__':
    obsLog(sys.argv)
