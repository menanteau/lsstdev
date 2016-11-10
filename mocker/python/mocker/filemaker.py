
import os
import fitsio
import numpy
from collections import OrderedDict
import mock_tools

# This can be modified by the configuration file.
RAW_OUTFILE  = "{archive_path}/raw/{date}/raw_{expnum:09d}_c{ccdnum:03d}_{band}.fits"
BPM_OUTFILE  = "{archive_path}/cals/bpm/bpm_c{ccdnum:03d}.fits"
FLAT_OUTFILE = "{archive_path}/cals/flats/flats_c{ccdnum:03d}_{band}.fits"
BIAS_OUTFILE = "{archive_path}/cals/bias/bias_c{ccdnum:03d}.fits"
TEMPLATE_OUTFILE = "{archive_path}/cals/templates/tmpl_c{ccdnum:03d}_{band}.fits"

OUTFILE = {
'raw'  : RAW_OUTFILE,
'bpm'  : BPM_OUTFILE,
'flat' : FLAT_OUTFILE,
'bias' : BIAS_OUTFILE,
'template' : TEMPLATE_OUTFILE,
}

class IMAGEMAKER(object):

    """
    A Class to create mock file to test LSST L1/Prompt processing
    pipeline footprints
    """

    def __init__(self, **keys):

        self.keys = keys

        # Load defaults OUTFILE patterns
        self.OUTFILE = OUTFILE
        
        # Unpack the dictionary of **keys into variables
        # self.keyname = key['keyname']
        for k, v in keys.iteritems():
            setattr(self, k, v)

        # Update OUTFILE format
        for key in self.OUTFILE.keys():
            if keys.get('%s_OUTFILE' % key.upper()):
                print "Updating %s" % key
                self.OUTFILE[key] = keys.get('%s_OUTFILE' % key.upper())

        # Get the generic headers for CCD/TEL
        self.header =  self.read_generic_headers()

    def make(self,filetype,btype,extnames=['SCI',],band='',**keys):

        """ Generic Make image of filetype, btype"""


        self.band = band
        # If any additional keys.... unpack
        for k, v in keys.iteritems():
            setattr(self, k, v)

        # Make sure the path location exists
        outpath = os.path.dirname(self.OUTFILE[filetype]).format(**self.keys)
        mock_tools.create_output_path(outpath)

        print "Preparing the %s files" % filetype
        for ccdnum in self.ccds:

            # Make sure that they are integers
            ccdnum = int(ccdnum)
            # The output name
            kw = {'band':self.band,'expnum':self.expnum,'ccdnum':ccdnum, 'archive_path':self.archive_path, 'date':self.date}
            outfile = OUTFILE[filetype].format(**kw)
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
        
    @staticmethod
    def read_generic_headers():
        """ Read in the generic header per CCD  and telescope """
        # TODO: Add a PRODUCT_DIR path
        header = OrderedDict()
        ccd_head_file = os.path.join(os.environ['MOCKER_DIR'],'etc','ccd.header')
        tel_head_file = os.path.join(os.environ['MOCKER_DIR'],'etc','telescope.header')
        header['CCD'] = fitsio.read_scamp_head(ccd_head_file)
        header['TEL'] = fitsio.read_scamp_head(tel_head_file)
        return header

