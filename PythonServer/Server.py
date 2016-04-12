import argparse
import MySQLdb
import thread
import sys

sys.path.insert(0, './util')

from socket import *
from ssl import *
from log import *
from ConnectionHandler import *

if __name__=='__main__':

    cmdParser = argparse.ArgumentParser(description="8505A1-CovertChannel Client")
    cmdParser.add_argument('-i','--IP',dest='IP', help='HOST Ip', required=True)
    cmdParser.add_argument('-p','--PORT',dest='PORT', help='HOST Port', required=True)
    args = cmdParser.parse_args();

    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind((args.IP, int(args.PORT)))
    serversock.listen(5)
    tls_server = wrap_socket(serversock, ssl_version=PROTOCOL_TLSv1, cert_reqs=CERT_NONE, server_side=True, keyfile='./res/tls-credentials/key.pem', certfile='./res/tls-credentials/cert.pem')

    db = MySQLdb.connect(host="localhost", user="root", passwd="", db="pwd_manager")
    logger = initLogger()

    while 1:
        print '>> Server Listening on Port: ', args.PORT
        clientsock, addr = tls_server.accept()
        print '>> Connected to: ', addr
        thread.start_new_thread(handler, (clientsock, addr, db, logger))