.. _getting-started:

===============
Getting Started
===============
Processing and calibrating your F2 data requires some preparation, including setting up your software environment if you have not already done so, retrieving and organizing the data of interest, and reviewing reference material that may be relevant. 

.. contents:: 
   :depth: 2

.. _software-setup:

Software Environment
--------------------
The IRAF **gemini** package is presently the most comprehensive set of utilities for reducing data from F2. 
There is more than one way to install and configure the software needed to reduce your F2 data.
However, most users prefer a relatively simple installation process that is robust, easy to upgrade, and that does not interfere with other software that is installed on their hardware. This section will describe the recommended path (which, happily, requires the least time and trouble) to install the software you will need. 

IRAF, PyRAF, the **gemini** data reduction package, and all required dependency packages are, as of 2017 Jan, distributed through the `AstroConda <http://astroconda.readthedocs.io/en/latest/index.html>`_ software repository. 
The instructions below describe the essentials of setting up the software environment, but for full details see the full `AstroConda Installation Instructions <http://astroconda.readthedocs.io/en/latest/installation.html>`_.

.. warning::

   The tutorial processing scripts were tested using v1.13.1 of the **gemini** IRAF package, which was released in 2017 January. *Use of prior versions is unlikely to be compatible* as some capabilities, task parameters, and default values have been added or changed. See the `release history <http://www.gemini.edu/sciops/data-and-results/processing-software?q=node/12078>`_. You should upgrade to v1.13.1 via AstroConda. 

.. warning::

   The `Ureka software distribution <http://ssb.stsci.edu/ureka/1.5.2/>`_, which had been the recommended way of creating the software environment prior to 2016 April, has been deprecated. While Ureka is still available, there will be no upgrades to the software packages it includes. Specifically, the **gemini** package v1.13.1 and above **will not** be available through Ureka. 

First-Time Setup
^^^^^^^^^^^^^^^^
The first step is to install **python v2.7.x** and various supporting packages on your system; 
this is a prerequisite for the PyRAF environment. 
That may seem odd if you only want to use IRAF for your data reductions. 
But the platform supported by Gemini Observatory is PyRAF, and there are known problems and incompatibilities with the **gemini** package using the standard IRAF distribution. 
It is also critical to select a **python** version and a consistent set of dependency packages, which may or may not be fully compatible with what you currently have on your personal machine. 

The solution is to install the `Anaconda distribution <https://www.continuum.io/downloads>`_ of **python** from Continuum Analytics, and then install PyRAF and related packages from the `AstroConda distribution <http://astroconda.readthedocs.io/en/latest/installation.html>`_ at Space Telescope Science Institute. 

.. note::

   Anaconda and AstroConda do not interfere with your current defaults for IRAF, python and related packages if they are already installed on your computer. It merely provides a way to install and use one or more *consistent, compatible, and self-contained* sets of software environments for Gemini/IRAF. AstroConda provides shell commands that allow you to switch between environments. 

Anaconda
::::::::
**Anaconda Update**
...................
If you already have the Anaconda distribution installed on your system, ensure that the packages are up to date: 

.. code-block:: bash

   conda update --all

**First-Time Install**
......................
If this is a first-time setup, install and configure **python** and related packages from `Anaconda <https://www.continuum.io/downloads>`_. 

   1. **Use bash.** Be sure you are using the **bash** shell (the response to typing ``echo $SHELL`` should be something like ``/bin/bash``). If this is not your default shell, start one (e.g., by typing ``bash -l`` in your current terminal window). 

   2. **Download Anaconda.** Fetch the **command-line** installer appropriate to your system for **python** version 2.7, and place it in a suitable directory.

   3. **Invoke the installer.** From the directory where you placed the downloaded install script, invoke it: 

.. code-block:: bash

   # Mac OSX users:
   bash Anaconda2-4.0.0-MacOSX-x86_64.sh

   # Linux users:
   bash Anaconda2-4.0.0-Linux-x86_64.sh

The exact name of the file will depend upon the version number and the name of your platform. 
The installation process may take awhile, as it downloads, unpacks, and installs a lot of software including IRAF, python, and supporting packages. 

   4. **Start a new terminal window** for the changes to your login file to take effect. Then type ``which conda``; the response should be the path to the Anaconda installation. If instead the response is a blank line, update your bash shell configuration file to include the path to the anaconda installation. 

AstroConda
::::::::::
You should review the detailed documentation for AstroConda, particularly the `installation instructions <http://astroconda.readthedocs.io/en/latest/installation.html>`_. 
The instructions to get **pyraf** running are summarized below. 

**First-Time Install**
......................
The first step is to configure Anaconda to install software packages directly from the STScI AstroConda repository. 
The following will add AstroConda to the Conda search path (defined in the ``~/.condarc`` file):

.. code-block:: bash

   conda config --add channels http://ssb.stsci.edu/astroconda

Now software can be installed from the AstroConda repository:

.. code-block:: bash

   conda create -n iraf27 python=2.7 iraf pyraf stsci

**Subsequent Uses**
...................
Once all the software has been installed, activate the data analysis environment of your choice *each time you start a shell*:

.. code-block:: bash

   # Python with IRAF and PyRAF: 
   source activate iraf27

.. caution::

   A test version of the **gemini** package distribution via AstroConda was made available in early 2017. By March 2017 the distribution mechanism the **gemini** package is via the command above. During the test period, the (deprecated) commands below would have applied. 

.. code-block:: bash

   # Temporary config for deprecated test version:
   conda config --add channels http://astroconda.gemini.edu/public
   # Temporary install for test version:
   conda create -n gemini python=2.7 iraf-all pyraf stsci
   source activate gemini

Now start PyRAF as usual. 
To return to your default (non-AstroConda) installation of IRAF and python, type ``source deactivate iraf27`` at the Unix prompt, or close the terminal window. 

IRAF, PyRAF, and Python
:::::::::::::::::::::::
Configure your IRAF setup if you have not already done so, preferably in a directory that is by default compatible with PyRAF:

.. code-block:: sh

   cd ~
   mkdir iraf
   cd iraf
   mkiraf
   ...
   # Respond to the prompt to select an IRAF terminal type, e.g.:
   Enter terminal type [default: xterm]: xgterm

Finally, start the analysis environment of your choice from the Unix prompt: 

* ``pyraf`` for PyRAF
*  ``python``

For an interactive **python** session, import the relevant portion of the **pyraf** package. 

.. code-block:: python

   import sys
   from pyraf import iraf
   from pyraf.iraf import gemini
   # import other python and  pyraf packages as needed

See the *PyRAF Programmer's Guide* by Phil Hodge, specifically the chapter `Writing Python Scripts that Use IRAF/PyRAF Tasks <http://stsdas.stsci.edu/pyraf/doc.old/pyraf_guide/node2.html>`_. 

Getting Help
^^^^^^^^^^^^
Help is available if you run into problems. 
Contact:

* help@stsci.edu with problems installing or invoking the software  
* `Gemini Help Desk <http://www.gemini.edu/sciops/helpdesk/>`_ with problems with using the software for data reduction. 

.. _data-downloads:

Data Downloads
--------------
Search and retrieve the science and calibration data from the `Gemini Observatory Archive <https://archive.gemini.edu/searchform>`_ for each program, source, or calendar night of interest. 
See the `GOA overview <https://www.gemini.edu/sciops/data-and-results/gemini-observatory-archive>`_ for details. 

First-Time Access
^^^^^^^^^^^^^^^^^
If you are a general archive user, no login is necessary to search for any data, or to retrieve non-proprietary data including calibration frames. 
**Only** if you are a PI or Co-I of an observing program **and** you wish to retrieve your *proprietary* data, you must do the following before you can access these files:

   1. `Request an account <https://archive.gemini.edu/request_account/>`_ if you don't already have one. You will receive an e-mail telling you how to establish a password (or *data access key* in their vernacular). 
   2. Navigate to the `Gemini Observatory Archive <https://archive.gemini.edu/searchform>`_ in your browser.
   3. Click the ``Not logged in`` link at the upper right of the page and login using your account credentials. **You will need your program ID and password to retrieve your proprietary data.**

PIs of Gemini observing programs should have received in their award notification email the instructions for how to establish an account. 

.. caution::
   Note that applicable ancillary data (arc lamp, flat-field, or standard star exposures) may have been obtained on a night other than that of the science observation(s) of interest. You may need these exposures to calibrate the science data, particularly if they were obtained in Queue mode. These calibration data are normally accessible by clicking the **Associated Calibrations** tab following a successful search. 

.. _archive-search: 

Archive Searches
^^^^^^^^^^^^^^^^
Science Data
::::::::::::
GOA searches for FLAMINGOS-2 data begin with selecting ``F2`` from the **Instrument** pull-down menu, as shown below. 

.. figure:: /_static/GOA_search.* 
   :width: 90 %

   Interface for GOA search for FLAMINGOS-2 data, also showing the available metadata that may be displayed in columns of the results table. The tabs at the bottom allow access to the calibration data for the specified program. This search was for spectroscopic data from program GS-2014B-Q-17 with a restricted date range. 

Calibration Data
::::::::::::::::
Calibration exposures are routinely obtained by Gemini staff to support queue observations, and to monitor the health and performance of the instruments. 
Some calibrations are obtained at night to support queue mode. 
The exposures of most potential interest for data reduction include: 

* Darks
* Arcs
* Flat-fields
* Telluric standard stars

Very often observers include additional standard star exposures in their programs, depending upon the science goals. 

.. _retrieve-data:

Retrieving Data
:::::::::::::::
After a successful search for your data of interest, do the following: 

* Scroll to the bottom of the search results and click the *Download all [NNN] files* button. This will create a tar of the selected files and download it to your machine. Naturally you can download only selected files from the search table, if you have the patience. 

* Click the **Load Associated Calibrations** tab on the search results page, and click the *Download all [NNN] files* button. It is common for these files to include some exposures you do not need, but but it is easier to ignore them during data reduction than to attempt to filter them out with tighter archive search criteria. 

* Move the tar files to your desired working directory and un-tar. Re-name the data subdirectory to ``/raw``, then use ``bunzip2`` to uncompress the files. 

.. _data-packaging:

Data Packaging
::::::::::::::
.. image:: /_static/MEF.*
   :width: 160px
   :align: right

FLAMINGOS-2 raw data, and processed data as produced by tasks in the **f2** and related packages, are stored in :term:`FITS` files and structured internally in Multi-Extension FITS (:term:`MEF`)---i.e., FITS files with one or more `standard extensions <http://fits.gsfc.nasa.gov/xtension.html>`_. 
MEF files are used to group logically connected data objects, as explained below and on the `FLAMINGOS-2 website <http://www.gemini.edu/sciops/instruments/flamingos2/status-and-availability/fixes-and-improvements-20092011>`_. 
The structure of an MEF file is shown at right: a Primary Header-data unit (:term:`PHDU`), followed by one or more `standard FITS extensions <http://fits.gsfc.nasa.gov/xtension.html>`_. 
The extensions are numbered sequentially, and normally will contain a header keyword record called ``EXTVER`` with a value equal to the extension number. 

F2 MEF files follow the :term:`FITS` Standard recommendation that the PHDU never contains image pixel data; the extensions are either of type IMAGE or BINTABLE, and no other type. 
The number and type of extensions in F2 data files depends upon the level of processing and the content, and the extensions can appear in any order. 
Raw exposures contain a :math:`2048\times2048\times1` pixel array in the first extension. 
The table below summarizes the structure of the contents for reduced data products. 
Optional extensions in grey are added if the ``fl_vardq+`` flags are specified during processing. 

.. image:: /_static/Extn_Table.*
   :scale: 40%

.. _reference-presentations:

Reference Materials
-------------------
In addition to the material in the :ref:`resources` chapter, it may be handy to have the following documents available when reducing your data: 

* `FLAMINGOS-2 Instrument pages <http://www.gemini.edu/sciops/instruments/F2/?q=sciops/instruments/F2>`_
* Data reduction recipes, [TBA]

Getting Organized
-----------------
Many FLAMINGOS-2 observing programs (on clear nights, at least) generate hundreds of exposures. 
Some of them (such as *acq* exposures) may have been obtained to configure the instrument for observing and are not relevant for data reduction. 

Types of Observations
^^^^^^^^^^^^^^^^^^^^^
The following types of FLAMINGOS-2 observations are routinely obtained, depending upon the observing program. Types in *italics* are rarely useful for data reduction. 

.. csv-table:: **Types of Observations**
   :header: "Type", "Frequency", "Description"
   :widths: 20, 30, 50

   *Focus*, a few to several per night, Part of a sequence of exposures of a bright star or a flat-field lamp used to obtain the best focus of the telescope or the spectrograph. Not used for calibration. 
   Dark, dozens per night, Sequence of finite-duration exposures with the shutter closed.  Duration of darks should match the duration of science exposures.
   Flat-field, several nightly per filter, Sequence of exposures of the twilight sky (typically for imaging) or with the :term:`GCAL` flat-field lamp (for spectroscopy). They are combined and normalized to apply the pixel-level sensitivity correction.  
   Comparison Arc, one or more per night per slit/grating combination, Exposures of the Argon comparison arc used to derive geometric rectification and wavelength calibration.
   Image, one or more per filter per target field, **Science image** obtained with ``ObsMode = imaging``. May also be obtained for target field acquisition. 
   *Acquisition image*, one or more per target field, Short-duration image obtained through a custom :term:`Slit-mask` (``ObsMode = acq``). Used to determine offsets from targets to slits; not used for data reductions. 
   Long-slit spectrum, one or more per target position, **Science spectrum** obtained with a facility longslit (``MASKNAME = <X>pix-slit``). 
   MOS spectrum, one or more per target position, **Science spectra** obtained with a custom Slit-mask (``MASKNAME`` = <mask>); one spectrum per slit including field stars. Mask names include the observing program ID. 

