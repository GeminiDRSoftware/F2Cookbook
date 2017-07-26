.. _resources:

================
Useful Resources
================

Resources for your data reduction needs are collected here for easy reference. 
Information about the FLAMINGOS-2 instrument design, operation, and observing may be found on the `FLAMINGOS-2 Home Page <http://www.gemini.edu/sciops/instruments/flamingos2/>`_. 

Archive Portal
--------------
Users of Gemini should retrieve their data from the `Gemini Observatory Archive <https://archive.gemini.edu/searchform>`_. 
No account is necessary to retrieve data, except for recent data covered by a proprietary period during which only the PI or designated Co-Is of the observing program have access. 
Calibration data are not proprietary. 

.. _F2-help:

FLAMINGOS-2 Help
----------------
For help with FLAMINGOS-2 data reduction you may find the `Data Reduction Support page <http://www.gemini.edu/sciops/helpdesk/?q=node/11412>`_ useful. 
To address problems with the Gemini software, direct your inquiry as follows: 

* `Astroconda <http://astroconda.readthedocs.io/en/latest/>`_ installation and PyRAF: help@stsci.edu
* Gemini Helpdesk (`<http://www.gemini.edu/sciops/helpdesk/>`_) for problems with:

  * IRAF tools, including the **gemini** packages
  * Gemini Observatory Archive

* Gemini/IRAF `FAQ list <http://www.gemini.edu/?q=node/11889>`_
* List of `known problems <http://www.gemini.edu/sciops/data-and-results/processing-software/data-reduction-support/known-problems>`_ with **gemini** package software or the data. 
* `Gemini Data Reduction User Forum <http://drforum.gemini.edu/topic-tag/FLAMINGOS-2/>`_

.. _online-resources:

On-Line Resources
-----------------
A number of good tutorials for reducing data have been developed over the years, some of which contain links to demonstration data. 
This *Cookbook* draws upon many of them. 
Here are several:

* `Eduard Westra's data reduction notes <http://eduard.hles.nl/thesis/geminiReductions.shtml>`_ are somewhat applicable to F2 longslit or MOS spectra
* Josh Walawender's `Basic Reductions for Spectroscopic Data <http://www.twilightlandscapes.com/IRAFtutorial/index.html>`_ in IRAF. This resource includes a particularly good tutorial on the `apextract package <http://www.twilightlandscapes.com/IRAFtutorial/IRAFintro_06.html>`_. 

* `The PyRAF Tutorial <http://stsdas.stsci.edu/pyraf/doc.old/pyraf_tutorial/>`_ by Rick White and Perry Greenfield provides a good primer for using **python** to invoke IRAF tasks, while offering the rich programming environment that the language provides. 

* `The PyRAF Programmer's Guide <http://stsdas.stsci.edu/pyraf/doc.old/pyraf_guide/pyraf_guide.html/>`_ by Phil Hodge is a reference for writing **python** tasks that use IRAF functionality. This is an excellent resource for **python** programmers for using and extending PyRAF. 

* `On-line IRAF help files <http://stsdas.stsci.edu/gethelp/HelpSys.html>`_ provided by STScI, which unfortunately does not include the tasks within the **gemini** package.

Standards and Catalogs
----------------------
The following catalogs and other reference material may be of use during your data reduction and analysis: 

* Telluric standard star compendia and a model atmosphere library

  * `Spectroscopic/telluric standards <http://www.gemini.edu/sciops/instruments/nearir-resources/spectroscopic-standards>`_ from Gemini
  * Standard star `calibration library <https://www.eso.org/sci/observing/tools/standards/IR_spectral_library.html>`_ from ESO
  * Standard star `calibration library <http://www.stsci.edu/hst/observatory/crds/calspec.html>`_ from STScI 
  * Cool star `model atmosphere library <http://irtfweb.ifa.hawaii.edu/~spex/IRTF_Spectral_Library/index_files/F.html>`_ from IRTF 

* `DSS <http://archive.eso.org/dss/dss>`_: ESO Online Digitized Sky Survey

* `USNO <http://www.usno.navy.mil/USNO/astrometry/optical-IR-prod/icas>`_ Image and Catalog Archive Server

.. _software-tools:

Software Tools
--------------
IRAF Tools
^^^^^^^^^^
`IRAF <http://iraf.noao.edu>`_ (version 2.16.1) has a variety of packages for the reduction and calibration of images and longslit spectra. For help with IRAF software, post a message to `iraf.net <http://iraf.net>`_

.. csv-table:: **IRAF Data Processing References**
   :header: "Resource", "Description"
   :widths: 15, 60

   `ximtool <http://iraf.noao.edu>`_, IRAF image display tool (not under active development). May be used in place of `ds9 <http://ds9.si.edu/site/Home.html>`_. 
   `WCS Tutorial <http://iraf.noao.edu/projects/ccdmosaic/astrometry/astrom.html>`_, *Creating a Mosaic World Coordinate System* 2000 ([V00]_). Although the material is intended for images from the NOAO MOSAIC Cameras it is quite general and can be applied to most images. **Note:** many of the links on this page are stale.
    :download:`Slit Spectral Reductions <_static/IRAF_LSreduce.pdf>`, *User's Guide to Reducing Slit Spectra with IRAF* [MVB]_; ca. 1992.
    `LS Spectral Extraction <http://iraf.noao.edu/tutorials/doslit/doslit.html>`_, Tutorial for extracting longslit spectra using the `doslit` task; ca. 1994. 


Python Tools
^^^^^^^^^^^^
The **python** packages used within this *Cookbook* are either included with **AstroConda** (or **Ureka** for older installations), or can be installed easily. Two additional modules were built to support this *Cookbook*:

.. csv-table:: **Python Processing Tools**
   :header: "File", "Description"
   :widths: 15, 60

   ``obslog.py``, Unix command-line tool to create a log of observations based on FITS file metadata. Output is an sqlite database and optionally an ASCII representation. 
   ``fileSelect.py``, Provides a method to retrieve a list of files from the observing log (i.e. the SQLite3 database created with **obslog.py**) based on exposure metadata. Can be executed from the unix command line to produce a list of files. 

These tools have dependencies on some common **python** packages. 
A few particularly useful **python** packages are listed in the table below: 

.. csv-table:: **Python Package Dependencies**
   :header: "File", "Description"
   :widths: 15, 60

   `numpy <http://www.numpy.org>`_, Numerical operations on arrays
   `astropy <http://www.astropy.org>`_, General astronomical utilities including FITS i/o
   `matplotlib <http://matplotlib.org/>`_, 2-D python plotting library. 
   `scipy <http://scipy.org>`_, General scientific and mathematical utilities
   `sqlite <https://www.sqlite.org>`_, Database creation and access tools 
   `yaml <https://martin-thoma.com/configuration-files-in-python/#yaml>`_, Data serialization language for configuration files

These packages are included by default in the `Anaconda distribution of python <https://store.continuum.io/cshop/anaconda/>`_, which is highly recommended. 

Third-Party Software
^^^^^^^^^^^^^^^^^^^^
Various third-party software tools may be useful for the data reduction process, depending upon the scientific goals. 
While most astronomers will have many or most of these tools, they are listed here for convenience. 

.. csv-table:: **Third-Party Tools**
   :header: "Tool", "Description"
   :widths: 15, 60

   `Aladin <http://aladin.u-strasbg.fr>`_, Interactive sky atlas; may be used to refine WCS solution in images. The desktop tool can access many on-line astronomical catalogs as well as local (private) catalogs.
   `ds9 <http://ds9.si.edu/site/Home.html>`_, SAOImage DS9 image display tool. May be used in place of IRAF ``ximtool``.
   `SQLite Browser <http://sqlitebrowser.org>`_, Browser for SQLite3 database files.

Acknowledgements
----------------
Scientific publications that make use of data obtained from Gemini facilities should include the appropriate acknowledgement described on the `Gemini Observatory Acknowledgements <http://www.gemini.edu/sciops/data-and-results/acknowledging-gemini>`_ page.  
You should also cite the FLAMINGOS-2 instrument description paper by [EE]_. 

Citations to this *Cookbook* should read: 

   Shaw, R. A. 2017, *FLAMINGOS-2 Data Reduction Cookbook* (Version 1.0; Hilo, HI: Gemini Observatory)

Use of IRAF software should include the following footnote: 

   *IRAF is distributed by the National Optical Astronomy Observatory, which is operated by the Association of Universities for Research in Astronomy (AURA) under a cooperative agreement with the National Science Foundation.*

Use of PyRAF software should also include the following footnote: 

   *PyRAF is a product of the Space Telescope Science Institute, which is operated by AURA for NASA.*

.. _literature-ref:

Literature References
---------------------
.. [NS] Abraham, R. G., et al. 2004, *The Gemini Deep Deep Survey. I. Introduction to the Survey, Catalogs, and Composite Spectra*, `AJ, 127, 2455 <http://adsabs.harvard.edu/abs/2004AJ....127.2455A>`_

.. [WISE] Cutri, R. M., et al. 2013, *Explanatory Supplement to the WISE All-Sky Data Release Products*, `available on-line: <http://adsabs.harvard.edu/abs/2013wise.rept....1C>`_

.. [EE] Eikenberry, S., et al. 2004, *FLAMINGOS-2: the facility near-infrared wide-field imager and multi-object spectrograph for Gemini*, `SPIE, 5492, 1196 <http://adsabs.harvard.edu/abs/2004SPIE.5492.1196E>`_

.. [EE3] Eikenberry, S., et al. 2008, *FLAMINGOS-2: the facility near-infrared wide-field imager and multi-object spectrograph for Gemini*, `SPIE, 7014, 0V <http://adsabs.harvard.edu/abs/2008SPIE.7014E..0VE>`_

.. [G15] Gagne, et al. 2016, *BANYAN. VII. A New Population of Young Substellar Candidate Members of Nearby Moving Groups from the Bass Survey*, `ApJS, 219, 33 <http://adsabs.harvard.edu/abs/2015ApJS..219...33G>`_

.. [L15] Leggett, et al. 2015, *Near-infrared Photometry of Y Dwarfs: Low Ammonia Abundance and the Onset of Water Clouds*, `ApJ, 799, 37 <http://adsabs.harvard.edu/abs/2015ApJ...799...37L>`_

.. [L16] Leggett, et al. 2016, *Near-IR Spectroscopy of the Y0 WISEP J173835.52+273258.9 and the Y1 WISE J035000.32-565830.2: The Importance of Non-Equilibrium Chemistry*, `ApJ, 824, 2 <http://adsabs.harvard.edu/abs/2016ApJ...824....2L>`_

.. [MVB] Massey, P., Valdes, F., & Barnes, J. 1992, *User's Guide to Reducing Slit Spectra with IRAF*, (Tucson: NOAO/IRAF)

.. [FITS] Pence, W.D., Chiappetti, L, Page, C.G., Shaw, R.A., & Stobie, E. 2010, *Definition of the Flexible Image Transport System (FITS), Version 3.0*, `A&A, 524, 42 <http://adsabs.harvard.edu/abs/2010A%26A...524A..42P>`_

.. [AP] Robitaille, T. P., et al. 2013, `Astropy: A Community Python Package for Astronomy  <http://adsabs.harvard.edu/abs/2013A%26A...558A..33A>`_ A&A, 558, 33

.. [RA] Rayner, J. T., Cushing, M.C., & Vacca, W.D. 2009, *The Infrared Telescope Facility (IRTF) Spectral Library: Cool Stars*, `ApJS, 185, 289 <http://adsabs.harvard.edu/abs/2009ApJS..185..289R>`_ 

.. [V00] Valdes, F. 2000, *Creating a Mosaic World Coordinate System*, (Tucson: NOAO/IRAF), available `on-line <http://iraf.noao.edu/projects/ccdmosaic/astrometry/astrom.html>`_

.. [VC] Vacca, W. D., Cushing, M. C., & Rayner, J. T. 2003, *A Method of Correcting Near-Infrared Spectra for Telluric Absorption*, `PASP, 115, 389 <http://adsabs.harvard.edu/abs/2003PASP..115..389V>`_

.. [VD] van Dokkum, P. G. 2001, *Cosmic-Ray Rejection by Laplacian Edge Detection*, `PASP, 113, 1420 <http://adsabs.harvard.edu/abs/2001PASP..113.1420V>`_

