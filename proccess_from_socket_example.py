#!/usr/bin/env python

import os
import sys
import client_getfile as client
import pyfits 
import time

CCDNUM = 59
recv_path = '/lsst8/felipe/ARCHIVE_RECEIVED/DECam/instcal'
REPO = '/lsst8/felipe/REPOS/DECam'
PRODUCTS = '/lsst8/felipe/PRODUCTS'

def elapsed_time(t1,verbose=False):
    """ Formating of the elapsed time """
    import time
    t2    = time.time()
    stime = "%dm %2.2fs" % ( int( (t2-t1)/60.), (t2-t1) - 60*int((t2-t1)/60.))
    if verbose:
        print "# Elapsed time: %s" % stime
    return stime

if __name__ == "__main__":

    # Simple command line option to avoid using argparse
    try:
        remote_host = sys.argv[1]
    except:
        usage ='ERROR: Must provide remote hostname command line\nUSAGE: %s <remote_hostname>' % os.path.basename(sys.argv[0])
        exit(usage)

    # Get the socket and file
    s = client.prepare_socket(remote_host,port=50000)
    filename = client.retrieve_filename(s,path=recv_path)

    # Get the EXPNUM or visit from the file
    header = pyfits.getheader(filename)
    EXPNUM = "%07d" % header['EXPNUM']

    # Step 0 -- Ingestion
    repo_expnum = os.path.join(REPO,EXPNUM)
    if os.path.exists(repo_expnum):
        print "Skipping ingestion -- path %s exists" % repo_expnum
    else:
        print "Will attemp to ingest file: %s" % filename
        # 1 Check if file has already been ingested
        cmd = "ingestImagesDecam.py %s %s" % (REPO,filename)
        print "Running:\n%s\n" % cmd
        os.system(cmd)
        print "Done Ingesting"


    t0 = time.time()
    # Step 1 -- processCCd
    #repo_path = REPO
    repo_path = '/lsst7/ctslater/decam_instcal_repo' # we need to use this one, REPO is not working
    instcal_config = '/home/felipe/LSSTDEV/L1Devel/diffImTest/config/instcal.config'
    command = "processCcd.py {REPO} --id visit={EXPNUM} ccdnum={CCDNUM} --output {PRODUCTS}  -C {instcal_config}"
    cmd = command.format(REPO=repo_path,EXPNUM=EXPNUM,CCDNUM=CCDNUM,PRODUCTS=PRODUCTS,instcal_config=instcal_config)
    print "Running:\n%s\n" % cmd 
    #os.system(cmd)
    print "Done processCcd.py\n"

    # Step 2 -- diffIm
    diffIm_config = '/home/felipe/LSSTDEV/L1Devel/diffImTest/config/diffIm.config'
    command = "imageDifference.py {PRODUCTS} --id visit={EXPNUM}  ccdnum={CCDNUM} --templateId visit={EXPNUM_TEMPLATE} --rerun A --config doAddCalexpBackground=False -C {diffIm_config}"
    cmd = command.format(EXPNUM=EXPNUM,CCDNUM=CCDNUM,PRODUCTS=PRODUCTS,diffIm_config=diffIm_config,EXPNUM_TEMPLATE='0197371')
    print "Running:\n%s\n" % cmd
    #os.system(cmd)
    print "Done imageDifference.py\n"

    print "Total process time: %s" % elapsed_time(t0)
