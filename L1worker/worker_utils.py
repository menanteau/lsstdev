# A set of functions to run parts of the mock pipeline
#

import os
import sys
import time
import sqlite3
import numpy
import shutil

def elapsed_time(t1,verbose=False):
    """ Formating of the elapsed time """
    t2    = time.time()
    stime = "%dm %2.2fs" % ( int( (t2-t1)/60.), (t2-t1) - 60*int((t2-t1)/60.))
    if verbose:
        print "# Elapsed time: %s" % stime
    return stime


def load_repoDB(path,ID):

    DBfilename = os.path.join(path,'registry.sqlite3')
    print "# Loading Template Library from file: %s" % DBfilename
    
    dbh = sqlite3.connect(DBfilename)
    cur = dbh.cursor()
    #query='select distinct  visit, instcal, wtmap, dqmask from raw'
    query='select distinct  instcal, wtmap, dqmask from raw where visit=%s' % ID
    cur.execute(query)
    tuples = cur.fetchall()
    if len(tuples)>0:
        names  = [d[0] for d in cur.description]
        return numpy.rec.array(tuples,names=names)
    else:
        if verb: print "# WARNING DB Query in query2rec() returned no results"
        return False

def make_worker_repo(repo_path,mapper_name='lsst.obs.decam.DecamMapper',clobber=False):
    """ Initialize a local repo in the worker node"""

    # TODO: Define what to do if already exists

    mapper_file = os.path.join(repo_path,"_mapper")

    if os.path.exists(mapper_file):
        print "_mapper already exists at REPO:%s -- bye" % repo_path
        return
    elif not os.path.isdir(repo_path):
        print "Will create REPO localtion:%s" % repo_path
        os.makedirs(repo_path)

    with open(mapper_file, 'w') as f:
        f.write(mapper_name)
    print "Initialzing REPO at: %s" % repo_path
    return

def safe_copy(source,dest):
    

    """ Makes 'safe' copy by creating directory if doesn't exist"""

    dirname = os.path.dirname(dest)
    if not os.path.exists(dirname):
        print '# Making %s' % dirname
        os.makedirs(dirname)

    shutil.copy(source,dest)
    return
    

def find_templateID(visitID):
    # Dictionary to relate exposure with templates
    # Taken from: http://dmtn-006.lsst.io/en/latest/#appendix-a-data-used-in-this-work
    TEMPLATE_ID = {
        '0197371' : '0197371',
        '0197367' : '0197371',
        '0197375' : '0197371',
        '0197379' : '0197371',
        #
        '0197384' : '0197384',
        '0197388' : '0197384',
        '0197392' : '0197384',
        }
    return TEMPLATE_ID[visitID]


def get_template(visitID, repo_path, archive_path):
    """ Find the templates, copy/link file and ingest to WORKER_REPO"""

    # 1. Find the TEMPLATE_ID for a visit 
    ID = find_templateID(visitID)

    # 1. Load in the sqlite3 DB fron the archive path
    fname_archive = load_repoDB(archive_path,ID)[0]

    # 2. Get the fnames in the REPO
    ftypes = fname_archive.dtype.names # gives ['dqmask','wtmap','instcal']
    outnames = [os.path.join(repo_path,f,os.path.basename(fname_archive[f])) for f in ftypes]
    outnames = [tuple(outnames)]
    # Make then into record for consistency
    fname_repo = numpy.rec.array(outnames,names=ftypes)[0]

    # 3. Copy the file
    print "# Copying files from %s --> %s" % (archive_path,repo_path)
    for f in ftypes:
        safe_copy(fname_archive[f],fname_repo[f])

    return fname_repo


def get_visit(visitID, repo_path, archive_path):
    """ Find the templates, copy/link file and ingest to WORKER_REPO"""

    # 1. Load in the sqlite3 DB fron the archive path
    fname_archive = load_repoDB(archive_path,visitID)[0]

    # 2. Get the fnames in the REPO
    ftypes = fname_archive.dtype.names # gives ['dqmask','wtmap','instcal']
    outnames = [os.path.join(repo_path,f,os.path.basename(fname_archive[f])) for f in ftypes]
    outnames = [tuple(outnames)]
    # Make then into record for consistency
    fname_repo = numpy.rec.array(outnames,names=ftypes)[0]

    # 3. Copy the file
    print "# Copying files from %s --> %s" % (archive_path,repo_path)
    for f in ftypes:
        safe_copy(fname_archive[f],fname_repo[f])
    return fname_repo

def ingestDECamFile(REPO,filename):

    from lsst.obs.decam.ingest import DecamIngestTask
    sys.argv[1:] = [REPO,str(filename)]
    DecamIngestTask.parseAndRun()
    return

def processCcd(REPO,visit,ccdnum,**kw):

    from lsst.pipe.tasks.processCcd import ProcessCcdTask
    command = "{REPO} --id visit={EXPNUM} ccdnum={CCDNUM} --output {output} --configfile {configfile}"
    args = command.format(REPO=REPO,EXPNUM=visit,CCDNUM=ccdnum,**kw).split()
    print "Running:\n%s\n" % " ".join(args)
    ProcessCcdTask.parseAndRun(args=args)
    return

def diffImage(REPO,visit,ccdnum,**kw):

    try:
        import scipy.stats
    except ImportError:
        pass
    from lsst.pipe.tasks.imageDifference import ImageDifferenceTask

    template = find_templateID(visit)
    command = "{REPO} --id visit={EXPNUM}  ccdnum={CCDNUM} --templateId visit={TEMPLATE} --rerun A --config doAddCalexpBackground=False --configfile {configfile}"
    args = command.format(EXPNUM=visit,CCDNUM=ccdnum,REPO=REPO,TEMPLATE=template,**kw).split()
    ImageDifferenceTask.parseAndRun(args=args)
    print "Done imageDifference\n"
