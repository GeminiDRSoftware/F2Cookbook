.. _f2-proc-dith-img:

============================
Reduction of Dithered Images
============================
This tutorial will use observations from program GS-2013B-Q-15 (PI:Leggett), NIR photometry of the faint T-dwarf star WISE J041358.14-475039.3, obtained on 2013-Nov-21. 
Images of this sparse field were obtained in the *Y,J,H,Ks* bands using a dither sequence; :term:`dayCal` darks and :term:`GCAL` flats were obtained as well. 
Leggett, et al. (2015; [L15]_) briefly describe the data reduction procedures they followed, which are similar to those described below. 

.. contents:: 
   :depth: 3

Tutorials for other configurations are listed below:

* **[Img offset-sky]**
* :ref:`f2-proc-faint-ls`
* :ref:`f2-proc-bright-ls`

Retrieve & Organize Data
------------------------
The first step is to retrieve the data from the Gemini Observatory Archive (see :ref:`archive-search`). 
We will retrieve exposures within about a month of the target exposures in 2013 Nov 21. 
You may search the `GOA <https://archive.gemini.edu/searchform>`_ yourself, or instead just cut-and-paste the following direct URL in your browser. 

.. code-block:: html

   # images of the WISE 0413-4750 target field:
   https://archive.gemini.edu/searchform/GS-2013B-Q-15-39/cols=CTOWEQ/NOTAO/notengineering/F2/imaging/20130101-20150701/NotFail#

After retrieving the science data, click the **Load Associated Calibrations** tab on the search results page and download the associated bias and flat-field exposures. 

.. note::

   Unfortunately, GOA internal limits prevent a few applicable *Ks--* band flat-field exposures from being selected with the above query. The query below will select additional exposures, which should also be downloaded.

.. code-block:: html

   # Additional Ks-band flats:
   https://archive.gemini.edu/searchform/exposure_time=8/cols=CTOWFEQ/NOTAO/filter=Ks/notengineering/F2/imaging/20131101-20140301/NotFail

Unpack all of them in a subdirectory of your working directory (assumed to be named ``/raw`` in this tutorial). 
Be sure to uncompress the files. 
See :ref:`retrieve-data` for details. 

Exposure Summary
^^^^^^^^^^^^^^^^
The data contain exposures of a specific science target and :term:`dayCal` calibrations; see the table below for a summary. 
All exposures were obtained with ``ReadMode = Bright``. 
The science exposures were obtained in a :math:`3\times3` spatial dither pattern, with a spacing of about 15 arcsec in each direction from the initial alignment (see :ref:`ir-background`). 

.. _img-exp-summary:

.. csv-table:: **Exposure Summmary**
   :header: Target, Filter, T_exp, N_exp
   :widths: 18, 8, 8, 15

   WISE 0413-4750, Y,   120,  9
                 , J,    60,  9
                 , H,    15, 72
                 , Ks,   15, 72
   Dark,            ,   120, 10
       ,            ,    60, 21
       ,            ,    20, 20
       ,            ,    15, 10
       ,            ,     8, 25
       ,            ,     3, 13
   GCAL Flat,      Y,    20, 4 (on); 6 (off)
                 , J,    60, 4 (on); 6 (off)
                 , H,     3, 4 (on); 6 (off)
                 , Ks,    8, 12 (off)

The GCAL exposures list those for :term:`Lamps-On` and :term:`Lamps-Off` separately. 
The exposure durations above are noted in the ``obsConfig.yml`` file. 
We will use calibration exposures obtained within a few days of the observations. 

Processing Preparation
^^^^^^^^^^^^^^^^^^^^^^
Reference Files
:::::::::::::::
The required **MasterCals** that will be constructed in this tutorial are: 

* :term:`Darks` (for each exposure duration)
* Static :term:`Bad Pixel Mask`
* Flat-fields for each filter
* Sky level for each filter and dither sequence

Software
::::::::
You must create an observing log database of the exposures in the ``./raw`` subdirectory. 
Download: :download:`obslog.py <../pyTools/obslog.py>` to the ``./raw`` subdirectory, and execute it from the unix prompt.

.. code-block:: bash

   python obslog.py obsLog.sqlite3

The name of the file is your choice, but the extension ``.sqlite3`` is recognized by the `SQLite browser <http://sqlitebrowser.org/>`_. 
It is important to review the observing log to understand how the observations were obtained. 
See :ref:`gen-obslog` for details.

Also retrieve the python file selection module, which includes template SQL statements for selecting files, and functions for specifying metadata on which to perform selections. 

* Download: :download:`fileSelect.py <../pyTools/fileSelect.py>`

Place this module in your work directory; it is used by the reduction script (below). 
You can perform all of the processing steps for this tutorial by downloading the Longslit Tutorial **python** script. 

* Download: :download:`f2_ImgProc.py <../pyTools/f2_ImgProc.py>` 

You may find it useful to download the script to follow this tutorial in detail, and use it as the basis for reducing other longslit observations. 
Finally, download two `YAML <https://martin-thoma.com/configuration-files-in-python/#yaml>`_ files of configuration parameters which will be used throughout the processing: 

* Download IRAF task parameters: :download:`imgTaskPars.yml <../pyTools/imgTaskPars.yml>` 
* Download observing configurations: :download:`imgObsConfig.yml <../pyTools/imgObsConfig.yml>` 

The PyRAF Session
-----------------
After starting your PyRAF session, load the necessary packages. Note that the order of import matters as there are some dependencies between packages. 

.. code-block:: python

   import copy
   import glob
   from pyraf import iraf
   from pyraf.iraf import gemini
   from pyraf.iraf import f2
   from pyraf.iraf import gemtools, gnirs, niri
   import yaml
   import fileSelect as fs

First, a few global variables are needed for processing. 
Note that it is *essential* to create an observing log before proceeding with this tutorial.

.. code-block:: python

   # Path to raw exposures
   rawpath = './raw/'
   # Observing log database
   dbFile = rawpath + 'obsLog.sqlite3'
   iraf.imtype = 'fits'

Configuration Parameters
^^^^^^^^^^^^^^^^^^^^^^^^
A large number of configuration parameters are used to customize the processing for an observing run. 
These include IRAF task parameters; see :ref:`config-files` for details. 
These parameter--value pairs are represented in the **python** session as dictionaries. 
If you have not already done so, download the following files to your work directory, and customize them as necessary for the observing run.
Then load the configurations into your PyRAF session:

.. code-block:: python

   # IRAF task parameters
   with open('imgTaskPars.yml','r') as yf:
       pars = yaml.load(yf)

   # Observing configurations to support exposure queries
   with open('imgObsConfig.yml','r') as yf:
       qd = yaml.load(yf)

The contents of these dictionaries are updated as necessary throughout the course of data reduction processing to select relevant exposures and to specify task parameters. 

Processing Basics
^^^^^^^^^^^^^^^^^
In the remainder of this tutorial, the general approach to processing is: 

* use python dictionaries to contain the processing task parameters (either read from **.yml** files or a modified copy of a dictionary from another invocation)
* construct a query to obtain a list of files to process, and create a template for output filenames
* execute the task(s) over the file lists

It is handy to have a small utility routine to create an IRAF-style comma-separated list of filenames (e.g., *file1.fits,file2.fits,...*) from a **python** ``list`` of input filenames. 

.. code-block:: python

   def flistToStr(prefix, fileList):
       '''Create a comma-separated string of file names (with a prefix) 
          from a python list.
       '''
       return ','.join(str(prefix+x) for x in fileList)

The number of files to process can sometimes be unwieldy (for IRAF), so it is necessary to have a routine to chunk up a large list of files into manageable pieces. 
Note from the observing log that the science exposures are dithered, with the dither pattern repeated every 9 exposures. 
Partitioning the file lists to this size also enables more fine-grained tracking of temporal changes in the sky emission. 

.. code-block:: python

   ditherCycle = 9
   def chunks(inList, chunkSize):
       '''Return a list generator for chunks of a lengthy list.
       '''
       n = max(1, chunkSize)
       return (inList[i:i+n] for i in xrange(0, len(inList), n))

Calibration Processing
----------------------
The next steps will create the necessary **MasterCal** reference files that are used to calibrate the science exposures. 
Files are selected by matching specific exposure metadata in the observing log database (see :ref:`dr-keywords`). 

Configuration of nireduce
^^^^^^^^^^^^^^^^^^^^^^^^^
The **nsreduce** task has several parameters; the table below lists the defaults for the processing flags---i.e., the parameters with logical values to indicate whether to perform an operation. 

.. csv-table:: **nireduce Processing Flag Defaults**
   :header: "Flag", "Default", "Description"
   :widths: 12, 8, 50

   ``fl_autosky``,     Yes, Determine constant sky level to restore?
   ``fl_dark``,         No, Subtract dark image?
   ``fl_flat``,        Yes, Apply flat-field correction?
   ``fl_scalesky``,    Yes, Scale the sky image to input image?
   ``fl_sky``,         Yes, Perform sky subtraction using skyimage?
   ``fl_vardq``,       Yes, Propagate VAR and DQ extensions?

The default parameter values need to be chosen carefully, as the order of operations performed by the task is not consistent with the order adopted in this tutorial. 
This means **nireduce** will be invoked multiple times, with different processing flag settings, to accomplish the processing steps in the needed order.

Flat-fields
^^^^^^^^^^^
The first step is to create the **Flat-field MasterCal** files from the GCAL flat-field lamp exposures for all filters *except for Ks* (explained below). 
The *lamps-off* exposures are used to subtract the (instrument) thermal background from the flat exposures. 
Begin by initializing the **gemini.gnirs** package for **F2** processing, and fetching some task parameters.

.. code-block:: python

   gnirs.nsheaders.unlearn()
   gnirs.nsheaders('f2')
   f2.f2prepare.unlearn()
   prepPars = pars['f2prepPars']
   gemtools.gemexpr.unlearn()
   gemtools.gemextn.unlearn()
   niri.niflat.unlearn()
   niflatPars = pars['niflatPars']

The short-dark exposures are only used to derive the static **Bad-Pixel Mask MasterCal** for each filter. 
Prepare the exposures, giving them a unique prefix so they aren't deleted when intermediate files are deleted: 

.. code-block:: python

   # Choose any observing configuration to enable file selection
   qs = qd['Y']
   qs['Texp'] = 3
   # The following generates an SQL template to contain the list of 
   # short-dark exposures to process
   SQL = fs.createQuery('dark', qs)
   shortDarks = fs.fileListQuery(dbFile, SQL, qs)
   prepPars['outprefix'] = 'd'
   f2.f2prepare(flistToStr('',shortDarks), **prepPars)
   prepPars['outprefix'] = 'p'

Now create the GCAL flat-field and BPM for all filters except Ks. 
Recall that the **niri.niflat** task combines and subtracts :term:`Lamps-Off` exposures from the combined :term:`Lamps-On` exposures. 

.. code-block:: python

   for filt in ['Y','J','H']:
       qs = qd[filt]
       qs['Texp'] = qs['Texp_flat']
       lampsOn = fs.fileListQuery(dbFile, fs.createQuery('lampsOn', qs), qs)
       lampsOff = fs.fileListQuery(dbFile, fs.createQuery('lampsOff', qs), qs)
       calFiles = lampsOn + lampsOff
       if len(lampsOn) > 1 and len(lampsOff) > 1:
           f2.f2prepare(flistToStr('',calFiles), **prepPars)
           niflatPars.update({
               'darks':flistToStr('d',shortDarks),
               'lampsoff':flistToStr('p',lampsOff)
           })
           niri.niflat(flistToStr('p',lampsOn), flatfile=qs['GCALflat'],
                                   **niflatPars)
       else:
           print 'Insufficient input files for filter: ', filt
       iraf.imdelete('pS*.fits')

Darks
^^^^^
Now create the **Dark MasterCals** for each exposure duration that was used for science or calibration (see :ref:`img-exp-summary`), using exposures taken within a month or so of the target observations. 
Also make use of the **MasterCal BPM** files to flag bad pixels in the input expossures. 
The output filenames will include a suffix that encodes the exposure duration in seconds (e.g., ``MCdark_120.fits``). 

.. code-block:: python

   gemtools.gemcombine.unlearn()
   darkCombPars = pars['gemcombinePars']
   prepPars['bpm'] = 'GCALflat_J_bpm.pl'
   qs = qd['J']
   qs['dateObs'] = '2013-10-20:2013-11-30'
   # Iterate over exposure times used in science+calibration exposures
   for t in [120, 60, 15, 8]:
       qs['Texp'] = t
       MCdark = 'MCdark_' + str(int(t))
       darkFiles = fs.fileListQuery(dbFile, fs.createQuery('dark', qs), qs)
       if len(darkFiles) > 1:
           f2.f2prepare(flistToStr('', darkFiles), **prepPars)
           gemtools.gemcombine(flistToStr('p', darkFiles), MCdark, 
                               **darkCombPars)
       iraf.imdelete('pS*.fits')

Ks Flat-field
^^^^^^^^^^^^^
As noted above, the *Ks--* band flat-field is special: it will be constructed from dark-subtracted *Lamps-Off* exposures. 
Thermal emission from the instrument (specifically, the GCAL shutter) is substantial in the *Ks--* band. 
Therefore no *Lamps-On* dayCal exposures are obtained (or needed); the *Lamps-Off* exposures provide sufficient illumination. 

Use the *J--* band static BPM as an approximate *Ks--* band BPM.

.. code-block:: python

   filt = 'Ks'
   qs = qd[filt]
   GCALflat = 'GCALflat_' + filt
   qs['MCdark'] = 'MCdark_' + str(int(qs['Texp_flat']))
   prepPars['bpm'] = qs['MCbpm']
   flatCombPars = copy.deepcopy(darkCombPars)
   flatCombPars.update({
       'statsec':'[350:1750,350:1750]',
       'bpmfile':qs['MCbpm']
   })
   gemtools.gemarith.unlearn()
   gemarithPars = pars['gemarithPars']
   gemtools.gemexpr.unlearn()
   gemexprPars = pars['gemexprPars']
   flatComb = qs['GCALflat'] + '_comb'

.. note::

   The Ks-band thermal emission from the GCAL shutter depends upon the temperature at the time of the exposure, and includes some spatial structure. Therefore the distribution of emission is not necessarily consistent, except for sequential exposures. So it is best to combine *lamps-off* exposures from a single day. 

.. code-block:: python

   qs['DateObs'] = '2013-11-29'
   lampsOff = fs.fileListQuery(dbFile, fs.createQuery('lampsOff', qs), qs)
   f2.f2prepare(flistToStr('',lampsOff), **prepPars)
   for f in lampsOff:
       gemtools.gemarith('p'+f, '-', qs['MCdark'], 'dp'+f, **gemarithPars)

   gemtools.gemcombine(flistToStr('dp', lampsOff), flatComb, **flatCombPars)

   # Use the mean for the normalization constant
   flatCombSect = flatComb+'.fits[1][350:1750,350:1750]'
   iraf.imstat(flatCombSect,fields='mean,stddev,min,max,midpt')
   mean_Ks = str(21894.)

   # Adopt the J-band BPM and replace bad pixels in normalized flat
   iraf.copy('GCALflat_J_bpm.pl',qs['MCbpm'])
   gemtools.gemexpr('(b > 0) ? 1 : a/'+mean_Ks, GCALflat, flatComb, 
                    'MCbpm', **gemexprPars)

   # Clean up
   iraf.imdelete('dS2013*.fits,pS2013*.fits,dpS2013*.fits')

Science Processing
------------------
With all the MasterCals in place, the Science images may be processed. 
The first step is to dark-subtract the science images, then proceed iteratively to construct the sky and science images. 
Because the order of operations in **nireduce** is different than that needed here, it will be necessary to invoke it multiple times with different settings. 

.. warning::

   The science exposures in all bands suffer from vignetting of the field in the NW quadrant. This may have been caused by the PWFS2 guide probe, which was used because of a hardware problem with the OIWFS (see the `F2 instrument status note <https://www.gemini.edu/sciops/instruments/flamingos2/status-and-availability>`_ for 2013 Sep. 5). Therefore the photometry of this portion of the image will be seriously compromised. 

Sky
^^^
The sky images will be derived from the dithered science images, where the sources in the field will be detected and masked. 
First, set task parameters for the invocations of **nireduce**.

.. code-block:: python

   # Set task parameters for first & second invocation of nireduce.
   niri.nireduce.unlearn()
   darkProcPars = pars['nireducePars']
   flatProcPars = copy.deepcopy(darkProcPars)
   flatProcPars.update({
       'outprefix':'f', 
       'fl_dark':'no',
       'fl_flat':'yes',
   })
   skyProcPars = copy.deepcopy(flatProcPars)
   skyProcPars.update({
       'outprefix':'s', 
       'fl_dark':'no',
       'fl_flat':'no',
       'fl_sky':'yes',
       'fl_autosky':'yes'
   })
   niri.nisky.unlearn()
   niskyPars = pars['niskyPars']
   flatCombPars.update({
       'statsec':'[350:1750,350:1750]', 
       'scale':'mean',
   })
   skyCombPars = copy.deepcopy(flatCombPars)
   skyCombPars.update({
       'lthreshold':0.
   })

Now set the calibration information and the list of science exposures for each filter.

.. code-block:: python

   for filt,qs in qd.iteritems():
       qs.update({
           'DateObs':'2013-11-21',
           'Texp':qs['Texp_sci'],
           'MCdark':'MCdark_'+str(int(qs['Texp_sci'])),
       })
       qs['sciFiles'] = fs.fileListQuery(dbFile, 
                                         fs.createQuery('sciImg', qs), qs)

Now process the science images with the following steps: 

* dark subtraction
* create the sky frames per dither sequence
* combine the sky frames per filter
* apply the flat-field to the combined sky frames, per filter

.. caution::

   IRAF will fail with an error if too many files (with lengthly file names) are specified as input to a task. The error (``603``, if you care) is not indicative of the actual problem, which is a string buffer overflow. Potential work-arounds are to loop over the exposures separately, use wildcards in filenames, or (the solution adopted here) to chunk up the file list to a manageable size. 

.. code-block:: python

   for filt,qs in qd.iteritems():
       print 'Creating sky for filter: ', filt
       darkProcPars.update({
           'darkimage':qs['MCdark'], 
           'outprefix':filt+'d'
       })
       i = 0
       for sciFiles in chunks(qs['sciFiles'], ditherCycle):
           f2.f2prepare(flistToStr('', sciFiles), **prepPars)
           niri.nireduce(flistToStr('p', sciFiles), **darkProcPars)
           # nsheaders sets nisky.statsec = '[350:1750,350:1750]'
           i += 1
           outImage = qs['MCsky'] + '-' + str(i)
           niri.nisky (flistToStr(filt+'dp', sciFiles), outimage=outImage, 
                       **niskyPars)
           # Apply flat-field to the sky frame
           flatProcPars['flatimage'] = qs['GCAL_flat']
           niri.nireduce (qs['MCsky']+'-'+str(i), **flatProcPars)
           iraf.imdelete('pS*.fits')
       if i > 1:
           gemtools.gemcombine('f'+qs['MCsky']+'-*', qs['MCsky'], **skyCombPars)
       else:
           iraf.imrename('f'+qs['MCsky']+'-1','f'+qs['MCsky'])

The run-time for the above code snippet is several minutes for the *H--* and *K--* band filters on a desktop machine. 
(Recall that these bands have 72 exposures each.) 
Go get a cup of coffee. 

.. note::

   The above sky frames will be adequate for this relatively sparse field. For deep images of crowded fields it is best to construct a higher fidelity sky frame using **nisupersky**, where the first-order, co-added science image is used as input for source detection and masking. 

Complete the Science Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Resume processing the science exposures. 
Because of the way the **MasterCals** were prepared, the correct order of processing for each science exposure is: 

1. *fprepare* the headers
2. subtract the dark
3. **apply the GCAL flat-field**
4. **subtract the flat-fielded sky image**

Because steps 1--2 were performed when constructing the sky image, we resume the processing with flat-fielding the dark-subtracted images. 
Note that **nireduce** needs to be invoked separately to apply the flat-field, *then* subtract the sky image, in that order.
Finally, combine the science exposures for each filter. 

.. caution::

   The **imcoadd** task is likely to generate incorrect shifts between dithered exposures unless the parameters are very carefully tuned. For example, the ``threshold`` for source detection is set in this tutorial to :math:`30\sigma` above sky, and the ``xwindow`` is set to 81 pixels. It is *highly recommended* to perform the fits to the geometric transformations interactively. The RMS in each coordinate should be around 0.2--0.3 pixels if all is well. 

.. code-block:: python

   gemtools.imcoadd.unlearn()
   imcoaddPars = pars['imcoaddPars']
   for filt,qs in qd.iteritems():
       print 'Creating science image for filter: ', filt
       flatProcPars['flatimage'] = qs['GCAL_flat']
       imcoaddPars['badpixfile'] = qs['MCbpm']
       prefix = filt + 'dp'
       i = 0
       for sciFiles in chunks(qs['sciFiles'],ditherCycle):
           i += 1
           niri.nireduce(flistToStr(prefix, sciFiles), **flatProcPars)
           skyProcPars['skyimage'] = 'f'+qs['MCsky'] + '-' + str(i)
           niri.nireduce(flistToStr('f'+prefix, sciFiles), **skyProcPars)
           outFile = qs['Object'][:-1] + '_' + filt + '-' + str(i)
           gemtools.imcoadd(flistToStr('sf'+prefix, sciFiles), 
                            outimage=outFile, **imcoaddPars)
       iraf.delete('*_mag,*_cen,*_pos,*_trn,*badpix.pl')
       iraf.imdel('*_avg.fits,*_mag.fits,*_med.fits,*_trn.fits')

   # Clean up
   for filt in qd.iteritems():
       iraf.imdelete(filt+'dpS*')
       iraf.imdelete('f'+filt+'dpS*')
       iraf.imdelete('sf'+filt+'dpS*')

The *H--* and *K--* band images of the target from each dither sequence will be combined with **gemcombine**. 

.. code-block:: python

   skyCombPars['zero'] = 'median'
   for filt in ['H','Ks']:
       qs = qd[filt]
       outFile = qs['Object'][:-1] + '_' + filt
       inFiles = outFile + '-*'
       gemtools.gemcombine(inFiles, outFile, **skyCombPars)

Below is a false-color image of the target field, with stars in the WISE catalog highlighted. 
Note that the WCS of the F2 images has been adjusted to the SE by a few pixels to align with the catalog. 

.. figure:: /_static/W0413_Jss.*
   :width: 80 %

   A portion of the *J--* band image of the target field. Stars in the All-WISE catalog [WISE]_ are indicated (*green circles*). The target WISE J041358.14-475039.3 is near the lower-left corner; small displacement from the catalog position may be due to proper motion of the star. 
