.. FLAMINGOS-2 Data Reduction Cookbook documentation master file, created by
   sphinx-quickstart on Mon Dec  5 10:19:20 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

 
.. figure:: /_static/F2_m17_sm.*
..   :figwidth: 6.5in

   FLAMINGOS-2 image of M17. Photo credit: Gemini Observatory/AURA

===================================
FLAMINGOS-2 Data Reduction Cookbook
===================================

The `Gemini Observatory <http://www.gemini.edu>`_ provides a variety
of facility-class instruments for use by the professional astronomy
community, including the FLAMINGOS-2 wide-field imager and
multi-object spectrograph (sometimes abbreviated `F2
<https://www.gemini.edu/sciops/instruments/gmos/?q=sciops/instruments/flamingos2>`_),
which is deployed on Gemini-South. This imaging spectrograph offers
useful sensitivity in the near-infrared (NIR) from :math:`0.95-2.4\mu
m`, at high spatial resolution and low to moderate spectral
resolution. FLAMINGOS-2 was constructed by the `University of Florida
Astronomy Department <http://www.astro.ufl.edu/>`_ and delivered in
2009 July; it was refurbished and commissioned in 2011-December.  The
F2 `Status and Availability
<https://www.gemini.edu/sciops/instruments/flamingos2/status-and-availability>`_
page summarizes significant operations issues over the life of the
instrument that may have affected the quality of the science data in
the Archive.

Data from the commissioning periods to the present are offered in the
`Gemini Observatory Archive
<https://www.gemini.edu/sciops/data-and-results/gemini-observatory-archive>`_.
Raw data for this instrument is archived and made available for public
use, but no calibrated, science-ready products are provided. This
*Cookbook* is intended as a guide to data reduction and calibration
for PIs and Archive users of data from FLAMINGOS-2. The descriptions,
recipes, and scripts offered in this *Cookbook* will provide the
necessary information for deriving scientifically viable (but not
necessarily optimal) spectra and images from F2. However, users should
be aware that the ultimate utility of the data for any specific
scientific goal depends strongly upon a number of external factors,
including:

  * the environmental conditions that prevailed at the time of the observations
    (see the `Gemini data quality assessment process <https://www.gemini.edu/sciops/data-and-results?q=node/10797#Off-lineDP>`_),
  * the performance of the instrument, 
  * the observing procedures used to obtain the data,
  * the scientific objectives of the original observing program.

The FLAMINGOS-2 instrument is very well documented on the
`Gemini/FLAMINGOS-2 website
<https://www.gemini.edu/sciops/instruments/flamingos2/>`_ and in
published papers.  But it is not necessary to understand every detail
of the instrument design and operation to reduce your data; links to
relevant portions of the instrument literature will appear throughout
this manual.

.. toctree::
   :numbered:
   :maxdepth: 2

   Introduction
   F2_overview
   Processing
   Tutorial_Imaging
   Tutorial_Longslit
   Tutorial_MOS
   Resources

   Glossary
