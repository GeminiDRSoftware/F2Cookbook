.. _glossary:

========
Glossary
========

.. glossary::

   ADU
      For sensor pixel arrays used in Optical/IR astronomy, one *analog-to-digital unit* is one count, corresponding to a quantity of detected photons given by the detector gain setting. 

   Baseline Calibrations
      *Baseline calibration* exposures are those that are obtained by Gemini Staff throughout an observing semester to support the science programs that have been initiated. They include closed-dome (bias, dark, flat-fields) and on-sky (standard stars) observations. See `NIR Baseline Calibrations <http://www.gemini.edu/sciops/instruments/nearir-resources/baseline-calibrations>`_ for details. 

   BPM
   Bad Pixel Mask
      A static *Bad Pixel Mask* can be defined for each focal plane, which consists of an array of short integers that encode pathologies, such as bad columns, that apply to each sensor (see `BPM Flag Encoding <http://ast.noao.edu/sites/default/files/GMOS_Cookbook/Processing/Supplement.html#gmos-bpm-flag-encoding>`_). The BPM is inserted into the :term:`MEF` files as the initial DQ extensions, one for each sensor. 

   CDS
   Correlated Double-Sample
      A method of reading IR sensors in which one or more non-destructive read pairs are obtained just before and just after the exposure. Since there is no shutter for IR cameras, this method provides a means of correcting for the counts that accumulate before the exposure starts, which can be quite substantial in the K-band thermal IR.

   Darks
      *Dark* exposures are of finite duration taken with the shutter closed. They are used to characterize the background that arises from the sensor array, some (or in the *K--* band, most) of which is thermal in origin. In the IR, it is essential that the duration of the dark exposures match that of the science or calibration exposures that are being corrected. 

   dayCal
      A variety of calibration exposures are obtained during the day (or twilight) to support observing programs, and to monitor the health and performance of GMOS. 

   Dither
      A *dither* pattern of exposures in a sequence, with small relative spatial offsets. Dither may be used to provide full coverage of a contiguous region of sky or, in the IR, enable the creation of a sky frame (i.e., with sources excluded). See, e.g., :ref:`ir-background`.

   FITS
      The *Flexible Image Transport System* format is an international standard in astronomy for storing images, tables, and related metadata in disk files. Multiple images and tables may be stored in :term:`MEF` files. See the `IAU FITS Standard <http://fits.gsfc.nasa.gov/fits_standard.html>`_ for details. 

   FoV
      The *field of view*, or spatial extent of sky the from the optical system of the telescope+instrument that actually falls on the detector. 

   GCAL
      The `Gemini Facility Calibration Unit <http://www.gemini.edu/sciops/instruments/gmos/calibration?q=node/10369>`_ provides continuum and emission light sources for flat-field and wavelength calibration of various instruments. 

   HDU
      A :term:`FITS` file consists of a primary *header-data unit* and zero or more extension HDUs. The primary HDU (:term:`PHDU`) contains a header, but may or may not contain an image. An extension HDU contains a header and any valid FITS extension type, including a binary image or a table. 

   Keyword
      In the astronomy data domain, *keyword* is most closely associated with a named metadatum stored in a :term:`FITS` header, which is assigned a particular scalar or text value represented as ASCII. 

   Lamps-Off
      A :term:`GCAL` exposure taken with the flat-field lamp turned *off*. The signal from such exposures taken in the IR consists of a thermal component from the instrument, which may be subtracted from a combined :term:`Lamps-On` exposure. This signal is quite strong in *K--* band, so there is no need to obtain separate Lamps-On exposures. 

   Lamps-On
      A :term:`GCAL` exposure taken with the flat-field lamp turned *on*. The signal from such exposures taken in the IR will include a thermal component from the instrument, which is measured with :term:`Lamps-Off` exposures. 

   MasterCal
      A *Master Calibration* file, which may be an image that captures a particular instrumental signature, or a table consisting of a calibration or reference information. *MasterCals* are often built by combining calibration exposures in a particular way, or by recording coefficients of a function that characterizes a calibration, e.g., the dispersion solution or a linearity correction. They may also consist of a catalog of reference information, such as astrometric or photometric standards. 

   MDF
   Mask Definition File
      The *mask definition file* is a :term:`FITS` binary table that gives the attributes of all apertures for the mask in use during the observation. 

   MEF
      *Multi-extension FITS* format files contain a primary :term:`HDU`, and one or more extensions HDUs, each of which contains a header and data such as a table or binary image. Raw exposures from Gemini normally contain a :term:`PHDU` with no associated data array, and one image extension for each amplifier used for read-out.

   MOS
      *Multi-object spectroscopy* is the capability of obtaining multiple spectra of different targets (or different regions within an extended object) in the same exposure. This may be achieved by orienting a facility longslit to include more than one target, or using a custom slitmask with multiple apertures corresponding to the targets of interest within the :term:`FoV`. 

   N&S
   Nod-and-Shuffle
      It is possible to improve the sky-subtraction in spectra obtained in the red using *nod-and-shuffle* data acquisition. In this operating mode, the telescope position is spatially dithered between sequential exposures, while the charge on the CCDs is shuffled to align with the new pointing. In this way the sky is sampled with the same pixels used to observe the science target. See the Gemini `Nod & Shuffle description <http://www.gemini.edu/sciops/instruments/gmos/nod-and-shuffle>`_ for details. 

   OIWFS
      The *On-Instrument Wavefront Sensor* provides guiding and tip-tilt correction information to the telescope control system. It is mounted on a probe that patrols an area that can extend into the imaging FoV. 

   PHDU
      Primary header-data unit of a :term:`FITS` file, i.e., extension [0] in an :term:`MEF` file. A simple FITS file contains a header and (usually) an image array. The PHDUs in :term:`MEF` files generally *do not* include an image array. 

   Slit-mask
      A *slit-mask* may be inserted at the focal-plane entrance to an instrument to block light from all except selected targets or regions within an extended source from passing through the instrument. Small apertures are cut into the mask that correspond spatially with targets of interest (see, e.g., `GMOS Mask Preparation <http://www.gemini.edu/pio/?q=node/10429>`_). The apertures are usually square (for alignment on field stars) or rectangular (i.e., *slitlets*), with the long axis sized to capture the target and nearby background, without overlapping spatially with other slitlets as projected on the detector. 

   WCS
   World Coordinate System
      A mapping from image pixel coordinates to physical coordinates. 
      For direct images the mapping is to the equatorial (RA, Dec) system; for extracted spectra the mapping is to the dispersion axis, usually in Angstroms, and position along the slit. 