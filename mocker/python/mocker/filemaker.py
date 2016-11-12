
import os
import fitsio
import numpy
from collections import OrderedDict
import mock_tools


class IMAGEMAKER(object):

    """
    A Class to create mock file to test LSST L1/Prompt processing
    pipeline footprints

    Felipe Menanteau, Nov 2016
    """

    def __init__(self, **keys):

        self.keys = keys

        # Load defaults FILENAME patterns
        self.FILENAME = mock_tools.FILENAME

        # Load default location
        self.MOCKER_DIR = mock_tools.MOCKER_DIR
        
        # Unpack the dictionary of **keys into variables
        # self.keyname = key['keyname']
        for k, v in keys.iteritems():
            setattr(self, k, v)

        # Update FILENAME format
        for key in self.FILENAME.keys():
            if keys.get('%s_FILENAME' % key.upper()):
                print "Updating %s definitions" % key
                self.FILENAME[key] = keys.get('%s_FILENAME' % key.upper())

        # Get the generic headers for CCD/TEL
        self.header =  self.read_generic_headers(self.MOCKER_DIR)

    def make(self,filetype,btype,extnames=['SCI',],band='',**keys):

        """ Generic Make image of filetype, btype"""

        self.band = band
        # If any additional keys.... unpack
        for k, v in keys.iteritems():
            setattr(self, k, v)

        # Make sure the path location exists
        outpath = os.path.dirname(self.FILENAME[filetype]).format(**self.keys)
        mock_tools.create_output_path(outpath)

        print "Preparing the %s files" % filetype
        for ccdnum in self.ccds:

            # Make sure that they are integers
            ccdnum = int(ccdnum)
            # The output name
            kw = {'band':self.band,'expnum':self.expnum,'ccdnum':ccdnum, 'archive_path':self.archive_path, 'nite':self.nite}
            outfile = self.FILENAME[filetype].format(**kw)
            im_ccd = OrderedDict()

            # Loop over extnames
            ofits = fitsio.FITS(outfile,'rw',clobber=True)
            for extname in extnames:
                # Make a random np array
                if filetype == 'template':
                    n1 = int(self.naxis1*1.25)
                    n2 = int(self.naxis2*1.25)
                    im_ccd[extname] = numpy.random.random((n1,n2)).astype(btype)
                else:
                    im_ccd[extname] = numpy.random.random((self.naxis1,self.naxis2)).astype(btype)
                ofits.write(im_ccd[extname],extname=extname,header=self.header['CCD'])

            print "Wrote %s" % outfile

        # If we make a raw, we need to revup by one the expnum
        if filetype == 'raw': self.expnum = self.expnum + 1
        
    @staticmethod
    def read_generic_headers(mocker_dir):
        """ Read in the generic header per CCD  and telescope """
        # TODO: Add a PRODUCT_DIR path
        header = OrderedDict()
        ccd_head_file = os.path.join(mocker_dir,'etc','ccd.header')
        tel_head_file = os.path.join(mocker_dir,'etc','telescope.header')
        header['CCD'] = fitsio.read_scamp_head(ccd_head_file)
        header['TEL'] = fitsio.read_scamp_head(tel_head_file)
        return header

