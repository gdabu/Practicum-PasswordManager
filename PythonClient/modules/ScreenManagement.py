import MySQLdb
import socket

from kivy.uix.screenmanager import ScreenManager

from ClientConnection import ClientConnection

HOST = '192.168.0.23'
PORT = 8000

# TODO: Kivy instantiates TWO ScreenManagement objects, and therefore creates to connections. 
# @param init is used to prevent the second ScnreenManagement instance from making a connection
init = 0

class ScreenManagement(ScreenManager):
    clientConnection = None
    connected = None
    db = None
    cursor = None

    def __init__(self, **kwargs):
        super(ScreenManager, self).__init__(**kwargs)
        
        global init

        if init == 0:
            
            try:
                self.clientConnection = ClientConnection()
                self.connected = self.clientConnection.connect_to_server(HOST, PORT)
            except socket.error as e:
                self.connected = None

            self.db = MySQLdb.connect(host="localhost", user="root", passwd="bastard11", db="pwd_manager")
            self.cursor = self.db.cursor()

        init = init + 1

