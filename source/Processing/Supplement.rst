.. _supplement:

======================
Supplementary Material
======================
Several topics intimately tied to data reduction are gathered here for reference. 
Most topics apply to multiple F2 observing configurations. 

.. _gen-obslog:

Creating an Observing Log
-------------------------
Raw data files from a single observing program can number in the hundreds. 
Add to that the files generated during the course of data reduction: intermediate files, :term:`MasterCal` reference files, combined exposures, extracted spectra, etc. and the task of keeping track of files in your workflow rapidly becomes a challenge. 
There is no uniquely correct way to manage the large number of files, but there are a couple of common approaches to sorting through the raw input files: 

1. Separate files of various types (e.g., calibrations, science, etc.) into subdirectories based on common attributes. This is a typical approach for preparing to run IRAF file processing tasks. 

2. Create an `sqlite3 <https://www.sqlite.org>`_ database of files and the relevant metadata (see below). Such a database is useful even if you choose classic IRAF for your image processing, since you can view and select by exposure attributes with the `sqlite browser <http://sqlitebrowser.org>`_. The tool enables you to develop selection criteria, from which file lists with common attributes may be constructed. 

In the latter case it is usually helpful to do the following: 

* Collect the raw calibration exposures (bias, dark, flat) into a subdirectory (called ``/raw`` in the tutorials).
* Collect the raw science exposures (arcs, standard stars, science targets) into the same subdirectory.

Some primary reduction tasks have a ``rawpath`` parameter that allows processing in the main work directory, while accessing input files from a subdirectory (called ``/raw`` in the tutorials). 
Finally, the intermediate files, by default, follow a :ref:`file-nomenclature` based on a prefix to the input file names, to make them easy to identify. 
Once these intermediate files have been checked for quality *and* you are certain you no longer need them, they can be deleted.

.. _sqlite3-browser:

SQLite Database
^^^^^^^^^^^^^^^
You can build an observing log with a python script (download: :download:`obslog.py <../pyTools/obslog.py>`), in the form of an `sqlite3 <https://www.sqlite.org>`_ database. 
The script will create a database with the fields and metadata described below. 
At the unix prompt, create the observing log and store it a file (``obsLog.sqlite3``) in the ``/raw`` subdirectory. 

.. code-block:: bash

   cd /path/to/work_directory/raw
   python obslog.py obsLog.sqlite3
   
You may add the ``-v`` option to also write the metadata for each file to STDOUT, which you can re-direct to an ASCII file. 
(Use the ``-h`` option to display command-line help.) 
The output file is an SQLite3 database, which can be accessed via the python API, or viewed directly with the `SQLite3 browser <http://sqlitebrowser.org>`_. 
An example of the data browser is shown below. 
The browser provides a quick way of assessing the content of an observing program, and for crafting the correct selection criteria for grouping files with related content. 

.. figure:: /_static/SQLite3.*
   :width: 100 %

   SQLite3 browser showing the observing log for Longslit program GS-2013B-Q-79. Of the 164 entries in the database, 10 have been selected by entering text of interest into the dialog boxes above the top row. In this case, file header keywords matching ``ObsType=OBJECT``, ``ObsClass=partnerCal`` and ``Disperser=JH`` yield the standard star exposures with the ``JH`` grism, along with other associated metadata including aperture, and filter. Note the lack of case sensitivity and minimum-match to text for the selection. Click to enlarge. 

The PyRAF tutorials use SQL to select files that match exposure metadata stored in the database.

.. _header-metadata:

Header Metadata
^^^^^^^^^^^^^^^
Values from the keywords listed below are harvested from the data headers. 
Some of the names are obscure, so they are re-mapped to somewhat more intuitive field names if you create an **sqlite3** database. 
Fields may be added (or deleted: *not recommended*) by changing the KW_MAP definition at the top of the python script. 

.. _log-keywords:

.. csv-table:: **Critical Header Metadata**
   :header: "Keyword", "DB Field", "Description"
   :widths: 15, 15, 60

    , ``use_me``, Flag: indicates file usage or exclusion [``1|0``]. Not present in the ASCII version of the log. 
   ``DATE-OBS``, ``DateObs``, UT Date of observation start (YYYY-MM-DD)
   ``TIME-OBS``, ``TimeObs``, UT Time of observation start (HH:MM:SS.S)
   ``OBJECT``, ``Object``, Name for target of exposure.
   ``RA``, ``RA``, Right Ascension of target (deg)
   ``DEC``, ``Dec``, Declination of target (deg)
   ``RAOFFSET``, ``RA_Offset``, Offset in Right Ascension from target (arcsec)
   ``DECOFFSE``, ``Dec_Offset``, Offset in Declination from target (arcsec)
   ``OBSTYPE``, ``ObsType``, Type of observation: [``arc|cal|dark|flat|mos|mask|pinhole|ronchi|object``]
   ``OBSCLASS``, ``ObsClass``, Class of observation: [``acq|acqCal|dayCal|partnerCal|progCal|science``]
   ``READMODE``, ``ReadMode``, Detector readout Mode [``Bright|Medium|Dark``]
   ``LNRS``,   ``N_Reads``, Number of non-destructive reads
   ``COADDS``, ``CoAdds``, Number of array co-adds
   ``FILTER``, ``Filter``, Name of selected filter [``Open|Y|J-lo|J|H|Ks|K-long|JH|HK``]
   ``GRISM``, ``Disperser``, Name of selected disperser: [``Open|JH|HK|R3K``]
   ``MASKNAME``, ``AperMask``, Name for selected slit(mask) [``[None|<n>pix-slit]``]
   ``MASKTYPE``, ``MaskType``, MOS mode? [``0|1``]
   ``DECKER``, ``Decker``, Decker position? [``longslit|??``]
   ``PA``, ``Rotator``, Position angle (:math:`\rho`) of slit on sky (N through E). At :math:`\rho = 0` (default) N is "up" and E is to the "left" in a default **ds9** display 
   ``GRWLEN``, ``CentWave``, Grating approximate central wavelength (nm)
   ``EXPTIME``, ``T_exp``, Exposure duration (s)
   ``AIRMASS``, ``Airmass``, Atmospheric column through which exposure was obtained

Be sure to browse the observing log and/or display the exposures, and remove (or mark as "excluded") any files that should **not** be processed, such as test or acquisition exposures. 

.. _dr-keywords:

F2 Processing Keywords
----------------------
The keywords listed below are introduced or modified during the course of processing. 

.. csv-table:: **Processing Keywords**
   :header: "Keyword", "Added by", "Description"
   :widths: 15, 15, 70

   ``CA-FLAG``,  `` ``, Flag for flux calibration
   ``CDi_j``,    `` ``,   :term:`WCS` transformation matrix between pixel axis ``j`` and world coordinate axis ``i``
   ``CRPIXj``,   `` ``,   Location of the reference point in the image for pixel axis ''j''
   ``CRVALi``,   `` ``,   World coordinate value at reference point for axis ``i``
   ``CTYPEi``,   `` ``,   Type for intermediate coordinate for axis ``i``
   ``DC-FLAG``,  `` ``, Flag for dispersion correction
   ``DCLOG1``,   `` ``, Name of reference arc
   ``DISPAXIS``, ``fprepare``,  Axis number of dispersion direction (2 for spectroscopy)
   ``DISPERSI``, ``f2cut``,     Dispersion (Ang/pix)
   ``EXTNAME``,  ``fprepare``,  Name of extension (SCI)
   ``EXTVER``,   ``fprepare``,  Version of extension (1 to no. amps in use)
   ``F2CUT``,    ``f2cut``,     UT Time stamp for F2CUT
   ``FLATIM``,   ``nsreduce``,  Name of **Flat-field MasterCal**
   ``GAIN``,     `` ``,   Updated value of gain from DB
   ``GEMARITH``, ``gemarith``,  UT Time stamp for GEMARITH
   ``GEM-TLM``,  <Any task>,     UT Timestamp for last modification by a gemini task
   ``GOFFREF``,  ``NSREDUCE``,  GEMOFFSETLIST spatial reference image
   ``LTMi_j``, ``f2prepare``,   Transformation matrix between detector (``i``) and raw image (``j``) axes
   ``NONLINCR``, ``fprepare``,  Non-linear correction applied
   ``NONLINEA``, ``fprepare``,  Non-linear regime (ADU)
   ``NSAPPWAV``, ``nsappwav``,  UT Time stamp for NSAPPWAV
   ``NSREDUCE``, ``f2cut``,     UT Time stamp for NSREDUCE
   ``OBSMODE``,  `` ``,      Observing mode; derived from ``MASKTYP`` (IMAGE|MOS)
   ``PREPARE``,  ``fprepare``,  UT Time stamp for F2PREPARE
   ``RAWFILT``,  ``fprepare``,  Raw FILTER keyword value
   ``RAWGAIN``,  ``fprepare``,  Value of gain for raw exposure
   ``RAWPIXSC``, ``fprepare``,  Raw PIXSCALE keyword value
   ``RDNOISE``,  `` ``,         Updated value of read noise from DB
   ``SATURATI``, ``fprepare``,  Saturation level (ADU)
   ``SKYIMAGE``,  ``nsreduce``, Sky image subtracted from raw data
   ``WAT0_001``, ``fprepare``,  IRAF WCS coordinate system
   ``WAT1_001``, ``fprepare``,  IRAF WCS description
   ``WAT2_001``, ``fprepare``,  Continuation of IRAF WCS description
   ``WAVTRAN``,  ``fprepare``,  Name of reference wavelength solution

.. caution::
   The **f2** and/or **gnirs** tasks *require* the above keywords from prior reduction stages to be present and populated correctly for processing to proceed to the next stage. If you choose to perform some of the processing with your own or other IRAF tools, you will need to ensure that the expected processing keywords are inserted into the output headers if you want to continue processing with **f2/gnirs** tasks. 

.. _calib-suppl:

Calibration Material
--------------------
Many calibration reference files are distributed with IRAF and the **gemini** package. 
Others are available from other sources. 
This sections provides pointers to many of the files you will need for F2. 

.. _arc-atlas:

Arc Lamp Atlas
^^^^^^^^^^^^^^
Line identifications for the Argon comparison arc may be found in a variety of places. 
See line lists and atlases on the `GNIRS/GCAL Arc lamp page <http://www.gemini.edu/sciops/instruments/gnirs/calibration/arc-lamp-ids>`_, for instance.  
A one-page atlas of the comparison arc is shown below. 

.. figure:: /_static/Ar_IR.* 
   :width: 90 %

   Spectra of the Ar comparison arc with the JH (*top*) and HK (*bottom*) grisms. Insets show weaker lines magnified (*purple*) and displaced vertically for clarity. Brighter and/or isolated lines of Ar_I are labeled, which should be enough to bootstrap a wavelength solution. Click to enlarge. 

The Ar lamp is the primary wavelength calibration source for F2, and line lists are provided in multiple IRAF packages. 

.. csv-table:: **Ar Arc Line Lists**
   :header: "Location", "Notes"
   :widths: 20, 40

   ``linelists$argon.dat``, Default IRAF list for Ar lines in the near-IR **in vacuum** from *Wavelength Standards in the Infrared* by K.N. Rao et al. (1966).
   ``gemini$gcal/linelists/argon.dat``, Ar line list for **gemini** package. Little provenance is given but the wavelengths seem to match the IRAF list where they overlap **in vacuum**. Lines taken from various observatories are noted. 
   ``gnirs$data/argon.dat``, Ar line list for **gnirs** package. Little provenance is given but the wavelengths seem to match the IRAF list where they overlap **in vacuum**. Lines taken from various observatories are noted.
   Download: :download:`Ar_NIR_lowres.txt <../calib/Ar_NIR_lowres.txt>`, Edited list of vacuum wavelengths for low-resolution (JH and HK grisms) taken from the NIST database (ca. 2017) downloadable with this *Cookbook*. Includes spectrum ID and notional relative intensities. Also gives literature references per ion. 

.. _ir-background:

IR Background Removal
---------------------
The night-sky background in the infrared is composed of emission lines and continuum, with the latter increasing strongly with wavelength. 
This background very often dominates the brightness of astrophysical targets, and it is variable on timescales of minutes. 
The thermal background from the telescope and instrument is also fairly strong in the K-band, but it is fairly stable. 
These facts lead to common strategies for measuring and removing the background: 

* Keep the integrations relatively short (less than a few minutes).
* Offset the telescope to a nearby position to measure the background with the same pixels used to detect the astrophysical target. This often consists of: 

  - Nodding the telescope several arcsec in an ABBA pattern (along the slit for longslit spectroscopic mode)
  - Offsetting the telescope by a large amount, away from a very extended target
  - Dithering the telescope, offsetting several arcsec in both RA and Dec in some pattern

* Subtract the sky exposures from the source exposures pair-wise to track short-timescale variations in sky, then combine the result.

One such :math:`3\times3` dither pattern is shown below for imaging. 

.. figure:: /_static/Dither.*
   :width: 80 %

   Nine-position dither pattern for IR imaging, for which offset exposures of equal duration are obtained sequentially in the serpentine order shown (*numbers* connected by *light blue arrows*). Center of the circular FoV is offset :math:`\pm15` arcsec in RA and Dec, relative to the initial exposure; offset between numbers in the figure is expanded by :math:`\times2` for clarity. Depth of combined exposure of the target field is represented by the intensity of the colored area (*red*). 

IRAF Reduction Tools
--------------------
A few of the IRAF data reduction tasks have interactive options, where the user provides input via the IRAF graphics utility. 
These tools involve cursor interactions and keystrokes, which can be viewed by entering ``?`` when in cursor mode. 
The most commonly used options for two of the most complex tasks are given below, for reference. 

.. _wav-identify:

Wavelength Calibration
^^^^^^^^^^^^^^^^^^^^^^
Wavelength calibration is performed with the **gnirs.nswavelength** task, which is really a wrapper for the IRAF **identify** family of tasks. 
See the excellent `identify tutorial <http://www.twilightlandscapes.com/IRAFtutorial/IRAFintro_06.html#H>`_ by Josh Walawender for details. The following tables summarize the most common cursor commands for this task. 

Cursor Keys
:::::::::::
.. csv-table:: **Identify Cursor Keys**
   :header: "Key", "Description"
   :widths: 5, 60

   ``?``, Clear the screen and print a menu of options.
   ``a``, Apply next *center* or *delete* operation to *all* features
   ``b``, Identify features and find a dispersion function automatically using the coordinate line list and approximate values for the dispersion.
   ``c``, Center the feature nearest the cursor. Used when changing the position finding parameters or when features are defined from a previous feature list.
   ``d``, Delete the feature nearest the cursor. Delete all features when preceded by the ``a`` ll key. This does not affect the dispersion function.
   ``e``, Find features from a coordinate list without doing any fitting. This is like the ``l`` key without any fitting.
   ``f``, Fit a function of the pixel coordinates to the user coordinates. **This enters the interactive function fitting package.**
   ``g``, Fit a zero point shift to the user coordinates by minimizing the difference between the user and fitted coordinates. The coordinate function is not changed.
   ``i``, Initialize (delete features and coordinate fit).
   ``l``, Locate features in the coordinate list. A coordinate function must be defined or at least two features must have user coordinates from which a coordinate function can be determined. If there are features an initial fit is done; then features are added from the coordinate list; and then a final fit is done.
   ``m``, Mark a new feature using the cursor position as the initial position estimate.
   ``n``, Move the cursor or zoom window to the next feature (same as ``+``).
   ``p``, Pan to the original window after zooming on a feature.
   ``q``, Quit and continue with next image.
   ``r``, Redraw the graph.
   ``s``, Shift the fit coordinates relative to the pixel coordinates. The user specifies the desired fit coordinate at the position of the cursor and a zero point shift to the fit coordinates is applied. If features are defined then they are recentered and the shift is the average shift. The shift is printed in pixels & user coordinates & z (fractional shift).
   ``u``, Enter a new user coordinate for the current feature. When marking a new feature the user coordinate is also requested.
   ``w``, Window the graph. A window prompt is given and a number of windowing options may be given. For more help type ``?`` to the window prompt or see help under gtools.
   ``x``, Find a zero point shift for the current dispersion function. This is used by starting with the dispersion solution and features from a different spectrum. The mean shift is printed in user coordinates & mean shift in pixels & the fractional shift in user coordinates.
   ``z``, Zoom on the feature nearest the cursor. The width of the zoom window is determined by the parameter zwidth.
   ``.``, Move the cursor or zoom window to the feature nearest the cursor.
   ``+``, Move the cursor or zoom window to the next feature.
   ``-``, Move the cursor or zoom window to the previous feature.

Colon-command Summary
:::::::::::::::::::::
The following is an abridged list of *colon commands* (i.e., command names preceded by the ``:`` key) to view (with no argument) or set (including trailing argument) a **nswavelength** task parameter. 
The commands may be abbreviated. 
For a full list see `identify <http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?identify>`_ or invoke the ``?`` cursor command within an interactive session.

.. csv-table:: **Identify Cursor Keys**
   :header: Key, Value, Description
   :widths: 5, 10, 60

   ``:show``, file, Show the values of all the parameters. If a file name is given then the output is appended to that file. If no file is given then the terminal is cleared and the output is sent to the terminal.
   ``:features``, file, Print the feature list and the fit rms. If a file name is given then the output is appended to that file. If no file is given then the terminal is cleared and the output is sent to the terminal.
   ``:coordlist``, file, Set or show the coordinate list file.
   ``:cradius``, value, Set or show the centering radius in pixels.
   ``:threshold``, value, Set or show the detection threshold for centering.
   ``:database``, name, Set or show the database for recording feature records.
   ``:ftype``, value, Set or show the feature type (emission or absorption).
   ``:fwidth``, value, Set or show the feature width in pixels.
   ``:labels``, value, Set or show the feature label type (``none|index|pixel|coord|user|both``). None produces no labeling; index labels the features sequentially in order of pixel position; pixel labels the features by their pixel coordinates; coord labels the features by their user coordinates (such as wavelength); user labels the features by the user or line list supplied string; and both labels the features by both the user coordinates and user strings.
   ``:match``, value, Set or show the coordinate list matching distance.
   ``:maxfeatures``, value, Set or show the maximum number of features automatically found.
   ``:minsep``, value, Set or show the minimum separation allowed between features.
   ``:zwidth``, value, Set or show the zoom width in user units. 

_

.. _apextract-summary:

APEXTRACT Summary
^^^^^^^^^^^^^^^^^
The aperture extraction utility (`apextract <http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?apextract.men>`_) in IRAF is invoked from the **gnirs.nsextract** task. 
When run interactively, this utility provides a variety of cursor keys to control the extraction of target spectra. 
If you use IRAF for your data reduction, you will need to get comfortable with this task. 
See the excellent `apextract.apall tutorial <http://www.twilightlandscapes.com/IRAFtutorial/IRAFintro_06.html>`_ by Josh Walawender for details. 

The following are the available cursor commands for aperture definition and spectrum extraction. 

.. csv-table:: **Aperture Editor Cursor Keys**
   :header: Key, Ap, Description
   :widths: 5, 5, 60

   ``?``,   , Print help
   ``a``,   , Toggle the ALL flag
   ``b``, an, Set background fitting parameters
   ``c``, an, Center aperture(s)
   ``d``, an, Delete aperture(s)
   ``f``,   , Find apertures up to the requested number 
   ``g``, an, Recenter aperture(s) 
   ``l``, ac, Set *lower* limit of current aperture at cursor position (see ``u``)
   ``m``,   , Define and center a new aperture on the profile near the cursor
   ``n``,   , Define a new aperture centered at the cursor
   ``q``,   , Quit
   ``r``,   , Redraw the graph
   ``s``, an, Shift the center(s) of the current aperture to the cursor position
   ``t``, ac, Trace aperture positions
   ``u``, ac, Set *upper* limit of current aperture at cursor position  (see ``l``)
   ``w``,   , Window the graph using the window cursor keys
   ``y``, an, Set aperture limits to intercept the data at the cursor y position
   ``z``, an, Resize aperture(s) 
   ``.``,  n, Select the aperture nearest the cursor to be the current aperture
   ``+``,  c, Select the next aperture (in ID) to be the current aperture
   ``-``,  c, Select the previous aperture (in ID) to be the current aperture
   ``I``,   , Interrupt task immediately. Database information is not saved.

The letter a following the key indicates if all apertures are affected when the ALL flag is set. The letter ``c`` indicates that the key affects the *current* aperture while the letter ``n`` indicates that the key affects the aperture whose center is *nearest* the cursor. 

Colon-command Summary
:::::::::::::::::::::
The following is an abridged list of colon commands (i.e., command names preceded by the ``:`` key) to view (with no argument) or set (including trailing argument) a **nsextract** task parameter. 
For a full list see `apall <http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?apall>`_ or invoke the ``?`` cursor command within an interactive session.

.. csv-table:: **Aperture Editor General Colon-commands**
   :header: "Command", "Description"
   :widths: 18, 50

   ``:b_function``, Background fitting function
   ``:b_function``, Background fitting function
   ``:b_high_reject``/ ``:b_low_reject``, Background high/low rejection limits
   ``:b_naverage``, Determine background from average or median
   ``:b_order``, Function order for background fit
   ``:b_sample``, Comma-separated list of background sample region(s) [``nnn:nnn``]
   ``:background``, Background to subtract (e.g. ``none``)
   ``:bkg``, Subtract background in automatic width? [``yes`` | ``no``]
   ``:clean``, Detect and replace bad pixels? [``yes`` | ``no``]
   ``:extras``, Extract sky & sigma etc. in addition to spectrum?
   ``:line``, Dispersion line over which to display profile
   ``:nsum``, Extent over which to determine profile (positive for *sum* or negative for *median*)
   ``:lower/:upper``, Lower/upper aperture limits relative to center
   ``:lsigma/:usigma``, Lower/upper rejection threshold
   ``:parameters``, Print the current value of all parameters
   ``:radius``, Profile centering radius
   ``:t_function``, Type of fitting function for trace
   ``:t_high_reject``/ ``:t_low_reject``, Upper/lower rejection limits for trace [sigma]
   ``:t_nsum``, Number of dispersion pixels to sum for trace
   ``:t_order``, Order of trace fitting function
   ``:t_step``, Step size for fitting function 
   ``:weights``, Extraction weights [``none`` | ``variance``]
   ``:width``, Profile centering width

Note that all parameters having to do with positions or distances are in units of pixels. 

For Further Reading
-------------------

.. _dispersion-solution:

Description of the Dispersion Solution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The grisms used in F2 introduce significant nonlinearity to the dispersion relation, which can generally be well characterized with a Legendre or Chebyshev polynomial of order 4 or 5. 
If a non-linear dispersion solution is written directly into the FITS header (as it is by the IRAF task ``dispcor`` when linearization is turned off), it will consist of a number of terms including the coefficients of the fitted polynomial. 
The coefficients are described in the paper `The IRAF/NOAO Spectral World Coordinate Systems <http://www.researchgate.net/publication/2308651_The_IRAFNOAO_Spectral_World_Coordinate_Systems>`_ (1991, F. Valdes). 
The following excerpt describes how to compute wavelengths from the nonlinear function of choice. 

There are three coordinates of relevance: the pixel coordinate *p* of the spectrum array; the normalized coordinates *n* over the domain of the fitting function, in the interval [-1, 1]; and the world coordinates *w* at each pixel. The transformation from pixel to normalized coordinates *n* is: 

.. math::
   n = \frac{2p - (p_{max} +p_{min})}{(p_{max}-p_{min})} 

Note that in practice the range of pixels will extend somewhat beyond the domain over which the fitting function was defined. 
For a single function type (the usual case unless comparison arcs taken immediately before and after a science exposure are used to refine the wavelength zero-point), the transformation from pixel coordinates *p* and world coordinates *w* is:

.. math::
   w = \frac{\Delta \lambda+\Lambda(p)}{(1+z)}

where *z* is the Doppler factor. The dispersion function :math:`\Lambda(p)` at pixel *p* can be evaluated over the function coefficients :math:`c_i`: 

.. math::
   \Lambda(p) = \sum_{i=1}^{order} c_i x_i

where :math:`x_1 = 1; x_2 = n`. The non-linear terms for order :math:`i>2` may be computed recursively; for Chebyshev polynomials we have:

.. math::
   x_i = 2nx_{i-1} - x_{i-2}

or for Legendre polynomials: 

.. math::
   x_i = \frac{(2i-3)nx_{i-1} - (i-2)x_{i-2}}{(i-1)}

IRAF spectroscopic tasks have a built-in capability to read dispersion solutions with the above form. 
For python users the following snippet of code may be used to construct a wavelength array from Legendre or Chebyshev function parameters and coefficients, using the functions in :download:`poly.py  <../pyTools/poly.py>`:

.. code-block:: python

   import numpy as np
   import poly as pl

   # Extract function, parameters, and coefficients from WAT2_00x keywords. 
   # An example from the center of an arc comparison exposure using grism b2k 
   # and facility longslit 3pxC:
   pMin, pMax = [90.65229797363281, 4054.766357421875]
   c = np.array([5160.180854771875, 1399.010545377342, 64.60055185877235, -24.74632014374652, 0.1313465583541718, -0.1962541400576848, -0.06403879553807495])
   nPix = 4096

   # Generate an array of world coordinates (in Angstroms, the declared WCS unit).
   n = pl.getNormCoords(pMin, pMax, nPix)
   w = pl.evDispersion(pl.evLegendre, c, n)

.. _wcs:

World Coordinate Systems
^^^^^^^^^^^^^^^^^^^^^^^^
It is useful to have at least an approximate World Coordinate Solution (:term:`WCS`) specified in the header of your science images; this solution can be refined later in target processing. 

.. _imaging-wcs:

Imaging WCS
:::::::::::
For imaging mode exposures, the WCS may be of scientific interest even when imaging was not the focus of the original observing program. 
For observing programs that used custom MOS slits, the WCS in acquisition images is helpful for associating slit locations with specific targets (or regions within extended astronomical objects).  

Setting the WCS Description
:::::::::::::::::::::::::::
An approximate solution was inserted in the observing environment from the telescope alignment during each exposure, and the instrument rotator angle. 
The following table lists the WCS keywords that are necessary to specify a complete FITS WCS in the image extension header. 

.. csv-table:: **GMOS Image WCS Keywords**
   :header: "Keyword", "Update", "Value", "Meaning"
   :widths: 10, 10, 15, 50

   ``RADECSYS``, Deleted, ``-``, Deprecated keyword
   ``WCSASTRM``, Deleted, ``-``, Not used for WCS
   ``RADESYS``,  Added,   ``FK5``, Celestial coordinate reference frame
   ``WCSAXES``,  Added,   ``2``,   Number of axes in WCS description
   ``CTYPEi``,   Updated, ``RA---TAN``, Coordinate type for axis ``i``
   ``CUNITi``,   Updated, ``deg``, Coordinate units for axis ``i``
   ``LTVi``,     Updated, ``0``,   CCD to image offset: axis ``i``
   ``CDi_j``,    Updated, (see below), Derivative of World Coordinate values ``i`` w.r.t pixel array ``j`` at the reference location

The CD matrix is given by the following: 

.. math::
   \begin{pmatrix}
   \mathtt{CD1\_1}  & \mathtt{CD1\_2} \\ 
   \mathtt{CD2\_1}  & \mathtt{CD2\_2} 
   \end{pmatrix} = \sigma
   \begin{pmatrix}
   -\cos\theta & \sin\theta \\ 
   -\sin\theta & -\cos\theta 
   \end{pmatrix} 

where:

.. math::
   & \theta =  \mathtt{PA} \\
   & \sigma =  \mathit{(plate scale)}/\mathrm{3600} \\

In the above, *platescale* is in arcsec/pixel, ``PA`` is the position angle in degrees given by this keyword value, and :math:`\theta` is measured from North through East. 
For F2, :math:`\theta=0` yields an orientation where N is down and E is to the left.

.. _refine-imaging-wcs:

Refining the Reference Coordinates
::::::::::::::::::::::::::::::::::
The world coordinates at the reference pixel are taken from the commanded telescope pointing, which may be off by up to a few arcmin. 
The WCS zero-point can be adjusted by correcting the CRVALi keywords with offsets determined from stars in the field. 
Often this correction can be determined using the `SAOImage DS9 <http://ds9.si.edu/site/Home.html>`_ image display tool. 
The process is: 

   * Process the image through bias- and flat-fielded correction
   * Display the image in DS9
   * From the pull-down menu, select "**WCS** :math:`\rightarrow` degrees" for the coordinate display
   * Select **Analysis** :math:`\rightarrow` Catalogs :math:`\rightarrow` Optical :math:`\rightarrow` USNO UCAC3
   * Compare the pattern of star locations with those of the catalog, as shown below

.. figure:: /_static/catalog_wcs.*
   :scale: 75 %

   Image of NGC 6302, with positions of catalog stars plotted (*green circles*). Note the "c" shaped pattern of catalog stars (bottom, left) appears to match that of stars in the image (bottom, center).

   * Select any star from the catalog (sorting by RA or Dec may help) and:

     * record the coordinates from both the catalog star and the image display cursor at the position of that star in the image
     * compute the difference (i.e., the offset values in degrees) in each coordinate

   * Update the ``CRVAL1`` and ``CRVAL2`` keyword values with these offsets

Highly Accurate WCS
:::::::::::::::::::
If your science objectives require a highly accurate WCS you must determine a full WCS solution with community software, such as the IRAF ``mscred.mscfinder.msctpeak`` task (see the `tutorial <http://iraf.noao.edu/projects/ccdmosaic/astrometry/astrom.html#msctpeak>`_). 
An astrometric catalog will be needed for this calibration; magnitudes in the same bandpass will be needed for the photometric calibration. 
Although the process to fit a full WCS solution is involved, it is possible to characterize optical distortions into the WCS (using the ``TNX`` projection); RMS uncertainties of 200 mas should be achievable. 

Refined Imaging WCS
...................
Solving for the WCS in a image requires using community software. There are a few possibilities, some of which also require local access to an astrometric catalog. The options include: 

 * The IRAF `MSCRED package <http://iraf.noao.edu/projects/ccdmosaic/astrometry/astrom.html>`_ (requires catalog)
 * The `astrometry.net <http://astrometry.net>`_ software (downloading & installing software may be necessary)
 * Using `Aladin <http://aladin.u-strasbg.fr>`_ to determine WCS, and transferring the keywords to the header manually
 * Using the `USNO image and catalog service <http://www.usno.navy.mil/USNO/astrometry/optical-IR-prod/icas/fchpix>`_

Refined Spectroscopic WCS
.........................
It is possible to refine the zero-point of the wavelength calibration if night-sky emission lines are present in your spectrogram, using the **rv** package. 

Advanced Longslit WCS
.....................
It is possible to create a linear WCS that will describe the RA and Dec along the slit, as well as wavelengths in the dispersion direction, by introducing a degenerate third image axis, as described by Calabretta & Greisen (`2002, A&A, 395, 1077 <http://adsabs.harvard.edu/abs/2002A%26A...395.1077C>`_; Sect. 7.4.3). 

