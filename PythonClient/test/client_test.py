import unittest
import sys
import thread
import socket
import json

sys.path.insert(0, '../util')
sys.path.insert(0, '../../PythonServer')
sys.path.insert(0, '../../PythonServer/util')
sys.path.insert(0, '../../PythonServer/res/tls-credentials')
from ClientConnection import ClientConnection
from Server import *
from AESCipher import *

IP = '192.168.0.23'
PORT = 8000

class client_test(unittest.TestCase):

    def connect(self, IP, PORT):
        connection = ClientConnection()
        connection.connect_to_server(IP, PORT)
        return connection

    def test_client_connection_success(self):

        try:
            self.connect(IP, PORT)
        except Exception, e:
            self.assertFalse(True, 'Exception raised')
            
    def test_client_connection_failed(self):

        with self.assertRaises(error):
            self.connect(IP, PORT + 1)

    # 
    # TEST to see if the registration server response is valid
    # 
    def test_client_register(self):

        username = "unittest_username"
        password = "password"

        connection = self.connect(IP, PORT)

        response = connection.send_receive(json.dumps({"action" : "REGISTER", "username":username, "password":password}))

        if response['action'] != "REGISTER":
            self.assertFalse(True, 'Exception raised')

    def test_client_login(self):

        username = "unittest_username"
        password = "password"

        connection = self.connect(IP, PORT)
        response = connection.send_receive(json.dumps({"action" : "LOGIN", "username":username, "password":password}))


        if response['action'] != "LOGIN":
            self.assertFalse(True, 'Incorrect Action')

        if response['status'] != 200:
            self.assertFalse(True, 'Incorrect Status')

        if response['message'] != "LOGIN Successfull":
            self.assertFalse(True, 'Incorrect Message')

    def test_client_crud_password_logged_out(self):

        new_account = "unittest_account"
        new_password = "unittest_password"

        connection = self.connect(IP, PORT)

        cipher = AESCipher("nv93h50sk1zh508v");

        try:
            encrypted_password = cipher.encrypt(new_password)
        except Exception, e:
            self.assertFalse(True, e)

        response = connection.send_receive(json.dumps({"action" : "CRUD", "subaction" : "CREATE", "entry" : {"account" : new_account, "accountPassword" : encrypted_password}}))
        
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')

        response = connection.send_receive(json.dumps({"action" : "CRUD", "subaction" : "DELETE", "entry" : {"id" : 0}}))
        
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')

        response = connection.send_receive(json.dumps({"action" : "CRUD", "subaction" : "READ"}))
        
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')

        response = connection.send_receive(json.dumps({"action" : "SCAN"}))
        
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')  

    def test_client_sync_logged_out(self):
        connection = self.connect(IP, PORT)

        response = connection.send_receive(json.dumps({"action" : "SYNC", "subaction" : "PUSH", "passwords" : str([])}))
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')

        response = connection.send_receive(json.dumps({"action" : "SYNC", "subaction" : "PULL"}))
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')

        response = connection.send_receive(json.dumps({"action" : "SYNC", "subaction" : "DIFF"}))
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')

    def test_client_scan_logged_out(self):
        connection = self.connect(IP, PORT)

        response = connection.send_receive(json.dumps({"action" : "SCAN"}))
        
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')
                
    def test_client_2fa_enable_logged_out(self):
        connection = self.connect(IP, PORT)

        response = connection.send_receive(json.dumps({"action" : "2FA_ENABLE", "enabled" : "False"}))
        
        if response['status'] != 400:
            self.assertFalse(True, 'Incorrect Status')




if __name__ == '__main__':
    thread.start_new_thread(Server, (IP, PORT, '../../PythonServer/res/tls-credentials/key.pem', '../../PythonServer/res/tls-credentials/cert.pem', '../../PythonServer/logs/login.log'))
    
    unittest.main()

















