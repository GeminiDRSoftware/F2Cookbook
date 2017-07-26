#!/usr/bin/env python
# shaw@stsci.edu: 2017-Jul-20

import argparse
from astropy.io import fits
import numpy as np
import scipy.interpolate as sp1d
import sys

def regrid(args):
    ''' Resample a model atmosphere spectrum to the dispersion of a telluric 
        standard spectrum, and write the  results to a FITS file.
    '''

    descr_text = 'Resample a model atmosphere spectrum'
    parser = argparse.ArgumentParser(description=descr_text)
    parser.add_argument('atmFile', type=str, help='Name of model atm file')
    parser.add_argument('stdFile', type=str, help='Name of telluric std file')
    parser.add_argument('outFile', type=str, help='Name of output file')
    args = parser.parse_args()

    # Telluric standard stores spectrum in the first image extension.
    # We only need the dispersion coefficients. 
    with fits.open(args.stdFile) as spHdu:
        eH = spHdu[1].header
        npts   = eH['NAXIS1']
        crpix1 = eH['CRPIX1']
        crval1 = eH['CRVAL1']
        cdelt1 = eH['CD1_1']
        we = crval1 + (npts - 1)*cdelt1

    # Wavelength bins for output spectrum
    x = np.arange(crval1, we, cdelt1)
    print npts, len(x)

    # Open the irregularly sampled model atmosphere spectrum, in PHDU
    # Convert flux density units from (um, W/m^2/s) to (Ang,erg/cm^2/Ang)
    with fits.open(args.atmFile) as hdu:
        wave = hdu[0].data[0] * 1.e4
        flux = hdu[0].data[1] * 10.
        print wave[0], flux[0]

        # Copy some metadata from model atm spectrum
        pH = hdu[0].header
        object = pH['OBJECT']
        spType = pH['SPTYPE']

    # Linear interpolation of atm spectrum (splines fail)
    f = sp1d.interp1d(wave, flux, kind='linear')
    y = f(x)

    # Create a new FITS spectrum
    pHDU = fits.PrimaryHDU()
    imgHdu = fits.ImageHDU(y, header=None, name='SCI')
    imgHdu.header['CRPIX1'] = crpix1
    imgHdu.header['CRVAL1'] = crval1
    imgHdu.header['CD1_1'] = cdelt1
    imgHdu.header['BUNIT'] = 'erg/cm^2/s/Ang'
    imgHdu.header['WAT0_001'] = 'system=equispec'
    imgHdu.header['WAT1_001'] = 'wtype=linear label=Wavelength units=angstroms'
    # Identification info
    imgHdu.header['OBJECT'] = object
    imgHdu.header['SPTYPE'] = spType
    hduList = fits.HDUList([pHDU,imgHdu])
    hduList.writeto(args.outFile)

if __name__ == '__main__':
    regrid(sys.argv)
