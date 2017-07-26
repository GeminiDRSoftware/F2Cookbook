.. _conceptual-overview:

===================================
Conceptual Overview of the Workflow
===================================
The data reduction software in the **gemini** package can be used in a variety of ways to reduce your science data. 
That generality can get in the way of understanding the process at a conceptual level, separately from the mechanics of invoking the tasks. 
This chapter offers a tour of the *what* to do and *why* it is done in a particular way, rather than the *how* something is done. 

The path through data reduction is somewhat different for each observing configuration, though there is some commonality, particularly in creating **MasterCal** reference files. 

.. contents:: 
   :depth: 3

What the GEMINI Package Offers
------------------------------
Parameters and Characterizations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Many of the instrument parameters and data characterizations necessary for data reduction have been provided in the **f2** package. 
The parameters related to these characterizations are stored in data files in the header metadata, the ``f2$data/`` or ``f2f$cal/`` package directories, or within IRAF package directories, and are accessed by the data processing tasks. 
They include: 

* Sections of the detector that are illuminated for choices of aperture, filter, and disperser 
* For the detector:

  - for selections of the number of :term:`CDS` in the readout:

    - readnoise and gain
    - full-well depth and upper limit to the linear counts regime

* Approximate dispersion coefficients for each grism
* Filter transmission curves

Many of these values can be overridden with task parameters or custom reference files. 

A Uniform Model of the Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^
F2 data include concomitant data, and the **f2** and **niri** packages attempt to hide the associated complexity from the user. 
There are 3 or 4 dimensions of complexity, depending upon the observing configuration, that are represented in :term:`FITS` file names or :term:`MEF` content: 

* concomitant data that describe the science arrays at the pixel level, 
* multiple spectral slitlets (i.e., MOS slitlets), and 
* spectroscopic slit definitions stored in a FITS table extension. 

This complexity is not an elegant match to FITS or IRAF, which partially explains why it is difficult to use traditional software tools to reduce F2 data, or to interleave these tools within the **gemini** package reduction workflow. 
Moreover, the `FITS standard <http://fits.gsfc.nasa.gov/fits_standard.html>`_ (and its support within IRAF) has limited ability to represent the semantic content and organization of the various data objects, apart from a linear sequence of extensions in a single file. 
See :ref:`data-packaging` for an overview of MEF file content and organization. 

Concomitant Data
::::::::::::::::
F2 data include a number of pieces, including concomitant data. 
Some of these are created during data reduction. 
They include the following: 

* Science array, one ``SCI`` extension per amplifier
* Variance array, ``VAR`` extension (optional)
* Data quality array, ``DQ`` extension (optional)
* Processing metadata, stored in FITS HDU keywords
* Processing logs, as separate ASCII files

where:

* **Raw Images** are images consisting of data from the sensor. Recall that the spectral orders span the sensors. 

* **Bad Pixel Masks** are arrays of bit-encoded values for each pixel of the science array indicating the data quality conditions that apply, where zero indicates no DQ conditions. 

* **Variance planes** are computed as the sum in quadrature of the variance from each processing stage, which for the most part is based on Poisson statistics. 

The variance of the reduced science array is computed as: 

.. math:: 

   \mathrm{Var}(S_c) = (R/G)^{2} + \max(S_r-D,0.0)/G + \mathrm{Var}(D)) + \frac{\mathrm{Var}(F)\times(S_r-B)^{2}}{F^{4}}

where Var(X) is the variance of the array X, and: 

* `D` is the **Dark MasterCal**
* `F` is the (normalized) **Flat-field MasterCal**
* `G` is the scalar gain in *e*/ADU
* `R` is the scalar read noise in electrons
* :math:`S_c` is the calibrated science array
* :math:`S_r` is the raw science array

.. note::

   The expression above for the variance does *not* include cross-terms to account for correlated noise between neighboring pixels, which would be appropriate once the data have been resampled. 

.. _file-nomenclature: 

File Nomenclature
:::::::::::::::::
It is usually simplest during data reduction to retain the filenames of raw exposures as provided by the Gemini Observatory Archive, and to allow **f2** and **gnirs** processing tasks to take care of naming output files. 
The raw filename template is the following: 

   <*site*><*yyyy*><*mm*><*dd*> ``S`` <*seq*> ``.fits``

where ``S`` and ``.fits`` are literals, and: 

* <*site*> is one of [``N | S``] for GMOS-N or GMOS-S
* <*yyyy*><*mm*><*dd*> is the year, numerical month, and UT day of observation
* <*seq*> is a running sequence number within a UT day

The Gemini convention for naming output files is to prepend one or more characters to the input filename. 
This occurs for each intermediate stage of data reduction processing, and is summarized in the table below. 
Unfortunately the characters used are not entirely unique, so the meaning of a few of them must be derived from context. 

.. csv-table:: **Processing Prefixes**
   :header: "Prefix", "Applies to:", "Description"
   :widths: 8, 15, 50

   *a*, Spec, telluric correction applied
   *c*, Spec, Flux calibrated
   *p*, Img+Spec, File "f2prepare-d" for reduction
   *r*, Spec, spectra reduced with nsreduce
   *r*, Img, images reduced with nireduce
   *t*, Spec, wavelength-calibrated; rectilinear spectral image
   *x*, Spec, 1-D extracted spectra 

Note that *Spec* is used above to indicate applicability to all spectral modes: LS, and :term:`MOS`.

Process Integrity
^^^^^^^^^^^^^^^^^
Some **gnirs** tasks are meta-tasks, in that they call other **gemini** or IRAF tasks to perform most stages of data processing. 
In some cases, particularly for IFU reductions, a meta-task performs part of the processing, then one or more other tasks perform specialized steps, then the meta-task is resumed for the remainder of the processing. 
In this sense, these meta-tasks are re-entrant. 
This flexibility means that **niri** tasks must do a great deal of integrity checking on the input data, including: 

* Input files are all accessible, and no output file will be overwritten,
* The science data and **MasterCals** match in readout mode (i.e., the number of correlated double samples), and (if relevant) filter,
* Header metadata indicate that preceding processing steps have been performed,
* The number of file extensions is correct, and
* The input image dimensions are correct/consistent with **MasterCal** files

If any of the preconditions are not met, processing will halt (probably in a very inconvenient place). 
The various processing steps are recorded in the image header; see :ref:`dr-keywords`. 

All processing steps (and many of the input parameters) are written to the processing log. 
Error messages, if any, are also written to the log. 
*Check the log if the processing goes awry.* 

F2 Data Reduction Overview
--------------------------
Data processing for all F2 configurations begins with preparing all relevant Master Calibration reference (:term:`MasterCal`) files. 
See ``master-ref`` for details. 
The **Dark MasterCal** is applied in raw pixel space, and is prepared in exactly the same way for all configurations. 

Steps Common to All Workflows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Whether for imaging or spectroscopic data reduction, the following steps are performed: 

0. **Data Preparation.** Raw data from the observing environment lack certain important metadata in the headers that are essential for data reduction. and for documenting the provenance of the reduced data products. 
This initial step inserts these metadata, and for MOS mode appends the appropriate Mask Definition File (:term:`MDF`) as a table extension. 

1. **Dark Correction.** The first step in reducing all F2 data is to subtract the dark level---i.e., the counts that accumulate even in the absence of astrophysical signal, from the pixel array. 
This signal originates from thermal emission within the instrument, and from the heat generated by the read-out amplifiers which varies depending upon the number of :term:`CDS` reads and the exposure duration. 

.. caution:: 

   It is *essential* for the exposure duration *and* read-out mode of the dark exposures that comprise the **Dark MasterCal** match that of the exposures being processed. 

It is common in IR data reduction to omit an explicit dark subtraction when sky subraction is performed prior to flat-fielding *if* the sky emission array has *not* had the dark correction applied. 
This is the default order of operations for the **nsreduce** task, for instance. 
However the F2 dithering or nodding operational modes make an explicit dark subtraction the more sensible choice in these cases. 

2. **Flat-field Correction.** The **Flat-field MasterCals** for each filter are usually created from GCAL flats, and are normalized to a mean of 1.0 over all non-flagged pixels before being divided out of the science frames. 

The order and method for most other steps depends upon the observing configuration, as described in the following subsections. 

.. _image-workflow:

Imaging Workflow
^^^^^^^^^^^^^^^^
Reduction of images is simplest of all the operating modes. 
A diagram of the nominal workflow is shown below: 

.. figure:: /_static/Workflow_img.*
   :width: 90%

   **Fig. 1.** Nominal order of processing for F2 imaging data. Successive columns show the conceptual operation, the task for accomplishing the step, and the type of science or calibration data to which the processing step applies. Color background in each column shows the steps that apply (*shaded*) or the output **MasterCal** product (*dark shaded*) named in the column header; steps that are optional or that may not always apply are *light grey*. 

Reduction Synopsis
::::::::::::::::::
Continuing with the basic image reduction steps, we have: 

3. **Sky Subtraction.** The sky is subtracted either pair-wise from successive dithered exposures, or by . 

Beyond the Basics
:::::::::::::::::

* It may be a good idea to refine the :term:`WCS` if your goal is to derive highly accurate coordinates or offsets. 
* Use **gemtools.imcoadd** to combine separate, overlapping exposures in the same filter to enable deep source detection or to perform photometry on very extended sources. 
  But be aware that the output may not be scientifically optimal, as this task creates the *intersection*, not the *union*, of the contributing images to the footprint of the first image in the list of files to co-add.
  Also, this task does *not* match PSFs *nor* account for varying sky brightness. 

* Measuring source brightnesses and establishing a photometric zero-point may be accomplished with widely available photometry packages, such as `SExtractor <http://www.astromatic.net/software/sextractor>`_. 

Proceed to :ref:`f2-proc-dith-img` or `f2-proc-offset-img`.

.. _ls-workflow:

Long-slit Workflow
^^^^^^^^^^^^^^^^^^
The workflow for F2 long-slit spectroscopy is illustrated below. 
Note that the order of the operations depends somewhat upon how the sky is subtracted: if sky is obtained from an offset position (rather than nodding along the slit), then the 2-D spectrograms be co-added before the sky is subtracted. 

.. figure:: /_static/Workflow_ls.*
   :width: 90%

   **Fig. 2.** Nominal order of processing for F2 longslit spectroscopic data. Color coding as in Fig. 1. 

Reduction Synopsis
::::::::::::::::::
Following the Dark correction described above: 

3. **Sky Subtraction.** The nodded-exposures are subtracted pair-wise, and then combined. 

4. **Flat-field Correction.** The combined image is divided by a normalized **Flat-field MasterCal**, where the response function to the flat-field source has been removed. 

5. **Combine dither sequences** If more than one dither sequence was obtained, images should be combined with outlier (e.g., cosmic-ray) rejection, scaling, and background offseting. 

6. **Apply approximate dispersion solution.** Keywords are recorded in the image header that describe the approximate zero-point and first-order terms of the dispersion solution. These terms will be updated when the wavelength calibration is applied. 

7. **Wavelength Calibration/Transformation.** The dispersion solution derived from the associated arc lamp exposure(s) (and for each slitlet for MOS mode) is written into the extension headers. 

8. **Extract Spectra.** Apertures are defined (usually interactively) for source(s) and sky region(s), and 1-D spectra are constructed for sources by summing along the cross-dispersion direction for each target subtracting a spatial fit to the sky at each wavelength. 

9. **Apply Telluric Correction.** If the spectra require flux calibration, correct for the mean atmospheric absorption at the airmass of the target and apply the sensitivity calibration derived from one or more standard star spectra. 

10. **Apply Flux Calibration.** If the spectra require flux calibration, correct for the mean atmospheric absorption at the airmass of the target and apply the sensitivity calibration derived from one or more standard star spectra. 

Proceed to :ref:`f2-proc-bright-ls` or :ref:`f2-proc-faint-ls`.

