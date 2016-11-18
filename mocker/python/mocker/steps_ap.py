import os
import fitsio
import numpy
import time
from collections import OrderedDict
import mock_tools
import shutil
from sys import stdout
import copy

class APmock(object):

    """
    A class to mimic the steps and I/O footprint of the LSST Alert Production Pipeline

    Felipe Menanteau, Nov 2016

    """

    def __init__(self, **keys):

        self.keys = keys

        # Load defaults FILENAME patterns
        self.FILENAME = mock_tools.FILENAME

        # TODO -- Load defaults for INPUT_PATH and PRODUCT_PATH
        #self.INPUT_PATH = mock_tools.INPUT_PATH
        #self.PRODUCT_PATH = mock_tools.PRODUCT_PATH

        # Unpack the dictionary of **keys into variables
        # self.keyname = key['keyname']
        for k, v in keys.iteritems():
            setattr(self, k, v)

        # Update FILENAME format
        for key in self.FILENAME.keys():
            if keys.get('%s_FILENAME' % key.upper()):
                print "Updating %s definitions" % key
                self.FILENAME[key] = keys.get('%s_FILENAME' % key.upper())

        # Define locations
        self.input_path   = self.INPUT_PATH.format(**keys)
        self.product_path = self.INPUT_PATH.format(**keys)

        # Assign wait times for each step
        self.waittime = {
            'slew'    : self.slew,
            'readout' : self.readout,
            'exposure': self.exposure,
            }

        # TODO: Asign compute times (in addtion to I/O) to steps
        self.computetime = {}

    def begin_visit(self):
        # Here we start the clock
        self.time_start = time.time()
        self.time_last  = self.time_start

    def copy_calibs(self,filetypes=['flat','bpm','bias','template']):

        for ftype in filetypes:
            
            src  = self.find_file(filetype=ftype,location=self.archive_path)
            dest = self.find_file(filetype=ftype,location=self.input_path)

            if self.dryrun:
                print "DRYRUN: Will not get %s --> %s" % (src,dest)
            else:
                print "Getting: %s --> %s" % (src,dest)
                # Prepare location
                mock_tools.create_output_path(os.path.dirname(dest))
                # Copy preserving metadata (cp -p)
                shutil.copy2(src, dest)

    def get_visit(self,snap):

        expnum = self.expnum + snap - 1

        src  = self.find_file(filetype='raw',location=self.archive_path,expnum=expnum)
        dest = self.find_file(filetype='raw',location=self.input_path,expnum=expnum)

        if self.dryrun:
            print "DRYRUN: Will not copy %s --> %s" % (src,dest)
        else:
            print "Getting SNAP %s: %s --> %s" % (snap,src,dest)
            # Prepare location
            mock_tools.create_output_path(os.path.dirname(dest))
            # Copy preserving metadata (cp -p)
            shutil.copy2(src, dest)

    def find_file(self,filetype='flat',location='archive_path',expnum=''):

        """ Find the path to the flats for the current visit """
        kw = {'band':self.band,'expnum':expnum,'ccdnum':self.ccdnum, 'archive_path': location, 'nite':self.nite}
        outfile = self.FILENAME[filetype].format(**kw)
        return outfile


    def run_step(self,stepname):

        sleeptime = getattr(self, stepname)
        if sleeptime > 0:
            while sleeptime > 0:
                stdout.write("\rSleeping while waiting for %s to complete : %d s. (remaining)" % (stepname,sleeptime))
                stdout.flush()
                time.sleep(1)
                sleeptime = sleeptime - 1
            stdout.write("\n") # move the cursor to the next line


    def write_coadd(self,nima=2,btype='float32'):

        # Read in and add
        coadd_data = {
            'SCI' : 0,
            'WGT' : 0,
            }
        for k in range(nima):
            expnum = self.expnum + k
            src = self.find_file(filetype='isr',location=self.product_path,expnum=expnum)
            ifits = fitsio.FITS(src,'r')
            for EXTNAME in ['SCI','WGT']:
                header = ifits[EXTNAME].read_header()
                data   = ifits[EXTNAME].read()
                coadd_data[EXTNAME] = coadd_data[EXTNAME] + data
            
        # Define out names
        dest = self.find_file(filetype='coadd',location=self.product_path)
        ofits = fitsio.FITS(dest,'rw',clobber=True)
        for EXTNAME in ['SCI','WGT']:
            ofits.write(coadd_data[EXTNAME],extname=EXTNAME,header=header)
        print "Wrote %s" % dest


    def write_isr(self,snap,btype='float32'):

        # Now we write the ISR corrected image based on 
        expnum = self.expnum + snap - 1
        src  = self.find_file(filetype='raw',location=self.input_path,expnum=expnum)
        dest = self.find_file(filetype='isr',location=self.product_path,expnum=expnum)

        ifits = fitsio.FITS(src,'r')
        ofits = fitsio.FITS(dest,'rw',clobber=True)
        # Read in the input
        header = ifits[0].read_header()
        data   = ifits[0].read()
        image = copy.deepcopy(data)        
        im = {
            'SCI' : image.astype(btype),
            'WGT' : 1e-4*image.astype(btype),
            }
        for EXTNAME in ['SCI','WGT']:
            ofits.write(im[EXTNAME],extname=EXTNAME,header=header)
        print "Wrote %s" % dest

    def write_remap(self,btype='float32'):

        # Now we write the remapped template
        src  = self.find_file(filetype='template',location=self.product_path)
        dest = self.find_file(filetype='remap',location=self.product_path)

        ifits = fitsio.FITS(src,'r')
        ofits = fitsio.FITS(dest,'rw',clobber=True)
        # Read in the input
        header = ifits[0].read_header()
        naxis1 = header['NAXIS1']
        naxis2 = header['NAXIS2']

        # We only read the section we need to use
        data   = ifits[0][0:naxis1-1,0:naxis2-1]
        weight = ifits[1][0:naxis1-1,0:naxis2-1]

        image_sci = copy.deepcopy(data)
        image_wgt = copy.deepcopy(weight)        
        im = {
            'SCI' : image_sci.astype(btype),
            'WGT' : image_wgt.astype(btype),
            }
        for EXTNAME in ['SCI','WGT']:
            ofits.write(im[EXTNAME],extname=EXTNAME,header=header)
        print "Wrote %s" % dest

    def write_diffima(self,btype='float32'):

        # Now we write the remapped template
        src  = self.find_file(filetype='coadd',location=self.product_path)
        dest = self.find_file(filetype='diffima',location=self.product_path)

        ifits = fitsio.FITS(src,'r')
        ofits = fitsio.FITS(dest,'rw',clobber=True)
        # Read in the input
        header = ifits[0].read_header()
        naxis1 = header['NAXIS1']
        naxis2 = header['NAXIS2']

        # We only read the section we need to use
        data   = ifits[0].read()
        weight = ifits[1].read()

        image_sci = copy.deepcopy(data)
        image_wgt = copy.deepcopy(weight)        
        im = {
            'SCI' : image_sci.astype(btype),
            'WGT' : image_wgt.astype(btype),
            }
        for EXTNAME in ['SCI','WGT']:
            ofits.write(im[EXTNAME],extname=EXTNAME,header=header)
        print "Wrote %s" % dest


    def write_catalog(self,ftype,ncols=10,nrows=None,btype='f8'):
        dest = self.find_file(filetype=ftype,location=self.product_path)

        # if not passed
        if not nrows:
            nrows = getattr(self, ftype)
        mock_tools.writeCatalog(dest,nrows,ncols,dtype='f8')
        print "Wrote %s objects to %s" % (nrows,dest)

    def next(self,step):

        self.time_now = time.time()
        #sleeptime = self.waittime[step] - (self.time_now - self.time_last )
        sleeptime = self.keys[step] - (self.time_now - self.time_last ) 
        if sleeptime > 0:
            while int(sleeptime) > 0:
                stdout.write("\rSleeping while waiting for %s time to complete : %d s. (remaining)" % (step,sleeptime))
                stdout.flush()
                time.sleep(1)
                sleeptime = sleeptime - 1
            stdout.write("\n") # move the cursor to the next line
        else:
            print "Running behind for %s: %.3f sec (remaining)" % (step,sleeptime)

        self.time_last = time.time()
        return


