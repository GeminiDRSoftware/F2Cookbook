.. _f2-proc-bright-ls:

===============================================
Reduction of Bright, JHK-band Long-Slit Spectra
===============================================
This tutorial reduces long-slit spectra from the program GS-2013B-Q-79 (PI:Gagne), longslit spectra of the bright M6 dwarf star WISE J021653.27-550550.6, observed on 2014-Jan-21. 
The spectra were obtained with the ``4pix-slit`` (0.72 arcsec) slit and the ``JH`` and ``HK`` grisms. 
Telluric standards were included in the observing plan, as were Ar comparison arcs. 
Gagne, et al. (2015; [G15]_) describe the data reduction procedures they followed, which are very similar to those described below. 

.. contents:: 
   :depth: 3

Tutorials for other configurations are listed below:

* :ref:`f2-proc-dith-img`
* **[Img f2-proc-offset-img]**
* :ref:`f2-proc-faint-ls`

Retrieve & Organize Data
------------------------
The first step is to retrieve the data from the Gemini Observatory Archive (see :ref:`archive-search`). 
We will retrieve exposures within about a month of the target exposures in 2014 Nov-Dec. 
You may search the `GOA <https://archive.gemini.edu/searchform>`_ yourself, or instead just cut-and-paste the following direct URL in your browser. 

.. code-block:: html

   # longslit spectra of WISE J0216:
   https://archive.gemini.edu/searchform/GS-2013B-Q-79-1152/cols=CTOWFEQ/NOTAO/notengineering/F2/LS/NotFail

After retrieving the science data, click the **Load Associated Calibrations** tab on the search results page and download the associated bias and flat-field exposures. 
Unpack all of them in a subdirectory of your working directory named ``/raw``. 
Be sure to uncompress the files. 
See :ref:`retrieve-data` for details. 

.. _ls-bright-exp-summary:

Exposure Summary
^^^^^^^^^^^^^^^^
The data contain exposures of a specific science target, telluric standards, and dayCal calibrations that are summarized in the table below. 
All exposures were obtained with ``ReadMode = Bright``.

.. csv-table:: **Exposure Summmary**
   :header: "Target", Band, T_exp, N_exp, Date, AirMass
   :widths: 20, 8, 8, 8, 25,10

   J0126-5505,     JH, 30,  4, 2014-Jan-21, 1.393
                 , HK, 30,  4, 2014-Jan-21, 1.414
   HD 99216 (F5V), JH,  6,  6, 2014-Jan-21, 1.047
   HIP 6546 (A2V), JH,  5,  4, 2014-Jan-21, 1.476
                 , HK, 10,  4, 2014-Jan-21, 1.491
   Dark,           --, 80, 32, 2014-Jan-17 --- 2014-Feb-17,
       ,           --, 40, 12, 2014-Jan-17 --- 2014-Jan-18,
       ,           --, 30, 10, 2014-Jan-18 --- 2014-Feb-09,
       ,           --, 15, 12, 2014-Jan-18 --- 2014-Jan-23,
       ,           --, 10, 10, 2014-Jan-18 --- 2014-Jan-23,
       ,           --,  6, 19, 2014-Jan-16,
       ,           --,  5, 10, 2014-Jan-18 --- 2014-Jan-23,
       ,           --,  4, 22, 2014-Jan-16 --- 2014-Jan-23,
   GCAL Flat,      JH,  4, 10, 2014-Jan-17 --- 2014-Jan-21,
            ,      HK, 80, 10, 2014-Jan-16 --- 2014-Feb-14,
   GCAL Ar Arc,    JH, 15,  3, 2014-Jan-21,
              ,    HK, 40,  1, 2014-Jan-21,

The later two JH flats were obtained just before or after the exposures of the telluric standards. 

Processing Preparation
^^^^^^^^^^^^^^^^^^^^^^
Reference Files
:::::::::::::::
The required **MasterCals** are: 

* Dark
* Flat-field (from the GCAL source)
* Wavelength calibration (from Ar comparison arcs)
* Telluric standard
* Flux calibration from a `model atmosphere library <http://irtfweb.ifa.hawaii.edu/~spex/IRTF_Spectral_Library/index_files/F.html>`_

All of them will be constructed in this tutorial. 

Software
::::::::
You must create an observing log database of the data in the ``./raw`` subdirectory. 
Download: :download:`obslog.py <../pyTools/obslog.py>` to the ``./raw`` subdirectory, and execute it from the unix prompt.

.. code-block:: bash

   python obslog.py obsLog.sqlite3

See :ref:`gen-obslog` for details.

Also retrieve the python file selection module, which includes template SQL statements for selecting files, and functions for specifying metadata on which to perform selections. 

* Download: :download:`fileSelect.py <../pyTools/fileSelect.py>`

Place this module in your work directory; it is used by the reduction script (below). 
You can perform all of the processing steps for this tutorial by downloading the Longslit Tutorial **python** script. 

* Download: :download:`f2_lsBrightProc.py <../pyTools/f2_lsBrightProc.py>` 

You may find it useful to download the script to follow this tutorial in detail, and use it as the basis for reducing other longslit observations. 

Configuration Parameters
::::::::::::::::::::::::
A large number of configuration parameters are used to customize the processing for an observing run. 
See :ref:`config-files` for details. 
These parameter--value pairs are represented in the **python** session as dictionaries. 
Download the following files to your work directory, and customize them as necessary for the observing run.

* Download IRAF task parameters: :download:`lsTaskPars.yml <../pyTools/lsTaskPars.yml>` 
* Download observing configurations: :download:`lsBrightObsConfig.yml <../pyTools/lsBrightObsConfig.yml>` 
* Download arc exposure attributes: :download:`lamps.yml <../pyTools/lamps.yml>`
* Download standard star attributes: :download:`lsBrightTargets.yml <../pyTools/lsBrightTargets.yml>`

Finally, fetch the Ar line list, which has been optimized for the medium-resolution grisms. 

* Download: :download:`Ar_NIR_lowres.txt <../calib/Ar_NIR_lowres.txt>` 

The PyRAF Session
-----------------
After starting your PyRAF session, load the necessary packages. 
Note that the order of import matters as there are some dependencies between packages. 

.. code-block:: python

   import copy
   import yaml
   from pyraf import iraf
   from pyraf.iraf import gemini
   from pyraf.iraf import gemtools, gnirs, niri
   from pyraf.iraf import f2
   import fileSelect as fs

The next order of business is to define a few global variables for processing. 
Note that it is *essential* to create an observing log before proceeding.

.. code-block:: python

   # Path to raw exposures
   rawpath = './raw/'
   # Observing log database
   dbFile = rawpath + 'obsLog.sqlite3'
   iraf.imtype = 'fits'

.. Note::

   If you end your PyRAF session before completing the reductions, then resume within a different session, you must first repeat all of the steps where variables or functions are defined (but not the processing loops), such as those in the code blocks above. 

Now load the IRAF task and observing configuration parameters for your PyRAF session:

.. code-block:: python

   # IRAF task parameters
   with open('lsTaskPars.yml','r') as yf:
       pars = yaml.load(yf)

   # Observing configurations to support exposure queries
   with open('lsBrightObsConfig.yml','r') as yf:
       qd = yaml.load(yf)

The contents of these dictionaries are updated as necessary throughout the course of data reduction processing to select relevant exposures. 

Processing Basics
^^^^^^^^^^^^^^^^^
In the remainder of this tutorial, the general approach to processing is: 

* use python dictionaries to contain the processing task parameters (either read from **.yml** files or a modified copy of a dictionary from another invocation)
* construct a query to obtain a list of files to process, and create a template for output filenames
* execute the task(s) over the file lists

It is handy to have a small utility routine to create an IRAF-style comma-separated list of filenames (e.g., *file1.fits,file2.fits,...*) from a **python** ``list`` of input filenames. 
The function below will create such a string, and prepend a prefix (which may be an empty string) to each file name. 

.. code-block:: python

   def flistToStr(prefix, fileList):
       '''Create a comma-separated string of file names (with a prefix)
          from a python list.
       '''
       return ','.join(str(prefix+x) for x in fileList)

Calibration Processing
----------------------
The next steps will create the necessary **MasterCal** reference files that are used to calibrate the science exposures. 
Files are selected by matching specific exposure metadata in the observing log database (see :ref:`dr-keywords`). 
Within the PyRAF session, first create the **Dark MasterCals**:

Processing with nsreduce
^^^^^^^^^^^^^^^^^^^^^^^^
The ``nsreduce`` task has more than 50 parameters; the table below lists the defaults for the processing flag keywords---i.e., the keywords with logical values to indicate whether to perform an operation. 
The default order of the processing steps in this task is different that what is needed in this tutorial, so the switches will have to be set with care. 

.. csv-table:: **nsreduce Processing Flag Defaults**
   :header: "Flag", "Default", "Description"
   :widths: 12, 8, 50

   ``fl_cut``,         Yes, Cut images using F2CUT?
   ``fl_corner``,      Yes, Set the science arrays to zero?
   ``fl_process_cut``, Yes, Should cutting be performed before or after processing?
   ``fl_nsappwave``,   Yes, Insert approximate wavelength WCS keywords into header?
   ``fl_dark``,         No, Subtract dark image?
   ``fl_save_dark``,   Yes, Save processed dark files?
   ``fl_sky``,         Yes, Perform sky subtraction using skyimages?
   ``fl_flat``,        Yes, Apply flat-field correction?
   ``fl_vardq``,        No, Propagate VAR and DQ?

The *corner* processing is not applied to F2 data. 
The dark subtraction is sometimes more conveniently performed with **gemarith**. 
Flat-field correction should be performed for Arc, standard star, and science exposures. 
Sky subtraction should only be performed for science and standard star exposures. 

.. note::

   The **nsreduce** task makes assumptions about the order of processing steps (e.g., whether trimming the exposures to the illuminated area precedes or follows other steps) that are not entirely compatible with processing F2 data. The exposure preparation and dark subtraction will therefore be performed explicitly, within **gemarith** rather than **nsreduce**.

Darks
^^^^^
Begin by creating the **Dark MasterCals** corresponding to the exposure durations for all of the calibration and science exposures *except for flat-fields* (see :ref:`ls-bright-exp-summary`). 
The filenames will include a suffix that encodes the exposure duration in seconds (e.g., *MCdark_80.fits*).
Begin by setting task parameters and initializing for F2 processing. 

.. code-block:: python

   # Set the task parameters, beginning with the F2 keyword translation.
   gnirs.nsheaders.unlearn()
   gnirs.nsheaders('f2')
   f2.f2prepare.unlearn()
   prepPars = pars['f2prepPars']
   gemtools.gemcombine.unlearn()
   darkCombPars = pars['gemcombinePars']
   # Use the attributes of any grism configuration to select dark exposures
   qs = qd['JH']
   for t in [4,5,6,10,15,30,40,80]:
       MCdark = 'MCdark_' + str(t)
       qs['Texp'] = t
       darkFiles = fs.fileListQuery(dbFile, fs.createQuery('dark', qs), qs)
       if len(darkFiles) > 1:
           f2.f2prepare(flistToStr('', darkFiles), **prepPars)
           gemtools.gemcombine(flistToStr('p', darkFiles), MCdark, 
                               **darkCombPars)
           iraf.imdelete('pS*.fits')
       else:
           print 'No Dark images available for Texp: ', t

Flat-field
^^^^^^^^^^
Next create the **Flat MasterCal** for each grism from the GCAL flat exposures. 
Begin by setting task parameters. 

.. code-block:: python

   gemtools.gemexpr.unlearn()
   gemtools.gemextn.unlearn()
   gemtools.gemarith.unlearn()
   gemarithPars = pars['gemarithPars']
   f2.f2cut.unlearn()
   f2cutPars = pars['f2cutPars']
   gnirs.nsflat.unlearn()
   nsflatPars = pars['nsflatPars']

We are explicitly subtracting the **Dark MasterCal** and performing the cut, so these operations need not be done by the **nsflat** task. 
The response fitting should be done interactively. 
This operation will also create BPM reference files.
Use the ``spline3`` function with a high order (default is 20) to normalize the flat. 
For JH, order=49; for HK, order=37. 

.. note::

   The flat-field exposure ``S20140117S0187`` has an inconsistent exposure time (40s vs. 80s), and must be excluded in the observing log database. Set the ``use_me`` field to zero.

.. code-block:: python

   for g,qs in qd.iteritems():
       qs['Texp'] = qs['Texp_flat']
       MCdark = 'MCdark_' + str(qs['Texp'])
       flatFiles = fs.fileListQuery(dbFile, fs.createQuery('gcalFlat', qs), qs)
       if len(flatFiles) > 1:
           f2.f2prepare(flistToStr('', flatFiles), **prepPars)
           for f in flatFiles:
               gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f,
                                 **gemarithPars)
           f2.f2cut(flistToStr('dp', flatFiles), **f2cutPars)
           nsflatPars.update({
               'bpmfile': qs['MCbpm'],
               'flattitle': 'GCAL Flat: ' + g
           })
           gnirs.nsflat(flistToStr('cdp',flatFiles), flatfile=qs['MCflat'], 
                               **nsflatPars)
       else: 
           print 'Insufficient files to process for grating: ', g

   # Clean up.
   iraf.imdelete('pS*.fits,dpS*.fits,cdpS*.fits')

After trimming the images with **f2cut** the resulting **Flatfield MasterCals** will have dimensions:

* 1494x1254 for *JH*
* 1462x1598 for *HK*

Arcs
^^^^
Wavelength calibration begins with performing basic processing on the Arc exposures. 
The dates of the exposures are restricted to those of the science observations.
Note the application of the **Bad Pixel Mask MasterCal** which was derived above when creating the **Flat-field MasterCal**.

.. code-block:: python

   # Set task parameters.
   gnirs.nsreduce.unlearn()
   arcProcPars = pars['nsreducePars']
   # Arc name mapping
   with open('lamps.yml','r') as yf:
       lamps = yaml.load(yf)

   arcs = lamps['arcs']
   for g,qs in qd.iteritems():
       prepPars.update({'bpm':qs['MCbpm']})
       qs['Texp'] = qs['Texp_arc']
       MCdark = 'MCdark_' + str(int(qs['Texp']))
       arcFiles = fs.fileListQuery(dbFile, fs.createQuery('arc', qs), qs)
       arcs = lamps['arcs']
       if len(arcFiles) > 0:
           f2.f2prepare(flistToStr('', arcFiles), **prepPars)
           arcProcPars['flatimage'] = qs['MCflat']
           for f in arcFiles:
               gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f, 
                                 **gemarithPars)
               gnirs.nsreduce('dp'+f, outimages=arcs['dp'+f], **arcProcPars)
           # Clean up.
           iraf.imdelete('pS*.fits,dpS*.fits')

Image rectification and wavelength linearization depend upon the wavelength calibration, using the Ar arc lamp exposures [TBA: link to `wave-cal`]. 
The fit to the dispersion relation should be performed interactively, though prior experience shows that a fit to nearly 60 features yields an RMS near 0.5 with ``func=chebyshev`` and ``order=5``. 

.. code-block:: python

   gnirs.nswavelength.unlearn()
   nswavePars = pars['nswavePars']
   #for f in arcs.values():
   for f in ['Ar_JH_061','Ar_HK_067']:
       gnirs.nswavelength(f, **nswavePars)

For this exercise only one wavelength solution will be derived for each grism. 

Science Processing
------------------
With the **MasterCals** in place, proceed with basic processing of the standard star and science target exposures. 
First, fetch the meta-information for the targets:

.. code-block:: python

   # Target metadata
   with open('lsTargets.yml','r') as yf:
       targets = yaml.load(yf)

   targProcPars = copy.deepcopy(arcProcPars)
   targProcPars.update({
       'outimages':'',
       'fl_sky':'yes'
   })
   gnirs.nscombine.unlearn()
   targCombPars = pars['nscombinePars']

These exposures were obtained in an ``ABBA`` sequence of nods along the slit, with an offset of approximately 30 arcsec (standard stars) or 20 arcsec (science target) to enable sky subtraction; this will be performed by **nsreduce**. 
Since the targets are bright, we will use cross-correlation to determine fractional pixel shifts when combining the exposures. 

.. note::

   The interval between some exposures is too inconsistent for the target/sky pairings to be matched correctly. Set the ``skyrange`` parameter (in the ``targets.yml`` file) to a sufficiently large value to work around the problem. 

.. code-block:: python

   for t,tPars in targets.iteritems():
       print 'Processing target: ', t
       for g,qs in qd.iteritems():
           qs.update({'Object':t+'%'})
           targType = tPars['type']
           targFiles = fs.fileListQuery(dbFile, fs.createQuery(targType, qs), qs)
           if len(targFiles) > 0:
               targProcPars.update({
                   'skyrange': tPars['skyrange'],
                   'flatimage': qs['MCflat']
               })
               prepPars['bpm'] = qs['MCbpm']
               f2.f2prepare(flistToStr('', targFiles), **prepPars)
               MCdark = tPars['darkFile'][g]
               for f in targFiles:
                   gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f, 
                                     **gemarithPars)
               gnirs.nsreduce(flistToStr('dp', targFiles), **targProcPars)
               outFile = tPars['outFile'] + '_' + g
               if len(targFiles) > 1:
                   gnirs.nscombine(flistToStr('rdp', targFiles), 
                                              output=outFile, **targCombPars)
               else:
                   iraf.imrename(flistToStr('rdp', targFiles), outFile)

   # Clean up.
   iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

Geometric Transformation and Extraction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The geometric transformations will be derived from the wavelength calibration. 
A fit to the coordinates from the applicable arc is performed to derive the geometric transformation. Here a spline3 fit with ``xorder=yorder=4`` will suffice, although a number of points may need to be deleted for an optimum fit. 
Note that a correction for S--distortion is unnecessary for point-sources and modest sized nods. 
The 1-D spectra should be extracted from each rectified 2-D spectrogram interactively using a ``spline3`` function of order 5. 
It is possible to achieve a fit with RMS of 0.02 or less after removing errant points near the ends of the spectral trace. 
The extraction includes the "positive" and "negative" spectra, which are added together. 
Since the target is relatively bright, a trace (from the standard) is not necessary to extract the science spectrum. 

.. caution::

   The **nsextract** task will **fail** if the parameter ``fl_addvar=yes``.

.. note::

   The parameter *fl_findneg* in **nsextract** is set to ``yes`` look for the "negative" spectra, so the interactive extraction step actually happens twice. 

   In the HK band there are bad pixels in the spectra at the red end that must be fixed. 

.. code-block:: python

   gnirs.nsfitcoords.unlearn()
   nsfitcrdPars = pars['nsfitcrdPars']
   gnirs.nstransform.unlearn()
   nstransPars = pars['nstransPars']
   gnirs.nsextract.unlearn()
   targExtrPars = pars['nsextrPars']

   for t,tPars in targets.iteritems():
       print 'Processing target: ', t
       for g in qd:
           inFile = tPars['outFile'] + '_' + g
           arcFile = tPars['arcFile'][g]
           gnirs.nsfitcoords(inFile, lamptransf=arcFile, **nsfitcrdPars)
           gnirs.nstransform ('f'+inFile, **nstransPars)
           gnirs.nsextract('tf'+inFile, **targExtrPars)

   # Fix bad pixels 
   iraf.imreplace('xtfJ0126-5505_HK.fits[1][1450:1598]',4500.)
   iraf.imreplace('xtfHIP6546_HK.fits[1][1450:1598]',7400.)

   # Tidy up.
   iraf.imdele('J0126-5505*,fJ0126-5505*,tfJ0126-5505*')

Telluric Correction
^^^^^^^^^^^^^^^^^^^
A common next step is to derive the correction for telluric absorption for the science targets. 
Telluric standards are selected to have relatively few absorption features in their spectra (although there are often atomic H absorption lines), so that the broad and narrow absorption can be characterized. 
For this program the star HIP6546 (spectral type A2V) was observed at an airmass similar to the science target (see :ref:`ls-bright-exp-summary`), so it should suffer much the same telluric absorption. 
The star HD99216 (HIP55686, spectral type F5V) has fewer absorption lines and has a similar amount of telluric absorption. 
However, it was only observed with the JH grism. 

It is in general not possible to correct well in the region :math:`1.34-1.5\mu\mathrm{m}`, nor in the region :math:`1.80-19.5\mu\mathrm{m}`, because the absorption is so strong and because it is variable on short timescales. 
In addition, absorption features (such as H_I) in the telluric standard show up as bogus emission features in the corrected target spectrum. 
This latter effect may be ameliorated by manually removing the absorption features in the standards prior to deriving the telluric correction. 
For these reasons, the method for :ref:`telluric-corr`, discussed elsewhere in detail, can yield an unsatisfactory result. 
A much better approach is discussed in the next section. 

.. code-block:: python

   gnirs.nstelluric.unlearn()
   nstelluricPars = pars['nstelluricPars']
   target = 'xtfJ0126-5505'
   std = 'xtfHIP6546'

   for g in qd:
       inFile = target + '_' + g
       telFile = std + '_' + g
       gnirs.nstelluric(inFile, telFile, **nstelluricPars)

Flux Calibration
^^^^^^^^^^^^^^^^
The technique with the most potential for successfully correcting telluric absorption, and for removing the instrumental response function, is to remove the response function from the extracted spectra, using either a library of model atmospheres or a library of flux standards. 
The `IRTF Spectral Library <http://irtfweb.ifa.hawaii.edu/~spex/IRTF_Spectral_Library/>`_ is a collection of optical/NIR stellar spectra from 0.8--5.0 um that is well suited to this purpose. 
The procedure is the following: 

1. Identify the spectrum from the IR spectral library that most closely matches the standard used for your program's observations.

2. Re-grid the library spectrum to that of the extracted standard (see the regrid.py program for an example).

3. Compute ratio of the standard to the re-gridded library spectrum. 

4. Fit the ratio with a low-order polynomial, rejecting all the spectral features and residual telluric features. This is the approximate sensitivity function.

.. figure:: /_static/FV5_fit.* 
   :width: 90 %

   Residual of the fit to the ratio of an FV5 library standard to the standard star HD218804. Note the rejection or deletion of stellar features and residual telluric absorption. 

5. Multiply the extracted spectra for the standard and the target by the sensitivity function. 

.. figure:: /_static/J0126-5505_JH_cal.* 
   :width: 90 %

   Target J0126-5505 in JH-band after flux calibration, but before correction for telluric absorption. 

6. Perform the telluric correction on the calibrated spectra.


