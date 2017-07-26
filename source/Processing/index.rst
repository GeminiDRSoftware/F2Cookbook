.. _processing-index:

=======================
Processing Science Data
=======================
The recipes described in the linked chapters provide a recommended, **but not unique** path for processing your FLAMINGOS-2 science data. 
The various tutorials will generate scientifically viable, but not necessarily optimal data products for analysis. 
They will also illustrate ways to organize and search your data, and provide tools and tips for efficient processing in python. 

As described in the :ref:`f2-overview`, FLAMINGOS-2 has three distinct configurations: 

 * imaging
 * long-slit spectroscopy
 * multi-object (:term:`slit-mask`) spectroscopy (not yet commissioned)

The path through data reduction is somewhat different for each mode, though for spectral modes there is considerable overlap. 

.. contents:: 
   :depth: 3

.. _processing-preliminaries:

Preliminaries
-------------
Prerequisites
^^^^^^^^^^^^^
Processing of individual targets can proceed once the following steps have been completed:

  - Software tools have been installed (see :ref:`getting-started` and :ref:`resources`)
  - Science and calibration data have been acquired from the `Gemini Observatory Archive <https://archive.gemini.edu/searchform>`_ (see :ref:`getting-started`)
  - Data have been reviewed and categorized, problem exposures have been identified, and a database has been created of the critical metadata (see :ref:`gen-obslog`)
  - Instrument issues have been reviewed for the epoch of your data (see `F2 Status <https://www.gemini.edu/sciops/instruments/flamingos2/status-and-availability>`_)

Data Retrieval
^^^^^^^^^^^^^^
Download the files of interest from the `Gemini Observatory Archive <https://archive.gemini.edu/searchform>`_ and unpack them in a subdirectory of your working directory. 
Or if you want to practice, then use the URLs given in the tutorials linked below to select the files to reduce, and download them to a working directory. 

.. note::

   When an archive search is performed, the search term values are encoded into the URL of the search results. This means you may save or bookmark the URL; if you use it to search again at a later time it will generate the same (or perhaps, an updated) table of results. 

Uncompress Files
::::::::::::::::
Data files in the GOA are stored in compressed form (with **bzip2**) to save storage and transfer bandwidth. 
Because IRAF tasks (and many other applications) cannot read them directly, you must uncompress all of the compressed :term:`FITS` files you retrieved from the archive. 
In the directory that contains the raw data to be processed: 

.. code-block:: c

   # At the unix prompt, uncompress the desired files. 
   bunzip2 *.fits.bz2

Generate an Observing Log
^^^^^^^^^^^^^^^^^^^^^^^^^
Data files from a single observing program can number in the hundreds. 
Files generated during processing may increase that total by a factor of a few. 
This makes the task of keeping track of files in your workflow a significant challenge. 
See :ref:`gen-obslog` to help manage the problem. 
The observing log is essential to planning your data reduction strategy. 

Be sure to review the exposures, and flag any science or supporting calibration data that should not be processed. 
Also note the exposure times and readout modes for flats, standard stars, and science targets: you will need to build **Dark MasterCals** that match each of these attributes. 

Build File Lists
^^^^^^^^^^^^^^^^
The fundamental approach in this *Cookbook* is to apply selection criteria to the exposure metadata (in the :term:`FITS` file headers) to build generic lists of files of various types, which serve as input to the processing tasks. 
For processing with PyRAF, the metadata are stored in an SQLite3 database, and **python** lists of exposures are created within the reduction scripts with SQL queries. 
The process for building these lists is discussed at the beginning of each tutorial, and in the Chapter :ref:`master-ref`.

.. _config-files:

Configuration Files
^^^^^^^^^^^^^^^^^^^
Various parameters for processing the data are stored in configuration files, the contents of which are read into memory in the form of **python** dictionaries. 
The files are in `YAML <https://en.wikipedia.org/wiki/YAML>`_ format, and the contents must be customized to apply to a particular observing run. 
This helps to separate the processing software from the details of the data being reduced. 
All of the files are recommended for the tutorials, and it is convenient to place them in your work directory; in any case the python dictionaries *must* be populated by some mechanism if not the ``.yml`` files. 

.. note::

   If you change a task parameter value in the ``.yml`` file during a processing session, you must either re-read the ``.yml`` file or explicitly update the relevant parameter dictionary. 

IRAF Task Parameters
::::::::::::::::::::
The large number of parameters for IRAF tasks can be managed with a configuration file, which specifies the initial values (which are not necessarily the default values). 
Fetch one of these files for your configuration

  * Download :download:`imgTaskPars.yml <../pyTools/imgTaskPars.yml>`
  * Download :download:`lsTaskPars.yml <../pyTools/lsTaskPars.yml>`

Parameter settings for a task (such as **nsreduce** or **nisky**) are often copied from a prior invocation, and updated for the circumstances. 
This allows steps to be repeated during a processing session with no worries about clobbering parameter values for another stage of processing. 

Observing Configurations
::::::::::::::::::::::::
Files are selected for processing by matching specific exposure metadata in the observing log database (see :ref:`log-keywords`). 
These parameters are the keyword/value pairs that will be used as file selection criteria in the database queries. 

  * Download :download:`imgObsConfig.yml <../pyTools/imgObsConfig.yml>` 
  * Download :download:`lsFaintObsConfig.yml <../pyTools/lsFaintObsConfig.yml>` or :download:`lsBrightObsConfig.yml <../pyTools/lsBrightObsConfig.yml>`

Data Reduction Work-flow
------------------------
The chapters linked below provide a conceptual workflow, and a set of step-by-step tutorials for data processing within your data reduction environment. The conceptual overview should provide sufficient context for understanding *what* steps are required and *why*, while the tutorials describe *how* the processing is done. 

.. toctree::
   :maxdepth: 3

   Concept_Overview

The first step (after dealing with the :ref:`processing-preliminaries`) is to prepare the calibration reference (:term:`MasterCal`) files for your data. 
The specific **MasterCal** files you will need depends upon the instrument configuration and your science goals for the reductions. 

.. toctree::
   :maxdepth: 2

   masterRef

There are various supplementary topics that describe tools and techniques, conventions, and calibration reference material for reducing your data. 

.. toctree::
   :maxdepth: 2

   SqlFileSelect
   Supplement

PyRAF Data Processing
^^^^^^^^^^^^^^^^^^^^^
The `AstroConda <http://ssb.stsci.edu/ureka/1.5.2/docs/index.html>`_ data processing environment, which includes `PyRAF <http://www.stsci.edu/institute/software_hardware/pyraf>`_, `IRAF <http://iraf.noao.edu>`_ and the **gemini** package, offers a large number of tools for data reduction and calibration. 
The recipes below provide a detailed path using PyRAF for processing your FLAMINGOS-2 science data. 

.. note::

   The PyRAF based tutorials assume a basic understanding of **python**. In addition a familiarity with SQL and the **sqlite** package as called from **python**, while not necessary, would be useful background information. The software module that makes use of **sqlite** is isolated from the tutorial processing scripts, however, so it is fine to treat the SQL selection machinery as a black box. 

.. _pyraf-proc:

Processing data with PyRAF allows scripting and IRAF task execution from the **python** environment. 
See `The PyRAF Tutorial <http://stsdas.stsci.edu/pyraf/doc.old/pyraf_tutorial/>`_ for a primer. 
In an interactive session **pyraf** emulates the IRAF command language very closely. 
In the PyRAF tutorials linked below more of the power of **python** is leveraged to process data, which results in processing scripts that are easier to understand and modify (not to mention more interesting). 
One of the keys to processing data efficiently is to generate **python** lists of files from an observing log database (see: :ref:`gen-obslog`), and either to supply these lists to the processing tasks directly, or to iterate over the lists to process files individually. See :ref:`sql-file-select` for details. 

.. note::

   The code blocks of commands in the tutorials linked below are intended to be executed within a PyRAF session, unless otherwise noted. The traditional prompt (e.g., :math:`\rightarrow`) has been omitted to make it easier to cut-and-paste commands into your own interactive session. Non-executable comments are prepended with a pound sign ("#", or hashtag). 

.. _proc-tutorials:

Processing Tutorials
--------------------
Images
^^^^^^
.. image:: /_static/Leggett_CCD.*
   :width: 304px
   :align: right

This tutorial reduces images from the program GS-2013B-Q-15 (PI: Leggett), *A Study of the 450K Transition from T to Y Dwarf, and of the 350K Y Dwarfs*. 
This team obtained *Y,J,H,Ks* -band images of the T9-dwarf star WISE J041358.14-475039.3. 
See Leggett et al. (2015, ; [L15]_) for details of the science objectives and their data reduction procedure. 

.. toctree::
   :maxdepth: 2

   F2_ProcImg

Longslit Spectra
^^^^^^^^^^^^^^^^
.. image:: /_static/J0126-5505.*
   :width: 326px
   :align: right

The bright, long-slit tutorial reduces long-slit spectra from the program GS-2013B-Q-79 (PI: Gagne), *Spectroscopic Confirmation of Very Low-Mass Stars, Brown Dwarfs and Planemo Candidates in Nearby, Young Moving Groups*. 
This team obtained *JH--* and *HK--* band spectra of generally bright M and L dwarf stars including the M6 dwarf WISE J021653.27-550550.6. 
See Gagne, et al. (2015; [G15]_) for details of the science objectives and their data reduction procedure. 

.. toctree::
   :maxdepth: 2

   F2_ProcBrightLS

.. image:: /_static/Y0_Spec.*
   :width: 326px
   :align: right

The faint, long-slit tutorial reduces long-slit spectra from the program GS-2014B-Q-17 (PI:Leggett), *Exploring the 300K Brown Dwarfs*. 
This team obtained *JH-* band spectra of the very faint Y1 star WISE J035000.32-565830.2. 
See Leggett, et al. (2016) [L16]_ for details of the science objectives and their data reduction procedure. 

.. toctree::
   :maxdepth: 2

   F2_ProcFaintLS

