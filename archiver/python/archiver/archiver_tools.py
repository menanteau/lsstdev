#!/usr/bin/env python

"""
A set of functions and signatures for functions for the LSST
Archiver
"""

import fitsio
import hashlib
import time
import yaml

# TODO:
# - Add logging

class ArchiverWorker:

    def __init__(self):

        # Define here:
        # - load yaml configuration file with keys
        with open("etc/archiver_conf.yaml", 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)

        # TODO
        # - DB engine and server to use, make connection
        # - archive location definitions

        
    def checkMetadata(self,FileName):

        """ Make sure that the file contains the minimum metadata """

        # Get the header using fitsio
        self.header = getheader(FileName)

        # Make sure that all required keywords and present
        for key in self.cfg['keywords']:
            if key in self.header:
                self.allkeys=True
            else
                self.allkeys=False

    def checkMD5(self,FileName,md5):

        if md5Checksum(FileName) == md5:
            print "MD5 Checksum values match -- continue"
            self.md5match = True
        else:
            print "MD5 Checksum values DO NOT match -- continue"
            self.md5match = False

    def updateDB(self,FileName):

        for key in self.cfg['keywords']:
            print "inserting %s to DB" % key
        
        

            

def getheader(filename,ext=0,**keys):
    
    """ Get the header of a file using fitsio"""
    header = fitsio.read_header(filename, ext=0, **keys)
    return header

def elapsed_time(t1,verbose=False):
    """ Formating of the elapsed time """
    import time
    t2    = time.time()
    stime = "%dm %2.2fs" % ( int( (t2-t1)/60.), (t2-t1) - 60*int((t2-t1)/60.))
    if verbose:
        print "# Elapsed time: %s" % stime
    return stime

def md5Checksum(filePath,blocksize=1024*512):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(blocksize)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

    

