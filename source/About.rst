.. _about:

================
About This Guide
================

This *Cookbook* was created to help users reduce and calibrate data obtained with the FLAMINGOS-2 imaging spectrograph. 
Note the version number in the top banner of your browser. 
Users may find the description of FLAMINGOS-2 data products in the :ref:`getting-started` chapter very helpful. 

.. note:: 
   Some intended content for this document has yet to be included: 

   * Tutorials for the MOS configuration must await commissioning of this mode for F2.

   Content created or updated since the last major release for the following topics: 

   * [N/A]

Authors
-------
This *Cookbook* was authored by Dick Shaw, and draws extensively upon the **gemini** package task help, original papers, and presentations about the instrument and IR data reduction techniques. 
In the interest of clarity, the incorporated material is not quoted; rather, citations to prior work appear throughout this *Cookbook*, a reference list is given in :ref:`literature-ref`, and prior data reduction tutorials are listed in :ref:`online-resources`. 

Citations to this *Cookbook* should read: 

   Shaw, Richard A. 2017, *FLAMINGOS-2 Data Reduction Cookbook* (Version 1.0; Hilo, HI: Gemini Observatory), available online at: 

   `<http://rashaw-science.org/F2_drc/>`_

Please see the copyright notice at the bottom of each page. 

Typographical Conventions
-------------------------
Technical documentation is often a struggle to follow. 
This document features some typographical conventions to help the reader understand the content, and to help distinguish explanatory text from dialog with the computer. 
Limitations of `reStructured text <http://www.sphinx-doc.org/en/stable/rest.html>`_ prohibit elaborate textual markup, however. 

Notes, Cautions, and Warnings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

   **Notes** describe technical or scientific points or caveats that likely have a bearing on the scientific viability of the outcome, or call attention to features of the reduction software that may not be obvious, but are important to understand. They appear in a text block like this, usually with a distinct background color (depending upon the settings used for the document build software). 

.. warning::

   **Cautions** and **warnings** describe technical or scientific matters that are likely to seriously compromise the science products being created, or software issues that may result in silent corruption of data. They appear in a colored text block like this, usually with a pink background. 

Technical Terminology
^^^^^^^^^^^^^^^^^^^^^
The descriptions in this *Cookbook* include many technical terms. The first time a technical term, such as :term:`WCS`, is used in a Chapter it is linked with a definition in the :ref:`glossary`.

Software Packages
^^^^^^^^^^^^^^^^^
Names of software packages appear in **bold** font. 
Scripts that were built for this *Cookbook* appear in ``fixed-space`` font and are downloadable via a link. 
Names of third-party packages are often linked to the web site from which they can be downloaded (in which case they cannot appear in **bold font**). 
See the chapter on :ref:`resources` for information about the software packages that are required to make use of the processing scripts. 

.. note::
   Scripts developed for this *Cookbook* are meant to be illustrative and useful. However they do not include error checking, and are not likely to be robust against unexpected input. They are intended serve as a guide for users to develop their own personal processing scripts. 

Code Blocks and Literals
^^^^^^^^^^^^^^^^^^^^^^^^
When describing a process for using software, the text that should be typed by the user appears in a code block, unless it is prepended by a hash:

.. code-block:: bash

   # Type the line below: 
   echo 'Hello, world!'

This text appears in ``fixed-space`` font and usually with syntax highlighting (using `Pygments <http://pygments.org>`_) that is appropriate for the context. 
Text describing a literal command-line, names of arguments, directory and file names, etc. are also set in ``fixed-space`` font.

Colophon
--------
This Cookbook was written using `Sphinx <http://sphinx-doc.org>`_, which uses `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ as the markup language (see `Sphinx Documentation <http://sphinx-doc.org/contents.html>`_). 
Most structured content (headings, lists, tables, warnings, source code blocks, etc.) was implemented with native **Sphinx** markup. 
**Sphinx** has significant limitations, however, so some content required custom tools. 
The following describes the technologies used to implements some features:  

* Some tables were created with **Microsoft Excel** and rendered as a figure (see, e.g., the table of :ref:`f2-grisms`).
* Figures were created in a variety of ways: 

  * screen shots with the OSX **grab** utility (e.g., :ref:`SQLite Browser <sqlite3-browser>`)
  * **python** scripts (e.g., :ref:`wave-cal`)
  * graphic illustrations with `Adobe Illustrator <http://www.adobe.com/products/illustrator.html>`_ (e.g., :ref:`f2-focal-plane`)

The source files used to create these illustrations are available separately. 

Updating This Document
^^^^^^^^^^^^^^^^^^^^^^
If the source or configuration files (found under the ``/source`` subdirectories) are altered, the document HTML files should be rebuilt with: 

.. code-block:: bash

   sphinx-build -b html source F2_drc

which will update the ``.html`` files in the ``/F2_drc`` subdirectory. Then make a tar of the ``/F2_drc`` directory contents, copy it to the deployment directory, and unpack. 

A PDF document may be generated (e.g., in the subdirectory ``tex``) by specifying a ``latex`` target: 

.. code-block:: bash

   sphinx-build -b latex source tex_drc
   cd tex_drc
   pdflatex F2_Cookbook

The quality of the rendering is not very good, however, and the **LaTeX** processing does not complete without errors. 
Improving it would at least require fixing the relevant **LaTeX** style files. 
The best approach is simply to build and tar-gzip the F2_drc directory and let users download it, which would preserve the hyperlink navigation. 
