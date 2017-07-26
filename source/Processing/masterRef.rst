.. _master-ref:

===============================
Creating Master Reference Files
===============================

**Master calibration reference** (:term:`MasterCal`) files are derived from calibration or science observations, and are used to remove the various components of the instrument signature from the data. 
Calibration exposures may combined or characterized to create a calibration, so that it may be applied when science data are processed. 
Some other instrument calibrations (e.g., slit mask definition files for MOS mode) have already been created for you by Gemini scientists, or are distributed with the **gemini.f2** package software. 

This chapter summarizes how to create the reference files that will be needed for your data reduction. 

.. contents:: 
   :depth: 3

Preparation
-----------
Select Exposures
^^^^^^^^^^^^^^^^
It is important to create a summary of the calibration and science exposures to be processed, so that the appropriate **Dark MasterCals** can be created. 
Not surprisingly, the exposure times are generally different for: each science target, flats, arcs, and telluric standards. 

Prepare Files
^^^^^^^^^^^^^
In the code snippets below, it is assumed that the relevant task parameters and values have been stored in a python dictionary, and **f2prepare** has been run on all exposures to populate the headers with the necessary metadata. 

.. _f2-dark:

Darks
-----
*Dark* images show the spatially variable signal that accumulates during exposures. 
This additive signal originates from multiple sources, including thermal radiation from both the shutter and the read-out electronics. 
The structure depends upon the exposure time and the read-out mode---i.e., the number of :term:`CDS` for ``bright`` (1), ``medium`` (4), or ``faint`` (8). 

.. figure:: /_static/MCdark_60.*
   :width: 90 %

   **Dark MasterCal** in false-color with log intensity stretch for exposures of 60s duration and ``READMODE = bright``. Note the amplifier glow along the edges of the 32 sub-arrays of the detector. 
   Click image to enlarge. 

.. Note::
   Creating the **Dark MasterCals** is very simple: Combine the dark exposures with outlier rejection, optionally creating the variance [VAR] and data quality [DQ] extensions. Create a **Dark MasterCal** for each combination of the following attributes: 

      * Read-out mode (``bright | medium | faint``) 
      * Exposure time

   The dark correction is applied by simply subtracting the matching **Dark MasterCal** using either **gemarith**, or one of **nireduce** or **nsreduce** depending upon the observing configuration. 

It is best to co-add several (10 or more) dark exposures, obtained on the same night, so that the noise in the **Dark MasterCal** does not dominate in science exposures with low background.
The convention in the tutorials is to name the **Dark MasterCal** files ``MCdark_NNN`` where ``NNN`` is the exposure duration in seconds. 
The output **Dark MasterCal** file will have one FITS image extension, or 3 extensions if you elected to create the VAR and DQ arrays. 

.. _flat-field:

Flat-Fields
-----------
Constructing a **Flat-field MasterCal** is largely a matter of combining dark-corrected flat-field exposures, with appropriate scaling, outlier rejection, normalization, and conditioning. 
Flat-field exposures of either the twilight sky or (more commonly) the :term:`GCAL` flatfield lamp can correct for pixel-to-pixel variations in sensitivity; twilight flats may alternatively be used to correct the illumination pattern of the GCAL lamp. 
They are combined and normalized to create a **Flat-field MasterCal**. Separate flats must be created for each choice of: 

* illumination source: twilight sky or GCAL
* for imaging mode: filter
* for spectroscopic modes:

  * aperture (slit or mask)
  * disperser 

It is best to combine a few to several well exposed flat-field exposures (if available) to keep noise in the flat-field from dominating the uncertainties in well exposed portions of the science data. 
The process for creating **Flat-field MasterCals** is somewhat different for each observing mode: each will be described in turn. 
The output **Flat-field MasterCal** files will have one FITS image extension, or 3 extensions if you elected to create the VAR and DQ arrays. 

.. _imaging-flats:

Imaging Flats
^^^^^^^^^^^^^
Imaging flats that are created from a set of GCAL exposures: one sequence with the continuum lamp on, and one with the lamp off. 
The combined :term:`lamps-off` exposures contain a low-level thermal background (except in *K-* band) signature of the instrument and GCAL shutter. 
The GCAL shutter is quite bright in the *K-* band, even with the lamps off, 
so the combined *lamps-off* exposure suffices for the flat-field. 

Creating **Master Flat-field** reference files for imaging mode is mostly straightforward. 
However, it is *very important* to preview twilight flats (if any) to exclude any exposures that are not well exposed or contain bright stars. 

.. Note::
   Once exposures with common attributes have been identified, the process to create an imaging Flat-field MasterCal is: 
     1. Perform the **Dark** correction on each exposure.
     2. Combine each set of dark-corrected flat exposures with outlier rejection, scaling by the clipped mean of the images to account for variations in the flat-field illumination:

       a. For *Ks-* band simply combine the *lamps-off* exposures and continue with step 3. 
       b. Combine *lamps-on*, and separately *lamps-off*, exposures for all other bands
       c. Subtract the combined *lamps-off* from *lamps-on* image

     3. Condition the combined image: 

        a. Divide by the clipped mean of the combined image excluding bad pixels and outliers.
        b. Set a floor and ceiling on the pixel values. 

The **niri.niflat** task combines and conditions the exposures to form a **Flat-field MasterCal**; it also optionally creates a static **Bad Pixel Mask MasterCal** file. 
Be sure to review the flat-field for quality. 
The normalized flats will show a variety of features, including charge traps, dust on the dewar window, etc., as shown below. 

.. figure:: /_static/GCALimgFlats.*
   :width: 90 %

   Imaging **Flat-field MasterCals** for the *Y, J, H, Ks* filters. This false-color rendering has a linear intensity stretch and a range of :math:`\pm30` % (40% for Ks) about a mean of 1.0. 
   Click image to enlarge. 

.. _longslit-flats:

Long-Slit Flats
^^^^^^^^^^^^^^^
Spectral flats require an additional step in the normalization to remove the response to the illumination source (i.e., the "color term"). 
MOS flats must in addition be extracted for each slitlet. 

.. Note:: 

   Processing long-slit spectroscopic flat-field exposures is straightforward: 
     1. Perform **Dark** correction on each exposure.
     2. Extract the portion of the images that are illuminated by the slit.
     3. Combine the exposures, with outlier rejection, scaling by the clipped mean of the images to account for variations in the flat-field illumination. 
     4. Characterize the shape in the dispersion direction (i.e., the color term) by fitting a spline3 curve of relatively low order (3 or 4) to an average over the slit direction. It is safest to perform the fit interactively. 
     5. Divide each column of the combined flat by the polynomial. 
     6. Normalize the color-corrected flat-field image. 
     7. Condition the flat by setting a floor and ceiling on the pixel values. 

Use **gnirs.nsflat** to: perform the dark correction, combine the exposures, and normalize to form the **Flat-field MasterCal**. 
The normalized spectral flats will show a variety of features, including detector defects, dust on the dewar window, and narrow absorption features. 
A **Flatfield MasterCal** constructed in this way should have either 1 or 3 image extensions depending upon whether you chose to create the DQ and VAR extensions. 
The following plot shows example fits to the flat-field spectral response.

.. figure:: /_static/MCflats_resp.*
   :width: 100 %

   Fit to the response function of the JH (*left*) and HK (*right*) combined flat-field. A ``spline3`` function of order 20 and 26, respectively, was used to create these normalized **Flat-field MasterCals**.
   Click image to enlarge. 

.. _wave-cal:

Wavelength Calibration
----------------------
Exposures of the Ar lamp are used to determine the dispersion solution for spectroscopic modes. 
Arc lamp exposures should be dark and flat-field corrected (typically using **gnirs.nsreduce**). 
Use the **gnirs.nswavelength** task to determine the dispersion solution. 
An atlas of the Ar comparison arc is shown below for the 4-pix (0.72 arcsec) slit. 

.. Note:: 

   Processing long-slit spectroscopic arc exposures is simple: 
     1. Perform **Dark** correction on each exposure.
     2. Perform **Flat** correction on each exposure.
     3. Determine a dispersion solution for each exposure

.. figure:: /_static/Ar_IR.*
   :scale: 25 %

   Ar spectra in the *JH-* band (*upper*) and *HK-* band (*lower*) at full scale (*blue*), with portions magnified (*purple*) and offset vertically for clarity. More than 100 identifiable lines are marked (*red ticks*) along the wavelength axis. Some of the brighter or more isolated lines are labelled, which should suffice to bootstrap a wavelength solution. 
   Click image to enlarge. 

The fit to the dispersion solution should be done interactively (to reject very weak or blended lines) to ensure the quality of the solution. 
(If you are unfamiliar with the IRAF ``identify`` family of tasks, see the summary of :ref:`wav-identify` cursor commands.) 
Once a sufficient number of lines are identified (50---60 features with a good line list with the 0.72 arcsec slit), a ``legendre`` polynomial of order 4 or 5 should yield a solution with an RMS near 0.5 in the center of the slit. 

.. figure:: /_static/ArcFit5_JH.*
   :width: 100 %

   Non-linear portion of a low-order fit to the dispersion for a JH arc spectrum. A ``spline3`` function of order 5 should suffice to yield an RMS < 0.5.
   Click image to enlarge. 

The dispersion solution will be stored in a subdirectory of the working directory called ``./database``. 
The dispersion solution will be applied to science spectra by first running the **gnirs.nsfitcoords** task to determine the 2-D transformation; geometric rectification and wavelength linearization is performed with the **gnirs.nstransform** task. 

.. _telluric-corr:

Telluric Correction
-------------------
An approximate correction for telluric absorption can be derived from telluric standards (stars that have few, relatively weak features in the IR), provided they are obtained at similar airmass under similar observing conditions. 
The standard and science spectra must first be processed through flat-fielding, sky subtraction, combined, and extracted. 

The goal is to make a low-order fit to regions of the spectra where there is little telluric absorption, which when normalized contains the signature of the telluric absorption. 
The essence of the telluric correction encoded in the **gnirs.nstelluric** task is a modified version of the technique  developed by [VC]_: 

1. Fit a low-order function (typically a ``spline3`` function of order 6--8) to the portions of the continuum that are apparently not affected by telluric absorption for each of:

  * telluric standard
  * science target(s)

2. Use that function to normalize each continuum.

3. Determine the wavelength offset to the normalized spectrum that best matches the telluric absorption features the spectra.

4. Scale the intensity of the absorption features to match those in the science spectrum.

5. Divide the science spectrum by the shifted, scaled, normalized continuum. 

There are obvious flaws in this technique, including: 

* the weak signal in the cores of deep absorption features are not well or reliably corrected;

* it is not straightforward to determine accurately the edges of regions affected by telluric absorption;

* weak absorption in the telluric standard spectrum (such as from the Paschen H lines) will appear as emission features in the corrected science spectrum; 

* the fitting function is difficult to match to the actual continuum at all wavelengths; and 

* telluric absorption features at low resolution are in fact composed of large numbers of absorption features, some of which are deeply saturated, so that even a small change in the airmass can result in a complicated change to the shape of the absorption profile. 

Use the task **gnirs.nstelluric** to determine the telluric correction, which is illustrated below for the standard star HIP6546 (spectral type A2V) and the target J0126-5505. 
It is difficult to do this step because the **nstelluric** task does not provide a lot of flexibility in adjusting the fitting function to normalize the standard and target spectra.
It will therefore take some trial-and-error to derive an acceptable fit. 
It is *essential* to perform this correction interactively; use the ``s`` key to define continuum regions before attempting to fit. 

.. code-block:: python

   for g in qd:
       inFile = 'xtfJ0126-5505' + '_' + g
       telFile = 'xtfHIP6546' + '_' + g
       gnirs.nstelluric(inFile, telFile, **nstelluricPars)

The fit to the standard star continuum is shown below. 

.. figure:: /_static/Telluric_HK.*
   :width: 90 %

   Fit to the HK spectrum of the telluric standard HIP6546. Spectral regions (*solid horizontal bars*) have been selected to indicate regions that are not affected by telluric absorption. These regions have been fit by a low-order spline, where stellar absorption features have been rejected from the fit. 
   Click image to enlarge. 

The normalized spectra of the standard and the target are then cross-correlated to align the telluric feature wavelengths. 

.. figure:: /_static/FitHD_JH.* 
   :width: 90 %

   Plot of the ratio of the target spectrum to that of the telluric standard HD99216 for a small range of wavelength shifts (*upper*), and the normalized spectrum of the standard (*lower*). The final wavelength shift is selected by minimizing in the ratio spectrum the RMS deviation about unity. 

Finally, the telluric correction is applied by dividing the the original extracted target spectrum by the shifted, normalized telluric spectrum. 
The telluric correction using the star HD99216 yields a somewhat better result, although it is obviously far from perfect. 

.. figure:: /_static/J0126_comb.* 
   :width: 90 %

   Plot of the JH and HK spectra for the star J0126-5505. The deepest telluric absorption is not well corrected. 

It is not possible to correct well in the region :math:`1.34-1.5\mu\mathrm{m}`, nor in the region :math:`1.80-19.5\mu\mathrm{m}`, because the absorption is so strong and because it is variable on short timescales. 
In addition, absorption features (such as H_I) in the telluric standard show up as bogus emission features in the corrected target spectrum. 
This latter effect may be ameliorated by manually removing the absorption features in the standards prior to deriving the telluric correction. 

.. _flux-cal:

Flux Calibration
^^^^^^^^^^^^^^^^
Perhaps the most useful technique for correcting telluric absorption, and for removing the instrumental response function, is to use either a library of model atmospheres or a library of flux standards. 
The `IRTF Spectral Library <http://irtfweb.ifa.hawaii.edu/~spex/IRTF_Spectral_Library/>`_ is a collection of optical/NIR stellar spectra from 0.8--5.0 um. 
The procedure is the following: 

1. Identify the spectrum from the IR spectral library that most closely matches the standard used for your program's observations.

2. Re-grid the library spectrum to that of the extracted standard (download the :download:`regrid.py <../pyTools/regrid.py>` program for an example):

.. code-block:: bash

   python regrid.py atmFile stdFile outFile

3. Compute ratio of the standard to the re-gridded library spectrum. 

4. Fit the ratio with a low-order polynomial, rejecting all the spectral features and residual telluric features. This is the approximate sensitivity function.

.. figure:: /_static/FV5_fit.* 
   :width: 90 %

   Residual of the fit to the ratio of an FV5 library standard to the standard star HD218804. Note the rejection or deletion of stellar features and residual telluric absorption. 



5. Multiply the extracted spectra for the standard and the target by the sensitivity function. 

6. Perform the telluric correction on the calibrated spectra.


