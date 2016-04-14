import argparse
import MySQLdb
import thread
import sys

sys.path.insert(0, './util')

from socket import *
from ssl import *
from log import *
from ConnectionHandler import *

class Server():

    def __init__(self, IP, PORT, keyPath, certPath, logPath):
        serversock = socket(AF_INET, SOCK_STREAM)
        serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serversock.bind((IP, int(PORT)))
        serversock.listen(5)
        tls_server = wrap_socket(serversock, ssl_version=PROTOCOL_TLSv1, cert_reqs=CERT_NONE, server_side=True, keyfile=keyPath, certfile=certPath)

        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="pwd_manager")
        logger = initLogger(logPath)

        while 1:
            print '>> Server Listening on Port: ', PORT
            try:
                clientsock, addr = tls_server.accept()
                print '>> Connected to: ', addr
                thread.start_new_thread(handler, (clientsock, addr, db, logger))
            except SSLError, e:
                print e


if __name__=='__main__':

    cmdParser = argparse.ArgumentParser(description="MajorKey Server")
    cmdParser.add_argument('-i','--IP',dest='IP', help='HOST Ip', required=True)
    cmdParser.add_argument('-p','--PORT',dest='PORT', help='HOST Port', required=True)
    args = cmdParser.parse_args();

    server = Server(args.IP, args.PORT, './res/tls-credentials/key.pem', './res/tls-credentials/cert.pem', './logs/login.log')
        