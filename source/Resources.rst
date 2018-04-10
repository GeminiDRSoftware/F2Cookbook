.. _resources:

================
Useful Resources
================

Resources for your data reduction needs are collected here for easy reference. 
Information about the FLAMINGOS-2 instrument design, operation, and observing may be found on the `FLAMINGOS-2 Home Page <http://www.gemini.edu/sciops/instruments/flamingos2/>`_. 

.. _F2-help:

FLAMINGOS-2 Help
----------------
For help with FLAMINGOS-2 data reduction you may find the `Data Reduction Support page <http://www.gemini.edu/sciops/data-and-results/data-reduction-support>`_ useful. 
To address problems with the Gemini software, direct your inquiry as follows: 

* `Astroconda <http://astroconda.readthedocs.io/en/latest/>`_ installation and PyRAF: help@stsci.edu
* Gemini Helpdesk (`<http://www.gemini.edu/sciops/helpdesk/>`_) for problems with:

  * IRAF tools, including the **gemini** packages
  * Gemini Observatory Archive

* Gemini/IRAF `FAQ list <http://www.gemini.edu/sciops/data-and-results/data-reduction-support/faq>`_
* List of `known problems <http://www.gemini.edu/sciops/data-and-results/processing-software/data-reduction-support/known-problems>`_ with **gemini** package software or the data. 
* `Gemini Data Reduction User Forum <http://drforum.gemini.edu/topic-tag/FLAMINGOS-2/>`_, a place for trading ideas, scripts, and best practices.

Standards and Catalogs
----------------------
The following catalogs and other reference material may be of use during your data reduction and analysis: 

* Telluric standard star compendia and a model atmosphere library

  * `Spectroscopic/telluric standards <http://www.gemini.edu/sciops/instruments/nearir-resources/spectroscopic-standards>`_ from Gemini
  * Standard star `spectral library <https://www.eso.org/sci/observing/tools/standards/IR_spectral_library.html>`_ from ESO
  * Standard star `calibration library <http://www.stsci.edu/hst/observatory/crds/calspec.html>`_ from STScI 
  * `IRTF Spectral Library <http://irtfweb.ifa.hawaii.edu/~spex/IRTF_Spectral_Library/>`_

* `DSS <http://archive.eso.org/dss/dss>`_: ESO Online Digitized Sky Survey

* `USNO <http://www.usno.navy.mil/USNO/astrometry/optical-IR-prod/icas>`_ Image and Catalog Archive Server


IRAF Reduction Tools
--------------------

A few of the IRAF data reduction tasks have interactive options, where
the user provides input via the IRAF graphics utility.  These tools
involve cursor interactions and keystrokes, which can be viewed by
entering ``?`` when in cursor mode.  The most commonly used options
for two of the most complex tasks are given below, for reference.
More detailed information can be found in the `IRAF Spectroscopy
Documentation <http://iraf.noao.edu/docs/spectra.html>`_

.. _wav-identify:

Wavelength Calibration
^^^^^^^^^^^^^^^^^^^^^^
Wavelength calibration is performed with the **gnirs.nswavelength**
task, which is really a wrapper for the IRAF **identify** family of
tasks.  The following tables summarize the most common commands
for this task.

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
The following is an abridged list of *colon commands* (i.e., command
names preceded by the ``:`` key) to view (with no argument) or set
(including trailing argument) a **nswavelength** task parameter.  The
commands may be abbreviated.  For a full list see `identify
<http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?identify>`_ or invoke the
``?`` cursor command within an interactive session.

.. tabularcolumns:: |l|l|L|

.. csv-table:: **Identify Colon Commands**
   :header: "Key", "Value", "Description"
   :widths: 10, 10, 30

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


.. _apextract-summary:

APEXTRACT Summary
^^^^^^^^^^^^^^^^^
The aperture extraction utility (`apextract
<http://stsdas.stsci.edu/cgi-bin/gethelp.cgi?apextract.men>`_) in IRAF
is invoked from the **gnirs.nsextract** task.  When run interactively,
this utility provides a variety of cursor keys to control the
extraction of target spectra.  If you use IRAF for your data
reduction, you will need to get comfortable with this task.

Cursor Keys
:::::::::::
The following are the available cursor commands for aperture
definition and spectrum extraction.

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

Note that all parameters having to do with positions or distances are
in units of pixels.




Acknowledgements
----------------
Scientific publications that make use of data obtained from Gemini
facilities should include the appropriate acknowledgement described on
the `Gemini Observatory Acknowledgements
<http://www.gemini.edu/sciops/data-and-results/acknowledging-gemini>`_
page.  You should also cite the FLAMINGOS-2 instrument description
paper by [EE]_.

Citations to this *Cookbook* should read: 

   Shaw, R. A. and Simpson, C. 2018, *FLAMINGOS-2 Data Reduction Cookbook* (Version 1.1; Hilo, HI: Gemini Observatory)

Use of IRAF software should include the following footnote: 

   *IRAF is distributed by the National Optical Astronomy Observatory, which is operated by the Association of Universities for Research in Astronomy (AURA) under a cooperative agreement with the National Science Foundation.*

Use of PyRAF software should also include the following footnote: 

   *PyRAF is a product of the Space Telescope Science Institute, which is operated by AURA for NASA.*


.. only:: html

   Literature references
   ---------------------

   .. [EE] Eikenberry, S., et al. 2004, *FLAMINGOS-2: the facility near-infrared wide-field imager and multi-object spectrograph for Gemini*, `SPIE, 5492, 1196 <http://adsabs.harvard.edu/abs/2004SPIE.5492.1196E>`_

   .. [EE3] Eikenberry, S., et al. 2008, *FLAMINGOS-2: the facility near-infrared wide-field imager and multi-object spectrograph for Gemini*, `SPIE, 7014, 0V <http://adsabs.harvard.edu/abs/2008SPIE.7014E..0VE>`_

   .. [L15] Leggett, et al. 2015, *Near-infrared Photometry of Y Dwarfs: Low Ammonia Abundance and the Onset of Water Clouds*, `ApJ, 799, 37 <http://adsabs.harvard.edu/abs/2015ApJ...799...37L>`_

   .. [L16] Leggett, et al. 2016, *Near-IR Spectroscopy of the Y0 WISEP J173835.52+273258.9 and the Y1 WISE J035000.32-565830.2: The Importance of Non-Equilibrium Chemistry*, `ApJ, 824, 2 <http://adsabs.harvard.edu/abs/2016ApJ...824....2L>`_

   .. [FITS] Pence, W.D., Chiappetti, L, Page, C.G., Shaw, R.A., & Stobie, E. 2010, *Definition of the Flexible Image Transport System (FITS), Version 3.0*, `A&A, 524, 42 <http://adsabs.harvard.edu/abs/2010A%26A...524A..42P>`_

   .. [IRTF] Rayner, J. T., Cushing, M.C., & Vacca, W.D. 2009, *The Infrared Telescope Facility (IRTF) Spectral Library: Cool Stars*, `ApJS, 185, 289 <http://adsabs.harvard.edu/abs/2009ApJS..185..289R>`_ 


.. only:: latex

   .. [EE] Eikenberry, S., et al. 2004, *FLAMINGOS-2: the facility near-infrared wide-field imager and multi-object spectrograph for Gemini*, SPIE, 5492, 1196

   .. [EE3] Eikenberry, S., et al. 2008, *FLAMINGOS-2: the facility near-infrared wide-field imager and multi-object spectrograph for Gemini*, SPIE, 7014, 0V

   .. [L15] Leggett, et al. 2015, *Near-infrared Photometry of Y Dwarfs: Low Ammonia Abundance and the Onset of Water Clouds*, ApJ, 799, 37

   .. [L16] Leggett, et al. 2016, *Near-IR Spectroscopy of the Y0 WISEP J173835.52+273258.9 and the Y1 WISE J035000.32-565830.2: The Importance of Non-Equilibrium Chemistry*, ApJ, 824, 2

   .. [FITS] Pence, W.D., Chiappetti, L, Page, C.G., Shaw, R.A., & Stobie, E. 2010, *Definition of the Flexible Image Transport System (FITS), Version 3.0*, A&A, 524, 42

   .. [IRTF] Rayner, J. T., Cushing, M.C., & Vacca, W.D. 2009, *The Infrared Telescope Facility (IRTF) Spectral Library: Cool Stars*, ApJS, 185, 289
