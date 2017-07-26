.. _f2-proc-faint-ls:

============================================
Reduction of Faint, J-band Long-Slit Spectra
============================================
This tutorial will use observations from program GS-2014B-Q-17 (PI:Leggett), longslit spectra of the faint Y1 star WISE J035000.32-565830.2, obtained between 2014-Nov-07 and 2014-Dec-04. 
The spectra were obtained with the ``4pix-slit`` (0.72 arcsec) slit and the ``JH`` grism at :math:`1.4\mu m`. 
Telluric standards were included in the observing plan, as were Ar comparison arcs. 
Leggett, et al. (2016; [L16]_) describe the data reduction procedures they followed, which are very similar to those described below. 

.. contents:: 
   :depth: 3

Tutorials for other configurations are listed below:

* :ref:`f2-proc-dith-img`
* **[Img f2-proc-offset-img]**
* :ref:`f2-proc-bright-ls`

Retrieve & Organize Data
------------------------
The first step is to retrieve the data from the Gemini Observatory Archive (see :ref:`archive-search`). 
We will retrieve exposures within about a month of the target exposures in 2014 Nov-Dec. 
You may search the `GOA <https://archive.gemini.edu/searchform>`_ yourself, or instead just cut-and-paste the following direct URL in your browser. 

.. code-block:: html

   # longslit spectra of WISE J0350:
   https://archive.gemini.edu/searchform/cols=CTOWFMDELQ/GS-2014B-Q-17/notengineering/F2/NOTAO/20141015-20141231/NotFail/spectroscopy

After retrieving the science data, click the **Load Associated Calibrations** tab on the search results page and download the associated bias and flat-field exposures. 
Unpack all of them in a subdirectory of your working directory named ``/raw``. 
Be sure to uncompress the files. 
See :ref:`retrieve-data` for details. 

.. _ls-faint-exp-summary:

Exposure Summary
^^^^^^^^^^^^^^^^
The data contain exposures of a specific science target, telluric standards, and dayCal calibrations that are summarized in the table below. 
*It is important to review the observing log database to understand how to approach the data processing.*
All exposures were obtained with ``ReadMode = Bright``.

.. csv-table:: **Exposure Summmary**
   :header: "Target", T_exp, N_exp, Date
   :widths: 20, 10, 8, 25

   WISE 0350-56, 300,  4, 2014-Nov-05 (not used)
               , 300, 52, 2014-Nov-07
               , 300,  6, 2014-Nov-13 (not used)
               , 300, 16, 2014-Dec-04
   HD 13517 (F3V), 5,  8, 2014-Nov-05 (not used)
               ,   5,  8, 2014-Nov-07
   HD 17813 (F2V), 5,  8, 2014-Nov-13 (not used)
   HD 30526 (F7V), 5,  4, 2014-Nov-07
   HD 36636 (F3V), 5,  4, 2014-Dec-04
   Dark,         300, 24, 2014-Nov-08 --- 2014-Dec-13
       ,          15, 27, 2014-Nov-08 --- 2014-Dec-13
       ,           5, 27, 2014-Nov-08 --- 2014-Dec-13
       ,           4, 21, 2014-Nov-08 --- 2014-Dec-13
   GCAL Flat,      4,  9, 2014-Nov-05 --- 2014-Dec-15
   GCAL Ar Arc,   15,  5, 2014-Nov-05 --- 2014-Dec-12

The spectral types of the telluric standards are noted above: this information is necessary to perform the flux calibration. 
There are other science, calibration, and telluric standards exposures on different dates, but we select the exposures that were used by Leggett et al. (2016; [L16]_). 

Processing Preparation
^^^^^^^^^^^^^^^^^^^^^^
Reference Files
:::::::::::::::
The following essential **MasterCals** will be constructed in this tutorial: 

* Dark
* Flat-field (from the GCAL source)
* Wavelength calibration (from Ar comparison arcs)
* Telluric standards
* Flux calibration from a `model atmosphere library <http://irtfweb.ifa.hawaii.edu/~spex/IRTF_Spectral_Library/index_files/F.html>`_

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

* Download: :download:`f2_lsFaintProc.py <../pyTools/f2_lsFaintProc.py>` 

You may find it useful to download the above script to follow this tutorial in detail, and use it as the basis for reducing other longslit observations. 

Configuration Parameters
::::::::::::::::::::::::
A large number of configuration parameters are used to customize the processing for an observing run. 
See :ref:`config-files` for details. 
These parameter--value pairs are represented in the **python** session as dictionaries. 
Download the following files to your work directory, and customize them as necessary for the observing run.

.. csv-table:: **Configuration Files**
   :header: File, Contents
   :widths: 20, 40

   :download:`lsTaskPars.yml <../pyTools/lsTaskPars.yml>`, IRAF task parameters
   :download:`lsFaintObsConfig.yml <../pyTools/lsFaintObsConfig.yml>`, Observing configurations
   :download:`lsFaintLamps.yml <../pyTools/lsFaintLamps.yml>`, Arc exposure name mapping
   :download:`lsFaintStdStar.yml <../pyTools/lsFaintStdStar.yml>`, Standard star attributes
   :download:`lsFaintTargets.yml <../pyTools/lsFaintTargets.yml>`, Science target attributes
   :download:`Ar_NIR_lowres.txt <../calib/Ar_NIR_lowres.txt>`, Ar line list optimized for medium-resolution grisms

The PyRAF Session
-----------------
After starting your PyRAF session, load the necessary packages. Note that the order of import matters as there are some dependencies between packages. 

.. code-block:: python

   import copy
   import glob
   import yaml
   from pyraf import iraf
   from pyraf.iraf import gemini
   from pyraf.iraf import gemtools, gnirs, niri
   from pyraf.iraf import f2
   import fileSelect as fs

The next order of business is to define a few global variables for processing. 
Note that it is *essential** to create an observing log before proceeding.

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
   with open('lsFaintObsConfig.yml','r') as yf:
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
Flat-field correction should only be performed for Arc, standard star, and science exposures.
Sky subtraction should only be performed for science and standard star exposures. 

.. note::

   The **nsreduce** task makes assumptions about the order of processing steps (e.g., whether trimming the exposures to the illuminated area precedes or follows other steps) that are not entirely compatible with processing F2 data. It is (slightly) more convenient to prepare the exposures and perform dark subtraction explicitly with **gemarith** rather than **nsreduce**.

Darks
^^^^^
Start by creating the **Dark MasterCals** for each exposure duration that was used for science or calibration (see :ref:`ls-faint-exp-summary`). The output filenames will include a suffix that encodes the exposure duration in seconds (e.g., *MCdark_300.fits*). 

.. note::

   Be sure to exclude from the processing below any combined darks that were obtained from the Archive (with a file suffix of ``*_dark.fits``) by setting the ``use_me`` field in the database to zero.

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
   for t in [300,15,5,4]:
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
Now create the **Flat-field MasterCal** files from the GCAL flat exposures. 
Begin by setting task parameters. 

.. code-block:: python

   # Match any date for the exposures.
   qs.update({'DateObs':'*'})
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
Use the ``spline3`` function with a small order (perhaps 3) to normalize the flat. 

.. code-block:: python

   # There is only one exposure duration for flats.
   qs['Texp'] = qs['Texp_flat']
   MCdark = 'MCdark_' + str(qs['Texp'])
   flatFiles = fs.fileListQuery(dbFile, fs.createQuery('gcalFlat', qs), qs)
   if len(flatFiles) > 1:
       f2.f2prepare(flistToStr('', flatFiles), **prepPars)
       for f in flatFiles:
           gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f, **gemarithPars)
       f2.f2cut(flistToStr('dp', flatFiles), **f2cutPars)
       # Now sum the flats and remove the response
       nsflatPars.update({
           'bpmfile': qs['MCbpm'],
           'flattitle': 'GCAL Flat: JH'
       })
       gnirs.nsflat(flistToStr('cdp',flatFiles), flatfile=qs['MCflat'], 
                               **nsflatPars)
   else: 
       print 'Insufficient files to process for grating: JH'

   # Clean up.
   iraf.imdelete('pS*.fits,dpS*.fits,cdpS*.fits')

The resulting **Flatfield MasterCal** will have dimensions: :math:`1494\times1254`. 

Arcs
^^^^
Wavelength calibration begins with performing basic processing on the Arc exposures. 
The dates of the exposures are restricted to those of the 3 epochs of science observations (see :ref:`lsFaint-science-exp`).
Note the application of the **Bad Pixel Mask MasterCal** which was derived above when creating the **Flat-field MasterCal**, and will be used in all subsequent processing.
Looping over grism configurations is not really necessary, since this dataset uses only the ``JH`` grism, but it handles the more general case of multiple grisms. 

.. code-block:: python

   # Set task parameters.
   gnirs.nsreduce.unlearn()
   arcProcPars = pars['nsreducePars']
   # Arc name mapping
   with open('lsFaintLamps.yml','r') as yf:
       lamps = yaml.load(yf)

   arcs = lamps['arcs']
   for g,qs in qd.iteritems():
       prepPars.update({'bpm':qs['MCbpm']})
       qs['Texp'] = qs['Texp_arc']
       MCdark = 'MCdark_' + str(int(qs['Texp']))
       #arcFiles = fs.fileListQuery(dbFile, fs.createQuery('arc', qs), qs)
       arcFiles = arcs.keys()
       if len(arcFiles) > 0:
           f2.f2prepare(flistToStr('', arcFiles), **prepPars)
           arcProcPars['flatimage'] = qs['MCflat']
           for f in arcFiles:
               gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f, **gemarithPars)
               gnirs.nsreduce('dp'+f, outimages=arcs[f], **arcProcPars)
           # Clean up.
           iraf.imdelete('pS*.fits,dpS*.fits')

Image rectification and wavelength linearization depend upon the wavelength calibration, using the Ar arc lamp exposures [TBA: link to `wave-cal`]. 
The fit to the dispersion relation should be performed interactively, though prior experience shows that a fit to nearly 60 features yields an RMS of about 0.6 near the center of the slit with ``func=chebyshev`` and ``order=5``. 

.. code-block:: python

   gnirs.nswavelength.unlearn()
   nswavePars = pars['nswavePars']   
   for f in arcs.values():
       gnirs.nswavelength(f, **nswavePars)

The wavelength solution nearest in time will be used for the science exposures. 

Science Processing
------------------
With the **MasterCals** in place, proceed with basic processing of the standard star and science target exposures. 
Unlike the :ref:`f2-proc-bright-ls`, we will process the standard star exposures separately from the science, owing to some peculiarities of the observation epochs and some special processing for the science target. 

Standard Star
^^^^^^^^^^^^^
First, fetch the meta-information for the standard stars, and set the task parameters:

.. code-block:: python

   # Standard star metadata
   with open('lsFaintStdStar.yml','r') as yf:
       stdStar = yaml.load(yf)

   stdProcPars = copy.deepcopy(arcProcPars)
   stdProcPars.update({
       'outimages':'',
       'fl_sky':'yes'
   })
   gnirs.nscombine.unlearn()
   stdCombPars = pars['nscombinePars']

These exposures were obtained in an ``ABBA`` sequence of nods along the slit, with an offset of approximately 16 arcsec to enable pair-wise sky subtraction; this will be performed by **nsreduce**. 
Since the standards are bright, we will use cross-correlation to determine fractional pixel shifts when combining the exposures. 

.. note::

   The interval between exposure start times for the star HD 36636 is somewhat irregular. Therefore the ``skyrange`` interval is set to 90 s in the configuration file ``lsFaintStdStar.yml``. 

.. code-block:: python

   for t,tPars in stdStar.iteritems():
       qs.update({
           'Object':t+'%',
           'DateObs':tPars['date']
       })
       print 'Processing star: ', t
       stdFiles = fs.fileListQuery(dbFile, fs.createQuery(tPars['type'], qs), qs)
       if len(stdFiles) > 0:
           stdProcPars.update({
               'skyrange': tPars['skyrange'],
               'flatimage': qs['MCflat']
           })
           prepPars['bpm'] = qs['MCbpm']
           MCdark = tPars['darkFile']['JH']
           f2.f2prepare(flistToStr('', stdFiles), **prepPars)
           for f in stdFiles:
               gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f, **gemarithPars)
           gnirs.nsreduce(flistToStr('dp', stdFiles), **stdProcPars)
           outFile = tPars['outFile']
           if len(stdFiles) > 1:
               gnirs.nscombine(flistToStr('rdp', stdFiles), 
                           output=outFile, **stdCombPars)
           else:
               iraf.imrename(flistToStr('rdp', stdFiles), outFile)

   # Clean up.
   iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

Std: Geometric Transformation and Extraction
::::::::::::::::::::::::::::::::::::::::::::
The geometric transformations will be derived from the wavelength calibration. 
Note that a correction for S--distortion is unnecessary for point-sources and modest sized nods. 
The transformation should be done interactively, and a ``spline3`` function of ``xorder 4`` and ``yorder=5` should yield a fit RMS <0.8 (you may wish to delete several deviant points during the fitting). 
The 1-D spectra will be extracted from each rectified 2-D spectrogram interactively; using a ``spline3`` function of ``order 5`` should yield a fit RMS <0.05. 
The extraction includes the "positive" and "negative" spectra, which are added together. 
Since the target is relatively bright, a trace (from the standard) is not necessary to extract the science spectrum. 
Finally, extract each spectrum and remove the spurious net signal in the first 160 pixels, or shortward of :math:`\sim10.2 \mu \mathrm{m}`. 

.. caution::

   The **nsextract** task will **fail** if the parameter ``fl_addvar=yes``.

.. note::

   The parameter *fl_findneg* in **nsextract** is set to ``yes`` look for the "negative" spectra, so the interactive extraction step actually happens twice. 

.. code-block:: python

   gnirs.nsfitcoords.unlearn()
   nsfitcrdPars = pars['nsfitcrdPars']
   gnirs.nstransform.unlearn()
   nstransPars = pars['nstransPars']
   gnirs.nsextract.unlearn()
   stdExtrPars = pars['nsextrPars']

   for t,sPars in stdStar.iteritems():
       print 'Processing target: ', t
       inFile = sPars['outFile']
       arcFile = sPars['arcFile']['JH']
       gnirs.nsfitcoords(inFile, lamptransf=arcFile, **nsfitcrdPars)
       gnirs.nstransform ('f'+inFile, **nstransPars)
       gnirs.nsextract('tf'+inFile, **stdExtrPars)
       #iraf.imreplace('xtf'+inFile+'.fits[1][1:160]', 0.)

   # Clean up.
   iraf.imdelete('fHD*.fits,tfHD**.fits')

Some fix to the bad values at the ends of the extracted spectra will simplify the telluric correction. 
These spectra can now be used for the telluric correction of the science spectra. 

.. _lsFaint-science-exp:

Science Exposures
^^^^^^^^^^^^^^^^^
The processing for the science target exposures is similar to that for the telluric standards, except for the combination and extraction steps. 
There were two observing nights when data of sufficiently high quality were obtained. 
Since the target is extremely faint, use integral pixel shifts determined from the WCS in the headers, rather than cross-correlation of the spectrum, to combine the exposures. 

.. code-block:: python

   sciProcPars = copy.deepcopy(stdProcPars)
   sciCombPars = pars['nscombinePars']
   # Optimize for a very faint target
   sciCombPars.update({
       'tolerance':1.0,
       'fl_cross':'no',
       'fl_shiftint':'yes'
   })
   # Target metadata
   with open('lsFaintTargets.yml','r') as yf:
       epochs = yaml.load(yf)

.. note::

   On 2014-11-07 there were two consecutive epochs, separated by ``partnerCal`` arc and flat exposures, which introduced a break in the observing cadence. The seeing seems to have changed between these epochs. One either has to write idiosyncratic logic to discover the discontinuity, or (as below) note the break in the observing log and build separate lists of files to combine. 

.. code-block:: python

   qs = qd['JH']
   qs['Object'] = 'WISE 0350-56' + '%'
   for ep,sPars in epochs.iteritems():
       qs['DateObs'] = sPars['date']
       sPars['sf'] = fs.fileListQuery(dbFile, 
                                     fs.createQuery(sPars['type'], qs), qs)

   # Note from the obsLog database the boundary between two consecutive 
   # observing epochs on 2014-11-07
   imgEnd = 'S20141107S0234'
   sciFiles = copy.deepcopy(epochs['ep1']['sf'])
   epochs['ep1']['sf'] = sciFiles[:sciFiles.index(imgEnd)+1]
   epochs['ep2']['sf'] = sciFiles[sciFiles.index(imgEnd)+1:]

Proceed with basic processing of the exposures: sky-subtract within each observing sequence, and combine exposures taken within the same epoch. 
Since the target signal is so weak, clip the combined images of pixel values that deviate substantially from the expected extrema. 

.. note::

   The duration of the science exposures is 300 s, and the difference between sequential exposure start times (:math:`\Delta t`) is several seconds longer than that. Since the default :math:`\Delta t` (within which source--sky pairs are searched) is 90 s, be sure that the parameter ``nsreduce.skyrange`` exceeds 300 by a sufficient margin. 

.. code-block:: python

   for ep,sPars in epochs.iteritems():
       sciFiles = sPars['sf']
       if len(sciFiles) > 0:
           MCdark = sPars['MCdark']
           f2.f2prepare(flistToStr('', sciFiles), **prepPars)
           for f in sciFiles:
               gemtools.gemarith('p'+f, '-', MCdark, 'dp'+f, 
                                 **gemarithPars)
           gnirs.nsreduce(flistToStr('dp', sciFiles), **sciProcPars)
           outFile = sPars['outFile']
           if len(sciFiles) > 1:
               gnirs.nscombine(flistToStr('rdp', sciFiles), 
                               output=outFile, **sciCombPars)
           else: 
               iraf.imrename(flistToStr('rdp', sciFiles), outFile)

   # Clip the images of extreme spurious values
   iraf.imreplace(outFile+'.fits[1]',0.,upper=-20.)
   iraf.imreplace(outFile+'.fits[1]',0.,lower=30.)

   # Clean up.
   iraf.imdelete('pS*.fits,dpS*.fits,rdpS*.fits')

Target Extraction
:::::::::::::::::
Like the standard stars, the exposures of the science target were obtained in a ``ABBA`` sequence of nods along the slit, with an offset of approximately 20 arcsec. 
The standard star was centered at a different place on the slit, so that trace will not help to extract the science spectrum. 

Note: the signal on the science spectrogram appears between rows 
100:160, 400:490, and 880:940; 
the extraction windows are 15 pix wide at approximately 837, 948, 1058. 
Perform the extraction interactively, and delete trace points that fall outside the region with signal from the target. 
The best data are from epoch 2, so extract that one first and then use it to trace the spectrum in the other epochs. 

.. code-block:: python

   sciExtrPars = copy.deepcopy(stdExtrPars)
   sciExtrPars.update({
       'line':425,
       'upper':10,
       'lower':-10,
       'func': 'legendre',
       'background':'median'
   })
   gnirs.nstelluric.unlearn()
   nstelluricPars = pars['nstelluricPars']

   for ep in ['ep2','ep1','ep3']:
       sPars = epochs[ep]
       inFile = sPars['outFile']
       arcFile = sPars['arcFile']
       gnirs.nsfitcoords(inFile, lamptransf=arcFile, **nsfitcrdPars)
       gnirs.nstransform ('f'+inFile, **nstransPars)
       sciExtrPars['trace'] = sPars['trace']
       gnirs.nsextract('tf'+inFile, **sciExtrPars)


Telluric Correction
:::::::::::::::::::
A common next step is to derive the correction for telluric absorption for the science targets. 
Telluric standards are selected to have relatively few absorption features in their spectra (although there are often atomic H absorption lines), so that the broad and narrow absorption can be characterized. 
For this program the standard stars HD_13517, HD_30526 and HD_36636 were observed (see :ref:`ls-faint-exp-summary`). 
HD_13517 has the strongest signal, and may yield the best correction. 

It is in general not possible to correct well in the region :math:`1.34-1.5\mu\mathrm{m}`, nor in the region :math:`1.80-19.5\mu\mathrm{m}`, because the absorption is so strong and because it is variable on short timescales. 
In addition, absorption features (such as H_I) in the telluric standard show up as bogus emission features in the corrected target spectrum. 
This latter effect may be ameliorated by manually removing the absorption features in the standards prior to deriving the telluric correction. 
For these reasons, the method for :ref:`telluric-corr`, discussed elsewhere in detail, can yield an unsatisfactory result. 
A much better approach is discussed in the next section. 

.. code-block:: python

   gnirs.nstelluric.unlearn()
   nstelluricPars = pars['nstelluricPars']

   for ep,sPars in epochs.iteritems():
       inFile = 'xtf'+sPars['outFile']
       telFile = sPars['telluric']
       gnirs.nstelluric(inFile, telFile, **nstelluricPars)

Flux Calibration
^^^^^^^^^^^^^^^^
The technique with the most potential for successfully correcting telluric absorption, and for removing the instrumental response function, is to remove the response function from the extracted spectra, using either a library of model atmospheres or a library of flux standards. 
The `IRTF Spectral Library <http://irtfweb.ifa.hawaii.edu/~spex/IRTF_Spectral_Library/>`_ is a collection of optical/NIR stellar spectra from 0.8--5.0 um that is well suited to this purpose. 
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

