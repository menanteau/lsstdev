#!/usr/bin/env python

"""
A simple, a very simple function to serve a binary file continusly
over TCP using python socket. This script should be executed on the
server. A compannion script: client-getfile.py should be use to retrieve the file

F. Menanteau, NCSA July 2016.

"""

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
        filename = sys.argv[1]
    except:
        usage ='ERROR: Must provide filename on command line\nUSAGE: %s <filename>' % os.path.basename(sys.argv[0])
        exit(usage)

    # Prepare the socket
    socket_object = prepare_socket(port=50000,backlog=5,size=4096)
    send_filename(filename,socket_object,size=4096)
