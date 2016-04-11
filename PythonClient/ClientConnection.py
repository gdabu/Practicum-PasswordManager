import json
from socket import *
from ssl import *

class ClientConnection():
    connection = None
    clientSocket = None
    server_address = None

    def connect_to_server(self, ip, port):
        try:
            self.clientsock = socket(AF_INET, SOCK_STREAM)
            # self.clientSocket.settimeout(5)
            self.clientSocket = wrap_socket(self.clientsock, ssl_version=PROTOCOL_TLSv1, cert_reqs=CERT_NONE)
            self.server_address = (ip, port)
            self.clientSocket.connect(self.server_address)
            self.connection = True
        except error, e:
            print "socket error: ", e
            self.connection = None
        return self.connection
    
    def print_message(self, message):
        print message

    def send_command(self, message):
        if self.connection:
            self.clientSocket.sendall((message + "\n").encode())

    def receive_response(self):
        # data = self.clientSocket.recv(4096)
        chunk = ""
        message = ""
        end = False
        while end == False:
            chunk = self.clientSocket.recv(4096)
            message += chunk
            for char in chunk:
                if char == "\n" or not chunk:
                    end = True
        if not message:
            self.connection = False
            self.clientSocket.close()
            raise socket.error
        else:
            return json.loads(message.decode().rstrip('\n'))

    def send_receive(self, message):
        self.send_command(message)
        return self.receive_response()

    def terminate_connection(self):
        self.connection = None
        self.clientSocket = None