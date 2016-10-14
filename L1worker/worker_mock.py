#!/Users/felipe/lsst_stack/DarwinX86/miniconda2/3.19.0.lsst4/bin/python

import os
import sys
import numpy
import time

import worker_utils as wutils

#import ConfigParser
import configparser
import argparse


# For LSST stacks, we fix the OSX EL Capitan and above
# DYLD_LIBRARY_PATH problem, but re-assigning it to LSST_LIBRARY_PATH
#import platform
#if platform.system() == 'Darwin' and int(platform.mac_ver()[0].split(".")[1]) >=1:
#    os.environ['DYLD_LIBRARY_PATH'] = os.environ['LSST_LIBRARY_PATH']

"""
This is a very simple set of instruction to mock the elements of
L1 LSST prompt processing.
"""

def read_config(filename):

    # Modifying the dictionary affects the Namespace oject
    args = argparse.Namespace()
    
    defaults = vars(args)
    config = configparser.ConfigParser()
    config.read([filename]) 
    for section in config.sections():
        defaults.update(dict(config.items(section)))
    return args

if __name__ == "__main__":

    t0 = time.time()

    
    # The conf file
    try:
        configfile = sys.argv[1]
    except:
        sys.exit("ERROR: usage:\n\t%s <config_file>" % os.path.basename(sys.argv[0]))

    args = read_config(configfile)

    # Step 0 -- START Initialization -- to be implemented
    # Start and receive information for the next visit, that includes:
    # CCDNUM, RA, DEC, rotation angle, FILTER, AIRMASS, OBS-DATE
    # For now, here we will pass the filename to be used

    # Step 1 -- Make the WORKER_REPO
    wutils.make_worker_repo(args.worker_repo)
    
    # Step 2 -- Locate template and move them to a local $REPO -- to be created here to
    templateID = wutils.find_templateID(args.visitid)
    template_fname_repo = wutils.get_template(args.visitid, args.worker_repo, args.archive_path)

    # Step 3 -- Ingest template into WORKER_REPO and proccess it
    wutils.ingestDECamFile(args.worker_repo,template_fname_repo['instcal'])
    wutils.processCcd(args.worker_repo,templateID,args.ccdnum,configfile=args.ccdproc_config,output=args.products)
    
    # Step 4 -- Ingest and Run processCcd.py on the visit/ID
    # For now we assume that the visit is in the the same REPO as the TEMPLATE
    visit_fname_repo = wutils.get_visit(args.visitid, args.worker_repo, args.archive_path)
    wutils.ingestDECamFile(args.worker_repo,visit_fname_repo['instcal'])
    wutils.processCcd(args.worker_repo,args.visitid,args.ccdnum,configfile=args.ccdproc_config,output=args.products)
    print "Total process time: %s" % wutils.elapsed_time(t0)

    # Step 5 -- Run difference Imaging
    wutils.diffImage(args.products,args.visitid,args.ccdnum,configfile=args.diffim_config)
    print "Total process time: %s" % wutils.elapsed_time(t0)
