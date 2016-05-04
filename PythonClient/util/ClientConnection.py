import json
from socket import *
from ssl import *

class ClientConnection():
    connection = None
    clientSocket = None
    server_address = None

    def validate_message(self, message):
        json.loads(message)

    def connect_to_server(self, ip, port):
        self.clientsock = socket(AF_INET, SOCK_STREAM)
        self.clientSocket = wrap_socket(self.clientsock, ssl_version=PROTOCOL_TLSv1, cert_reqs=CERT_NONE)
        self.server_address = (ip, port)
        self.clientSocket.connect(self.server_address)
        self.connection = True
        return self.connection
    
    def print_message(self, message):
        print message

    def send_command(self, message):
        self.validate_message(message)
        if self.connection:
            self.clientSocket.sendall((message + "\n").encode())

    def tlsReceive(self, clientsock, bufferSize):
        chunk = ""
        data = ""
        
        while 1:
            chunk = clientsock.recv(bufferSize)
            data += chunk
            
            if not data or chunk[len(chunk) - 1] == "\n":
                print data
                return data.decode()

    def receive_response(self):

        data = self.tlsReceive(self.clientSocket, 4096)
                
        # if client disconnects
        if not data:
            self.connection = False
            self.clientSocket.close()
            raise socket.error
        else:
            return json.loads(data.decode().rstrip('\n'))


    def send_receive(self, message):
        self.send_command(message)
        response = self.receive_response()
        return response

    def terminate_connection(self):
        self.connection = None
        self.clientSocket = None