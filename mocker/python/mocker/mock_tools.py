import os
import argparse
import ConfigParser
import time

# This can be modified by the configuration file -- move to mock_tools
RAW_OUTFILE  = "{archive_path}/raw/{nite}/raw_{expnum:09d}_c{ccdnum:03d}_{band}.fits"
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

# Get the location where the code is installed
try:
    MOCKER_DIR = os.path.join(os.environ['MOCKER_DIR'])
except:
    MOCKER_DIR = __file__.split("/python/")[0]

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
