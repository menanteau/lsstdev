import os
import argparse
import ConfigParser
import time
import fitsio
import numpy

from collections import OrderedDict
import copy

# This can be modified by the configuration file -- move to mock_tools

# Inputs
RAW_FILENAME  = "{archive_path}/raw/{nite}/raw_{expnum:09d}_c{ccdnum:03d}_{band}.fits"
BPM_FILENAME  = "{archive_path}/cals/bpm/bpm_c{ccdnum:03d}.fits"
FLAT_FILENAME = "{archive_path}/cals/flats/flats_c{ccdnum:03d}_{band}.fits"
BIAS_FILENAME = "{archive_path}/cals/bias/bias_c{ccdnum:03d}.fits"
TEMPLATE_FILENAME = "{archive_path}/cals/templates/tmpl_c{ccdnum:03d}_{band}.fits"

# Outputs
ISR_FILENAME  = "{archive_path}/isr_{expnum:09d}_c{ccdnum:03d}_{band}.fits"
COADD_FILENAME = "{archive_path}/coadd_c{ccdnum:03d}_{band}.fits"
REMAP_FILENAME = "{archive_path}/remap_c{ccdnum:03d}_{band}.fits"
DIFFIMA_FILENAME = "{archive_path}/diffima_c{ccdnum:03d}_{band}.fits"
DIAOBJ_FILENAME = "{archive_path}/diffima_c{ccdnum:03d}_{band}_objcat.fits"
DIASRC_FILENAME = "{archive_path}/diffima_c{ccdnum:03d}_{band}_srccat.fits"
DIAALR_FILENAME = "{archive_path}/diffima_c{ccdnum:03d}_{band}_alrcat.fits"

FILENAME = {
'raw'  : RAW_FILENAME,
'bpm'  : BPM_FILENAME,
'flat' : FLAT_FILENAME,
'bias' : BIAS_FILENAME,
'template' : TEMPLATE_FILENAME,
'isr' : ISR_FILENAME,
'coadd' : COADD_FILENAME,
'remap' : REMAP_FILENAME,
'diffima' : DIFFIMA_FILENAME,
'diasrc' : DIASRC_FILENAME,
'diaobj' : DIAOBJ_FILENAME,
'diaalr' : DIAALR_FILENAME,
}

# Get the location where the code is installed
try:
    MOCKER_DIR = os.path.join(os.environ['MOCKER_DIR'])
except:
    MOCKER_DIR = __file__.split("/python/")[0]


def get_headers_hdus(filename):
    
    header = OrderedDict()
    hdu = OrderedDict()   

    # Case 1 -- for well-defined fitsfiles with EXTNAME
    with fitsio.FITS(filename) as fits:
        for k in xrange(len(fits)):
            h = fits[k].read_header()

            if not h.get('EXTNAME') and k==0:
                header['PRIMARY'] = h
                extname = 'PRIMARY'
                header[extname] = h
                hdu[extname] = k
                continue

            # Make sure that we can get the EXTNAME
            if not h.get('EXTNAME'):
                continue
            extname = h['EXTNAME'].strip()
            if extname == 'COMPRESSED_IMAGE':
                continue
            header[extname] = h
            hdu[extname] = k
    return header,hdu

def elapsed_time(t1,verbose=False):
    """ Formating of the elapsed time """
    t2    = time.time()
    stime = "%dm %2.2fs" % ( int( (t2-t1)/60.), (t2-t1) - 60*int((t2-t1)/60.))
    if verbose:
        print "# Elapsed time: %s" % stime
    return stime


def create_output_path(local_archive,logger=None):
   
    """ Make sure that the place where we want to write exists"""
    if not os.path.exists(local_archive):
        message = "Will create: %s" % local_archive
        if logger: logger.info(message)
        else: print message
        os.makedirs(local_archive)
    return

def build_conf_parser(verb=False):

    """ Create a paser with argparse and ConfigParser to load default arguments """

    # Parse any conf_file specification
    # We make this parser with add_help=False so tha it doesn't parse -h and print help.
    conf_parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
        )
    conf_parser.optionxform = str
    conf_parser.add_argument("-c", "--conf_file",
                             help="Specify config file")
    args, remaining_argv = conf_parser.parse_known_args()

    # Load the info into a defaults dictionary
    defaults = {}
    if args.conf_file:
        if not os.path.exists(args.conf_file) and verb:
            print "# WARNING: configuration file %s not found" % args.conf_file
        config = ConfigParser.RawConfigParser()
        config.optionxform=str # Case sensitive
        config.read([args.conf_file]) # Fix True/False to boolean values
        # Read in each section auto-asign types
        for section in config.sections():
            # Go over items
            for option,value in config.items(section):
                # Fix str -> bool
                if value == 'False' or value == 'True':
                    bool_value = config.getboolean(section, option)  
                    if verb:
                        print "# Updating %s: %s --> bool(%s) section: %s" % (option,value,bool_value, section)
                    config.set(section,option, bool_value)
                # Fix str1,str2 to list
                elif value[0] == '[' and value[-1] == ']':
                    v = value[1:-1]
                    if v.split(',')[0]  == '':
                        config.set(section,option,v.split(',')[:-1])
                    else:
                        config.set(section,option,v.split(','))
            defaults.update(dict(config.items(section)))
    return conf_parser,defaults


def writeCatalog(outname,nrows,ncols,dtype='f8'):

        # Names of the columns and dtypes
        dtypes = [("VAR%s" % (k+1), dtype) for k in range(ncols)]
        data = numpy.zeros(nrows,dtypes)

        for var,vartype in dtypes:
            data[var] = numpy.random.random((nrows))

        header=fitsio.FITSHDR()
        fitsio.write(outname, data, extname='OBJECTS',clobber=True,header=header)
