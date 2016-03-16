# #install_twisted_rector must be called before importing the reactor
# from kivy.support import install_twisted_reactor
# install_twisted_reactor()


# #A simple Client that send messages to the echo server
# from twisted.internet import reactor, protocol


# class EchoClient(protocol.Protocol):
#     def connectionMade(self):
#         self.factory.screen_manager.on_connection(self.transport)
#         self.factory.screen_manager.print_message("connection succeeded")

#     def dataReceived(self, data):
#         self.factory.screen_manager.print_message("RECEIVED: " + data)


# class EchoFactory(protocol.ClientFactory):
#     protocol = EchoClient
#     screen_manager = None

#     def __init__(self, screen_manager):
#         self.screen_manager = screen_manager

#     def clientConnectionLost(self, conn, reason):
#         self.screen_manager.print_message("connection lost")

#     def clientConnectionFailed(self, conn, reason):
#         self.screen_manager.print_message("connection failed")

import socket

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty


class LoginScreen(Screen):
    username = StringProperty('')

    def login(self, username, password, connectivity):
        
        if connectivity == True:
            
            self.parent.connect_to_server()

            print self.parent.connection

            if self.parent.connection != None:
                self.username = username

                self.parent.current = "main_screen_online"
            
        elif connectivity == False:

            self.username = username
            self.parent.current = "main_screen_offline"

class MainScreenOnline(Screen):
    loggedInUser = StringProperty('')

    def createPasswords(self):
        print self.loggedInUser
        self.parent.send_command("create")
        self.parent.print_message(self.parent.receive_response())
        
        pass

    def readPasswords(self):
        print self.loggedInUser
        self.parent.send_command("read")
        self.parent.print_message(self.parent.receive_response())
        
        pass

    def updatePasswords(self):
        print self.loggedInUser
        self.parent.send_command("update")
        self.parent.print_message(self.parent.receive_response())
        
        pass

    def deletePasswords(self):
        print self.loggedInUser
        self.parent.send_command("delete")
        self.parent.print_message(self.parent.receive_response())
        
        pass

    def syncPasswords(self):
        print self.loggedInUser
        self.parent.send_command("sync")
        pass

    def logout(self):
        self.loggedInUser = ""
        self.parent.current = "login_screen"
        pass

class MainScreenOffline(Screen):
    loggedInUser = StringProperty('')

    def createPasswords():
        pass

    def readPasswords():
        pass

    def updatePasswords():
        pass

    def deletePasswords():
        pass

class ScreenManagement(ScreenManager):
    connection = None
    clientSocket = None
    server_address = None


    def connect_to_server(self):
        # reactor.connectTCP('localhost', 8000, EchoFactory(self), timeout=30)
        # print "fucka"
        # 
        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_address = ('localhost', 8000)
            self.clientSocket.connect(self.server_address)
            self.connection = True
        except socket.error, e:

            self.connection = None
        
    # def on_connection(self, connection):
    #     self.connection = connection
    
    def print_message(self, message):
        print message

    # def send_message(self, *args):
    #     msg = self.textbox.text
    #     if msg and self.connection:
    #         self.connection.write(str(self.textbox.text))
    #         self.textbox.text = ""

    def send_command(self, message):
        try:
            if self.connection:
                self.clientSocket.sendall(message)

        except socket.error, e:
            print "Raised Socket Exception: ", e
            self.connection = False
            self.clientSocket.close()
            self.current = "login_screen"

    def receive_response(self):
        data = self.clientSocket.recv(4096)
        if not data:
            self.connection = False
            self.clientSocket.close()
            self.current = "login_screen"
            return "Connection Ended"
        else:
            return data


    

presentation = Builder.load_file("main.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()