import os
import argparse
import ConfigParser

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
