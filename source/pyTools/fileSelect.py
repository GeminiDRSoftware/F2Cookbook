#!/usr/bin/env python
# RAShaw.astro@gmail.com  2016-Dec-26

import argparse
import glob, os
import sqlite3
import sys

APERMASKS = ['None','1pix-slit','2pix-slit','3pix-slit','4pix-slit','6pix-slit',
             '8pix-slit']
#DISPERSERS = ['Open', 'JH_G5801', 'HK_G5802', 'R3K_G5803']
DISPERSERS = ['Open', 'JH', 'HK', 'R3K']
FILELIST_TYPES = ['arc', 'dark', 'GCALflat', 'twiflat', 'science']
#FILTERS = ['open','Y_G0811','J-lo_G0801','J_G0802','H_G0803','Ks_G0804','K-long_G0812','JH_G0809', 'HK_G0806_good']
FILTERS = ['Open','Y','J-lo','J','H','Ks','K-long','JH','HK']
OBSTYPES = ['ARC','DARK','FLAT','OBJECT']
OBSCLASS = ['dayCal','partnerCal','progCal','science']
READMODES = {'Bright':1,'Medium':4,'Dark':8}

# SQL for various exposure types:
SQL_Arc = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='ARC' AND ObsClass LIKE '%Cal' AND Filter LIKE :Filter
    AND AperMask=:AperMask AND Disperser LIKE :Disperser AND CentWave=:CentWave
    '''

SQL_ArcP = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='ARC' AND ObsClass='progCal' AND Filter LIKE :Filter
    AND AperMask=:AperMask AND Disperser LIKE :Disperser AND CentWave=:CentWave
    '''

SQL_Dark = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='DARK' AND ObsClass LIKE '%Cal'
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads AND T_exp=:Texp
    '''

SQL_ImgTwiFlat = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsClass='dayCal' AND Object='Twilight'
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads
    AND Disperser='MIRROR' AND AperMask="None" AND Filter LIKE :Filter
    '''

SQL_SpecTwiFlat = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='OBJECT' AND ObsClass LIKE '%Cal' AND Object='Twilight'
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads AND Filter LIKE :Filter
    AND AperMask=:AperMask AND Disperser LIKE :Disperser AND CentWave=:CentWave
    '''
SQL_LampsOff = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='FLAT' AND ObsClass LIKE '%Cal' AND GCAL_Shutter='CLOSED'
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads AND Filter LIKE :Filter
    AND AperMask='None'
    '''

SQL_LampsOn = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='FLAT' AND ObsClass LIKE '%Cal' AND GCAL_Shutter='OPEN'
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads AND Filter LIKE :Filter
    AND AperMask='None'
    '''

SQL_GcalFlat = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='FLAT' AND ObsClass LIKE '%Cal'
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads AND Filter LIKE :Filter
    AND AperMask=:AperMask AND Disperser LIKE :Disperser AND CentWave=:CentWave
    '''

SQL_Std = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='OBJECT' AND ObsClass LIKE '%Cal' AND Object=:Object
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads AND Filter LIKE :Filter
    AND AperMask=:AperMask AND Disperser LIKE :Disperser AND CentWave=:CentWave
    '''

SQL_SciSpec = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='OBJECT' AND ObsClass='science' AND Object LIKE :Object
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads AND Filter LIKE :Filter
    AND AperMask=:AperMask AND Disperser LIKE :Disperser AND CentWave=:CentWave
    '''

SQL_SciImg = '''SELECT file FROM obslog WHERE
    use_me=1 AND ObsType='OBJECT' AND ObsClass='science' AND Object LIKE :Object
    AND ReadMode=:ReadMode AND N_Reads=:N_Reads AND Filter LIKE :Filter
    AND AperMask='None'
    '''

SQL_TYPES = {
             'arc':SQL_Arc,
             'arcP':SQL_ArcP,
             'dark':SQL_Dark,
             'lampsOff':SQL_LampsOff,
             'lampsOn':SQL_LampsOn,
             'gcalFlat':SQL_GcalFlat,
             'sciSpec':SQL_SciSpec,
             'sciImg':SQL_SciImg,
             'std':SQL_Std,
             'twiFlat':SQL_ImgTwiFlat,
             'twiSpecFlat':SQL_SpecTwiFlat
             }

def createQuery(listType, queryDict):
    '''Create an SQL statement to select files that match criteria.
        
        Parameters
        ----------
        queryType : str
            Type of exposures to select; one of SQL_TYPES.keys()
        queryDict : dict
            query parameters
        
        Returns
        -------
        SQLstr : str
            SQL query statement to execute
        '''
    # Select a pre-defined SQL statement based on desired type of file list.
    return SQL_TYPES[listType] + dateQuerySegment(queryDict)

def dateQuerySegment(queryDict):
    '''Create an SQL segment to allow any date, or select a range of dates.
        
        Parameters
        ----------
        queryDict : dict
            query parameters
        
        Returns
        -------
        SQLseg : str
            segment of SQL query string
    '''
    dateList = queryDict['DateObs'].split(':')
    if len(dateList) == 1:
        if '*' in dateList[0] or '?' in dateList[0]:
            SQLseg = ' AND DateObs GLOB :DateObs'
        elif 'None' in dateList[0]:
            SQLseg = ''
        else:
            SQLseg = ' AND DateObs=:DateObs'
    else:
        queryDict['date1'],queryDict['date2'] = dateList
        SQLseg = ' AND DateObs>=:date1 AND DateObs <=:date2'
    return SQLseg

def timeQuerySegment(queryDict):
    '''Create an SQL segment to allow any date, or select a range of dates.
        
        Parameters
        ----------
        queryDict : dict
        query parameters
        
        Returns
        -------
        SQLseg : str
        segment of SQL query string
        '''
    timeList = queryDict['TimeObs'].split(':')
    if len(timeList) == 1:
        if '*' in timeList[0] or '?' in timeList[0]:
            SQLseg = ' AND TimeObs GLOB :TimeObs'
        elif 'None' in timeList[0]:
            SQLseg = ''
        else:
            SQLseg = ' AND TimeObs=:TimeObs'
    else:
        queryDict['time1'],queryDict['time2'] = timeList
        SQLseg = ' AND TimeObs>=:time1 AND TimeObs <=:time2'
    return SQLseg


def fileListQuery(dbFile, query, selectDict):
    '''From a DB of observation metadata, return a list of files matching the
        specified criteria.
        
        Parameters
        ----------
        dbFile : str
            name of sqlite database created by obslog.py
        query : str
            SQL query statement
        selectDict : dict
            name:value pairs containing all necessary parameters for query
    '''
    with sqlite3.connect(dbFile) as db:
        db.row_factory = sqlite3.Row
        c = db.cursor()
        c.execute(query, selectDict)
        fileList = [row['File'] for row in c.fetchall()]
    return list(f.split(".fits")[0] for f in sorted(fileList))

def mkOutputFile (outFile, outList):
    '''Write the sorted contents of the list of files to an ASCII file.
        
        Parameters
        ----------
        outFile : str
            Name of output file
        outList : list
            List of selected results
    '''
    with open (outFile, 'w') as o:
        for f in outList:
            line = "%s\n" % (f)
            o.write(line)

def mkFileList(argv):
    '''Create a list of raw image attributes selected from a
       sqlite3 database. 
    '''

    descr_text = 'Construct a list of files or attributes'
    parser = argparse.ArgumentParser(description=descr_text)
    parser.add_argument('dbFile', type=str,
                        help='Name of sqlite3 DB to use')
    parser.add_argument('outFile', type=str,
                        help='Name of output file containing list of input files')
    parser.add_argument('-l', '--listType', choices=SQL_TYPES.keys(),
                        default='Bias', type=str,
                        help='Type of file list')
    parser.add_argument('-a', '--AperMask',
                        default='None', type=str,
                        help='Aperture mask name')
    parser.add_argument('-c', '--ObsClass', choices=OBSCLASS,
                        default='DARK', type=str,
                        help='Class of observation')
    parser.add_argument('-d', '--DateObs',
                        default='*', type=str,
                        help='Calendar date range of exposures (yyyy-mm-dd:yyyy-mm-dd)')
    parser.add_argument('-e', '--Exposure', type=str,
                        help='File name of exposure')
    parser.add_argument('-f', '--Filter', choices=FILTERS,
                        default='open', type=str,
                        help='Name of filter used')
    parser.add_argument('-g', '--Disperser', choices=DISPERSERS,
                        default='Open', type=str,
                        help='Name of grism, or open')
    parser.add_argument('-o', '--Object',
                        default='*', type=str,
                        help='Name of object observed')
    parser.add_argument('-r', '--ReadMode', choices=OBSTYPES,
                        default='bright', type=str,
                        help='Readout mode')
    parser.add_argument('-t', '--ObsType', choices=READMODES.keys(),
                        default='dayCal', type=str,
                        help='Type of observation')
    parser.add_argument('-w', '--CentWave', type=float,
                        help='Central wavelength')
    args = parser.parse_args()
    
    # A call to fileListQuery will need a dictionary something like the following
    queryDict = {
        'use_me':1,
        'ObsClass':args.ObsClass,
        'ObsType':args.ObsType,
        'Disperser':args.Disperser,
        'CentWave':args.CentWave,
        'AperMask':args.AperMask,
        'Filter2':args.Filter,
        'Object':'%'+ args.Object + '%',
        'DateObs':args.DateObs
    }
    # Match to substrings in non-default case.
    if args.Filter != 'Open':
        queryDict["Filter2"] = args.Filter + '_G%'
    if args.Disperser != 'Open':
        queryDict["Disperser"] = args.Disperser + '+_G%'

    # Select a pre-defined SQL statement based on desired type of file list.
    #SQL = SQL_TYPES[args.listType] + dateQuerySegment(queryDict)
    SQL = createQuery(args.listType, queryDict)

    # Expose the query result for testing.
    fileList = fileListQuery(args.dbFile, SQL, queryDict)
    mkOutputFile(args.outFile, fileList)

if __name__ == '__main__':
    mkFileList(sys.argv)
