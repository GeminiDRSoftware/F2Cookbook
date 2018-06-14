.. _introduction:

============
Introduction
============

.. _about:

About This Cookbook
-------------------

This cookbook provides python programs for reducing imaging and
long-slit spectroscopic data taken with the FLAMINGOS-2 instrument on
the Gemini South telescope, and descriptions of how to use and modify
them. While these programs do group together reduction steps and can
be run from start to finish to fully reduce scientific data with a
minimal amount of preparation, they are *not* intended to be
autonomous pipelines. You should always visually inspect your data for
obvious defects and understand the processes involved in reducing your
data so you can pinpoint where any problems arise.

No prior knowledge of python is assumed or required, although a basic
understanding will be helpful: due to the rather awkward way in which
PyRAF acts as an interface between python and IRAF, the tutorial
scripts are not the best learning material.

.. _software-setup:

Software Environment
--------------------

The IRAF **gemini** package is presently the most comprehensive set of
utilities for reducing data from F2. The only fully-supported way of
obtaining the up-to-date version of this software is through the
`AstroConda <http://astroconda.readthedocs.io/en/latest/index.html>`_
distribution channel of Anaconda.

Full details of how to obtain and install Gemini IRAF and its
dependencies can be found on the `Gemini website
<http://www.gemini.edu/sciops/data-and-results/processing-software>`_
and will not be addressed here.

If you already have AstroConda on your system, ensure that the
packages are up to date:

.. code-block:: bash

   conda update --all


Getting Help
^^^^^^^^^^^^
Help is available if you run into problems. 
Contact:

* help@stsci.edu with problems installing or invoking the software  
* `Gemini Help Desk <http://www.gemini.edu/sciops/helpdesk/>`_ with problems with using the software for data reduction. 

.. _data-downloads:

Data Downloads
--------------

Search and retrieve the science and calibration data from the `Gemini
Observatory Archive <https://archive.gemini.edu/searchform>`_ for each
program, source, or calendar night of interest.  See the `GOA overview
<https://www.gemini.edu/sciops/data-and-results/gemini-observatory-archive>`_
for details.

First-Time Access
^^^^^^^^^^^^^^^^^

If you are a general archive user, no login is necessary to search for
any data, or to retrieve non-proprietary data including calibration
frames.  **Only** if you are a PI or Co-I of an observing program
**and** you wish to retrieve your *proprietary* data, you must do the
following before you can access these files:

   1. `Request an account
      <https://archive.gemini.edu/request_account/>`_ if you don't
      already have one. You will receive an e-mail telling you how to
      establish a password (or *data access key* in their vernacular).
   2. Navigate to the `Gemini Observatory Archive
      <https://archive.gemini.edu/searchform>`_ in your browser.
   3. Click the ``Not logged in`` link at the upper right of the page
      and login using your account credentials. **You will need your
      program ID and password to retrieve your proprietary data.**

PIs of Gemini observing programs should have received in their award
notification email the instructions for how to establish an account.

.. caution::

   Note that applicable ancillary data (arc lamp, flat-field, or
   standard star exposures) may have been obtained on a night other
   than that of the science observation(s) of interest. You may need
   these exposures to calibrate the science data, particularly if they
   were obtained in Queue mode. These calibration data are normally
   accessible by clicking the **Load Associated Calibrations** tab
   following a successful search.

.. _archive-search:

Archive Searches
^^^^^^^^^^^^^^^^

Science Data
++++++++++++

There will always be multiple ways to select the science data you want
from the GOA search page, including via Program ID, Target Name, or
celestial coordinates. Note that, although proprietary data will
appear in a search, only *non-proprietary* archival data (or your own
proprietary data) will be available for download (the proprietary
period for Gemini data is currently 12 months).

.. figure:: /_static/GOA_search.* 
   :width: 90 %

   Interface for GOA search for FLAMINGOS-2 data, also showing the
   available metadata that may be displayed in columns of the results
   table. The tabs at the bottom allow access to the calibration data
   for the specified program. This search was for spectroscopic data
   from program GS-2014B-Q-17 with a restricted date range.


After a successful search for your data of interest, you should scroll
to the bottom of the search results and click the *Download all [NNN]
files* button. This will create a tar of the selected files and
download it to your local disk. If you are only interested in a few
files, you can manually check those files and click the *Download
Marked Files* button.


Calibration Data
++++++++++++++++

Calibration exposures are routinely obtained by Gemini staff to
support queue observations, and to monitor the health and performance
of the instruments.  The exposures of most potential interest for data
reduction include:

* Darks
* Flat-fields
* Arcs
* Telluric standard stars

Very often observers include additional standard star exposures in
their programs, depending upon the science goals.

To find the appropriate calibrations for your chosen science
exposures, click the **Load Associated Calibrations** tab on the
search results page. Note that this will find the calibrations
appropriate for *all* the science exposures, and not just those that
have been checked. It is therefore worth being as precise as possible
in your science data search to ensure that only relevant calibrations
are found.

Click the *Download all [NNN] files* button. It is common for these
files to include some exposures you do not need, but but it is easier
to ignore them during data reduction than to attempt to filter them
out with tighter archive search criteria.

After downloading all files, you should create a working directory for
the raw data, and extract the files from the tarballs there, using
``tar xvf /path/to/gemini_data.tar``. Then use ``bunzip2`` to
uncompress the files. If an unnecessarily large number of calibration
files have been downloaded, this is a sensible time to delete any
extraneous ones.

Types of Observations
^^^^^^^^^^^^^^^^^^^^^
The following types of FLAMINGOS-2 observations are routinely obtained, depending upon the observing program. Types in *italics* are rarely useful for data reduction. 

.. csv-table:: **Types of Observations**
   :header: "Type", "Frequency", "Description"
   :widths: 20, 30, 50

   Dark, several per week, Sequence of finite-duration exposures with the shutter closed.  Duration of darks must match the duration of science exposures and be taken with the same readout mode.
   Flat-field, several monthly per filter, Sequence of exposures of the :term:`GCAL` flat-field lamp. They are combined and normalized to apply the pixel-level sensitivity correction.
   Comparison Arc, one or more per night per slit/grating combination, Exposures of the Argon comparison arc used to derive geometric rectification and wavelength calibration.
   Image, one or more per filter per target field, **Science image** obtained with ``ObsMode = imaging``. May also be obtained for target field acquisition. Usually these are dithered to allow background subtraction.
   *Acquisition image*, one or more per target field, Short-duration image obtained through a custom :term:`Slit-mask` (``ObsMode = acq``). Used to determine offsets from targets to slits; not used for data reductions. 
   Long-slit spectrum, one or more per target position, **Science spectrum** obtained with a facility longslit (``MASKNAME = <X>pix-slit``).  Usually these are dithered along the slit to allow subtraction of bright sky lines.
   MOS spectrum, one or more per target position, **Science spectra** obtained with a custom Slit-mask (``MASKNAME`` = <mask>); one spectrum per slit including field stars. Mask names include the observing program ID. 

.. _data-packaging:

Data Packaging
--------------

.. _file-nomenclature: 

File Nomenclature
^^^^^^^^^^^^^^^^^

It is usually simplest during data reduction to retain the filenames
of raw exposures as provided by the Gemini Observatory Archive, and to
allow processing tasks to take care of naming output files.  The raw
filename template is the following:

   <*site*><*yyyy*><*mm*><*dd*> ``S`` <*nnnn*> ``.fits``

where ``S`` and ``.fits`` are literals, and: 

* <*site*> is either ``N`` or ``S``, indicating which telescope took the data
* <*yyyy*><*mm*><*dd*> is the year, numerical month, and UT date of observation
* <*nnnn*> is a 4-digit (prefixed with zeroes if necessary) running
  sequence number within a UT day

Multi-Extension FITS
^^^^^^^^^^^^^^^^^^^^

.. only:: html

   .. image:: /_static/MEF.*
      :width: 160px
      :align: right

FLAMINGOS-2 raw data, and processed data as produced by tasks in the
**f2** and related packages, are stored in :term:`FITS` files and
structured internally in Multi-Extension FITS (:term:`MEF`)---i.e.,
FITS files with one or more `standard extensions
<http://fits.gsfc.nasa.gov/xtension.html>`_.  MEF files are used to
group logically connected data objects, as explained below and on the
`FLAMINGOS-2 website
<http://www.gemini.edu/sciops/instruments/flamingos2/status-and-availability/fixes-and-improvements-20092011>`_.
Each MEF file contains a Primary Header-data
unit (:term:`PHU`), followed by one or more `standard FITS extensions
<http://fits.gsfc.nasa.gov/xtension.html>`_.  The extensions are
numbered sequentially, and will contain header keywords ``EXTNAME``
describing the type of data they contain and ``EXTVER`` with a value
equal to the extension number.

F2 MEF files follow the :term:`FITS` Standard recommendation that the
PHU never contains image pixel data; the extensions are either of
type IMAGE or BINTABLE, and no other type.  The number and type of
extensions in F2 data files depends upon the level of processing and
the content, and the extensions can appear in any order.  Raw
exposures contain a :math:`2048\times2048\times1` pixel array in the
first extension.  The table below summarizes the structure of the
contents for reduced data products.  Optional extensions in grey are
added if the ``fl_vardq+`` flags are specified during processing.

.. image:: /_static/Extn_Table.*
   :scale: 60%

