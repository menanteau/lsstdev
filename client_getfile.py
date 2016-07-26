#!/usr/bin/env python

import socket
import sys
import os

BFSIZE = 2048

def prepare_socket(remote_host,port=50000):

    localhost = socket.gethostname()     # Get local machine name to present ourselves

    # Create socket object
    s = socket.socket()    
    s.connect((remote_host, port))
    s.send("Hello server from: %s" % localhost)
    return s

def retrieve_filename(socket_object):

    s = socket_object
    
    # Get the name of the filename from the server
    filename = s.recv(BFSIZE)

    # Define the local name
    recv_filename = "rec_%s" % filename
    print "Will write to file: %s" % recv_filename

    with open(recv_filename, 'wb') as f:
        while True:
            sys.stdout.write('\rreceiving data...')
            sys.stdout.flush()
            data = s.recv(BFSIZE)
            if not data:
                break
            # write data to a file
            f.write(data)

        f.close()
        s.close()
        print "\n"
        print "Successfully got the file: %s" % filename
        print 'connection closed... bye'

    return

if __name__ == "__main__":

    # Simple command line option to avoid using argparse
    try:
        remote_host = sys.argv[1]
    except:
        usage ='ERROR: Must provide remote hostname command line\nUSAGE: %s <remote_hostname>' % os.path.basename(sys.argv[0])
        exit(usage)

    # Get the socket
    s = prepare_socket(remote_host,port=50000)
    retrieve_filename(s)
