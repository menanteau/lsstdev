#!/usr/bin/env python

"""
A simple, a very simple function to serve a binary file continusly
over TCP using python socket. This script should be executed on the
server. A compannion script: client-getfile.py should be use to retrieve the file

F. Menanteau, NCSA July 2016.

"""

DECam_filename = {
    "0197367" :"/lsst7/ctslater/decam_newNEO/instcal/tu1724182.fits.fz",
    "0197371" :"/lsst7/ctslater/decam_newNEO/instcal/tu1724563.fits.fz",
    "0197375" :"/lsst7/ctslater/decam_newNEO/instcal/tu1723669.fits.fz",
    "0197379" :"/lsst7/ctslater/decam_newNEO/instcal/tu1723666.fits.fz",
    "0197384" :"/lsst7/ctslater/decam_newNEO/instcal/tu1723664.fits.fz",
    "0197388" :"/lsst7/ctslater/decam_newNEO/instcal/tu1724060.fits.fz",
    "0197392" :"/lsst7/ctslater/decam_newNEO/instcal/tu1723662.fits.fz",
    "0197400" :"/lsst7/ctslater/decam_newNEO/instcal/tu1724558.fits.fz",
    "0197404" :"/lsst7/ctslater/decam_newNEO/instcal/tu1724407.fits.fz",
    "0197408" :"/lsst7/ctslater/decam_newNEO/instcal/tu1724172.fits.fz",
    "0197412" :"/lsst7/ctslater/decam_newNEO/instcal/tu1724056.fits.fz",
    "0197662" :"/lsst7/ctslater/decam_newNEO/instcal/tu1726959.fits.fz",
    "0197790" :"/lsst7/ctslater/decam_newNEO/instcal/tu1727432.fits.fz",
    "0197802" :"/lsst7/ctslater/decam_newNEO/instcal/tu1727130.fits.fz",
    "0198372" :"/lsst7/ctslater/decam_newNEO/instcal/tu1733827.fits.fz",
    "0198376" :"/lsst7/ctslater/decam_newNEO/instcal/tu1733271.fits.fz",
    "0198380" :"/lsst7/ctslater/decam_newNEO/instcal/tu1733042.fits.fz",
    "0198384" :"/lsst7/ctslater/decam_newNEO/instcal/tu1733308.fits.fz",
    "0198668" :"/lsst7/ctslater/decam_newNEO/instcal/tu1733688.fits.fz",
    "0199009" :"/lsst7/ctslater/decam_newNEO/instcal/tu1734344.fits.fz",
    "0199021" :"/lsst7/ctslater/decam_newNEO/instcal/tu1734248.fits.fz",
    "0199033" :"/lsst7/ctslater/decam_newNEO/instcal/tu1734584.fits.fz",
}


BFSIZE=2048

import socket
import os
import sys

def prepare_socket(port=50000,backlog=5,size=BFSIZE):

    """ Prepare a TCP socket on a given port """

    # Get local machine name
    host = socket.gethostname()     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host,port))
    s.listen(backlog)
    print "Setting up server: %s:%s, with backlog %s" % (host,port,backlog)
    return s


def send_filename(filename,socket_object,size=BFSIZE):

    """ Sends a filename using a socket object"""

    s = socket_object

    # Infinite loop
    while True:
        
        # Establish connection with client and get handshake
        conn, addr = s.accept()     
        print "Got connection request from: %s" % socket.getfqdn(addr[0])
        data = conn.recv(size)
        print "Received:%s" %  repr(data)
        
        # Senf the filename first
        conn.send(os.path.basename(filename))
        
        # Open and send contents
        f = open(filename,'rb')
        l = f.read(size)
        while (l):
            conn.send(l)
            l = f.read(size)
        f.close()
        print 'Done sending: %s ...bye' % filename
        conn.close()

if __name__ == "__main__":

    # Simple command line option to avoid using argparse
    try:
        EXPNUM = sys.argv[1]
    except:
        usage ='ERROR: Must provide filename on command line\nUSAGE: %s <VISIT>' % os.path.basename(sys.argv[0])
        exit(usage)


    # Prepare the socket
    socket_object = prepare_socket(port=50000,backlog=5,size=4096)
    send_filename(DECam_filename[EXPNUM],socket_object,size=4096)
