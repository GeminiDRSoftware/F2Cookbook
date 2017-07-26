.. _sql-file-select:

========================
SQL-Based File Selection
========================
The PyRAF-based tutorials use observation metadata harvested from exposure file headers, and stored in an `SQLite3 <https://www.sqlite.org>`_ database; the database is created with the ``obslog.py`` python script. 
See :ref:`gen-obslog` for details. 
A programming `interface to SQLite3 <https://docs.python.org/2/library/sqlite3.html>`_ is included in **python**, which makes it possible to move beyond browsing, and harness the full power of the database. 

You may browse the contents of the database using the `SQLite3 browser <http://sqlitebrowser.org>`_ independently of which environment you choose for data processing. 
It is in general necessary to review the observing log in order to discover associations between exposures in an observing program: Arcs or :term:`GCAL` flats taken before or after science exposures, for example, need to be used as :term:`MasterCal` reference files for the associated science exposures. 

Preliminaries
-------------
Software
^^^^^^^^
Beyond the software provided in the required `AstroConda <http://astroconda.readthedocs.io/en/latest/index.html>`_ distribution (which includes **python**, **IRAF**, and **PyRAF**; see :ref:`software-setup`), you will need to download the following **python** scripts: 

* Download: :download:`obslog.py <../pyTools/obslog.py>` 
* Download: :download:`fileSelect.py <../pyTools/fileSelect.py>` 

The file selection module includes template SQL statements for selecting files, and methods for specifying metadata on which to perform selections. 
Place ``fileSelect.py`` in your work directory. 

Observing Log Database
^^^^^^^^^^^^^^^^^^^^^^
You must create an observing log database of the data, assumed here to reside in the ``./raw`` subdirectory of your work directory. 
Place ``obslog.py`` in that subdirectory, and execute it from the unix prompt.

.. code-block:: bash

   cd /path/to/work_directory/raw
   source activate iraf27    # if needed
   python obslog.py obsLog.sqlite3

Database Contents
:::::::::::::::::
As with any database it is important to understand what and how information is stored within it (the database *schema* in the vernacular) in order to construct a meaningful query. 
Key metadata are harvested from raw exposures by the ``obslog.py`` script (see :ref:`header-metadata`). 
These metadata are contained in a single database table named ``obslog``. 

Start a PyRAF Session
^^^^^^^^^^^^^^^^^^^^^
From your work directory, start a PyRAF session. 

.. code-block:: bash

   cd /path/to/work_directory
   pyraf

Now load the packages needed for processing, plus the file selection module. 

.. code-block:: python

   from pyraf import iraf
   from pyraf.iraf import gemini, gemtools, f2
   import fileSelect as fs
   # import other packages if you need them

Selecting Files
---------------
There are really only a few things to know when selecting files from within PyRAF. 
Just two functions are needed in most of your PyRAF reduction scripts; a third is needed if you are reducing :term:`Nod-and-Shuffle` data: 

fs.\ **createQuery** (*query_type*, *query_dict*)

   Return an SQL template string for the specified type of exposure 

   * *query_type* --- The SQL appropriate for the type of exposure
   * *query_dict* --- The SQL selection parameter dictionary

fs.\ **fileListQuery** (*dbFile*, *SQL*, *query_dict*)

   Return a list of files matching a query, constructed with the SQL template and parameter values.

   * *dbFile* --- The path/name of the SQLite database created by ``obslog.py``
   * *SQL* --- The SQL template returned by **createQuery**
   * *query_dict* --- The SQL selection parameter dictionary

fs.\ **offsetQuery** (*dbFile*, *SQL*, *query_dict*)

   Return a list of DTAX offsets from files matching a query, constructed with the SQL template and parameter values.

   * *dbFile* --- The path/name of the SQLite database created by ``obslog.py``
   * *SQL* --- The SQL template returned by **createQuery**
   * *query_dict* --- The SQL selection parameter dictionary

The types of exposures for which there is a predefined SQL template can be found from a dictionary in the module: ``SQL_TYPES.keys()``. 
Other types can be created and used, but that requires some level of comfort with **python** and SQLite. 
See :ref:`sql-selection-examples` below for examples of using these functions in PyRAF.

Constructing an SQL Query
^^^^^^^^^^^^^^^^^^^^^^^^^
Creating an SQL query requires two elements: 

* a **python** dictionary of named parameters, which you create
* a template SQL ``select`` statement, which can be selected from the pre-defined templates

The file selection module performs the actual database query behind the scenes, and returns the **python** list of matching filenames. 

Parameters
::::::::::
The following is an example of a full specification of the parameter dictionary for long-slit science exposures (see the tutorial XXX: 

.. code-block:: python

   queryDict = {
        'Instrument': 'F2',
        'ObsType': 'OBJECT',
        'ObsClass': 'science',
        'Disperser': 'R3K',
        'AperMask': '2pix-slit',
        'Filter': 'K-long',
        'Object': '%AM2306%',
        'DateObs': '*'
   }

The ``Object`` parameter uses SQL wildcards to match any target name that contains a string, in this case ``AM2306``. 
Note that a fully qualified dictionary is not necessary if you are using one of the pre-defined SQL query templates because some of the parameters are known from context. 

SQL Templates
:::::::::::::
An SQL *select* statement specifies the fields to be matched. 
To create one, the ``fileSelect.py`` module contains predefined SQL *templates* that apply for the following kinds of exposures
In the table below all query templates require specifying the ``Instrument``, ``RoI``,, ``CcdBin``, and ``ObsDate`` parameters; other required parameters are listed.  

.. csv-table:: **SQL Templates**
   :header: "Key", "Required Parameters", "Description"
   :widths: 20, 15, 40

    ``SQL_Arc``, ``AperMask Disperser CentWave DateObs``, Arc lamp exposure taken as a generic calibration exposure 
    ``SQL_ArcP``,  ``AperMask Disperser CentWave DateObs``, Arc lamp taken as a ``progCal`` exposure 
    ``SQL_Bias``,  ``DateObs``, Bias exposure 
    ``SQL_Dark``,  ``DateObs``, Dark lamp exposure 
    ``SQL_GcalFlat``, ``AperMask Disperser CentWave DateObs``, Spectral flat-field obtained with GCAL 
    ``SQL_ImgTwiFlat``, ``Filter2 DateObs``, Imaging flat-field of the twilight sky 
    ``SQL_Std``,   ``AperMask Disperser CentWave DateObs``, Standard star spectrum 
    ``SQL_SciImg``, ``Object Filter2 DateObs``, Science target image 
    ``SQL_SciSpec``, ``Object AperMask Disperser CentWave DateObs``, Science target spectrum 
    ``SQL_Offset``, ``Object DateObs``, Science target spectrum and DTAX offset value

You can show the above template names in a PyRAF session by typing ``SQL_TYPES.keys()``.
The example SQL template below is relatively simple, for BIAS exposures. 

.. code-block:: SQL

   SQL_Bias = '''SELECT file FROM obslog WHERE
       use_me=1 AND ObsType='DARK' AND ObsClass LIKE '%Cal'
       AND Instrument=:Instrument
       '''

.. note::

   The special ``use_me`` parameter is added by default when creating the database. Changing this value to zero (using the `SQLite3 database browser <http://sqlitebrowser.org>`_ tool, for example), allows you to exclude individual bad exposures from being selected for processing. 

Some parameters are given literal arguments while others, preceded by a colon, must be provided via parameters. 
Parameters that are included in the query parameter dictionary, but not required for the chosen SQL template, are ignored. 

.. note::

   The ``DateObs`` parameter *must always* be specified, either as a wildcard (``*``) to match any date, as a single date, or as an inclusive date range (e.g., ``'DateObs':'2006-09-01:2006-10-30'``); a date clause will automatically be added to the SQL template.

.. _sql-selection-examples:

File Selection in PyRAF
-----------------------
The following example shows how the SQL-based file selection works in your PyRAF processing script. 

.. code-block:: python

   from pyraf import iraf
   from pyraf.iraf import gemini, gemtools, gmos
   import fileSelect as fs

   # Path to and name of the observing log database.
   dbFile='./raw/obsLog.sqlite3'

   # Select dark exposures within a particular date range.
   # Create the query dictionary of essential parameter=value pairs.
   qd = {
         'Instrument':'F2',
         'DateObs':'2014-09-01:2014-10-30'
        }
   # The following SQL generates the list of files to process.
   SQL = fs.createQuery('dark', qd)
   darkFiles = fs.fileListQuery(dbFile, SQL, qd)

   # The str.join() function is needed to transform a python list into a 
   # string of comma-separated filenames that IRAF can understand. 
   f2.dark(','.join(str(x) for x in darakFiles), "MCdaark", fl_vardq=yes)

The following selects imaging science exposures within the same dataset. 
Note that query dictionary merely needs to be augmented from the Bias exposure selection criteria above.

.. code-block:: python

   # Select the target at any position.
   qd["Object"] = 'M8-%'
   for f in filters:

       # Filter is selected by generic name: 'Ha' rather than 'Ha_G0336'
       qd["Filter2"] = f + '_G%'
       SQL = fs.createQuery('sciImg', qd)
       sciFiles = fs.fileListQuery(dbFile, SQL, qd)
       flatFile = "MCflat_%s.fits" % (f)

       # Science processing
       f2.nireduce (','.join(str(x) for x in sciFiles), bias="MCbias", 
                      flat1=flatFile)

Host-Level Filelist Creation
----------------------------
In formulating selection criteria for processing, it is sometimes not obvious if the result will select *exactly* the intended files. 
To preview the results, the ``fileSelect.py`` module may be executed as a task from the Unix prompt, which will generate an ASCII file of selected filenames. 
The task command-line switches may be viewed by invoking the *help* option: 

.. code-block:: bash

   # From the unix prompt:
   python fileSelect.py -h

Use the `SQLite3 database browser <http://sqlitebrowser.org>`_ to verify the accuracy of your selection criteria. 

