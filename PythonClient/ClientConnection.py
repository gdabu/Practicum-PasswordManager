import socket
import json

class ClientConnection():
    connection = None
    clientSocket = None
    server_address = None

    def connect_to_server(self, ip, port):
        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.settimeout(5)
            self.server_address = (ip, port)
            self.clientSocket.connect(self.server_address)
            self.connection = True
        except socket.error, e:
            print "socket error: ", e
            self.connection = None
        return self.connection
    
    def print_message(self, message):
        print message

    def send_command(self, message):
        if self.connection:
            self.clientSocket.sendall(message)

    def receive_response(self):
        data = self.clientSocket.recv(4096)
        if not data:
            self.connection = False
            self.clientSocket.close()
            raise socket.error
        else:
            return json.loads(data.rstrip())

    def send_receive(self, message):
        self.send_command(message)
        return self.receive_response()

    def terminate_connection(self):
        self.connection = None
        self.clientSocket = None