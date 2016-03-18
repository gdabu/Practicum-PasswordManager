import socket
import json
import ast

HOST = '192.168.0.122'
PORT = 8000

class ClientConnection():
    connection = None
    clientSocket = None
    server_address = None

    def connect_to_server(self, ip, port):
        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_address = (ip, port)
            self.clientSocket.connect(self.server_address)
            self.connection = True
        except socket.error, e:
            print "socket error: ", e
            self.connection = None
    
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

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.button import Button


class LoginScreen(Screen):
    username = StringProperty('')
    login_status = StringProperty('')

    def login(self, username, password, connectivity):
        recvJsonData = None

        # Connect to server if connectivity switch is True
        if connectivity == True:    
            self.parent.clientConnection.connect_to_server(HOST, PORT)
            
            # If a server connection exists
            if self.parent.clientConnection.connection != None:
                self.username = username

                commandData = json.dumps({"action" : "LOGIN", "username":username, "password":password})
                recvJsonData = self.parent.clientConnection.send_receive(commandData)

                if recvJsonData['action'] == 'LOGIN' and recvJsonData['status'] == 200:
                    self.login_status = ""
                    self.parent.current = "main_screen_online"

                else:
                    self.login_status = "Unsuccessful Login"
                    self.parent.clientConnection.print_message("Unsuccessful Login")
            else:
                self.login_status = "Unable to Connect"    
                self.parent.clientConnection.print_message("Unable to Connect")


                # self.parent.print_message(self.data)

        elif connectivity == False:

            self.username = username
            self.parent.current = "main_screen_offline"

class MainScreenOnline(Screen):
    loggedInUser = StringProperty('')
    passwordList = ListProperty([])

    currentAccount_pw = StringProperty('')
    currentPassword_pw = StringProperty('')
    currentId_pw = StringProperty('')

    def createPasswords(self):
        try:
            commandData = json.dumps({"action" : "CRUD", "subaction" : "CREATE", "entry" : {"account" : "fucknut", "accountPassword" : "bitchfuck"}})
            recvJsonData = self.parent.clientConnection.send_receive(commandData)
            self.loadPasswordList_UI()
        except socket.error, e:
            self.parent.clientConnection.terminate_connection()
            self.parent.current = "login_screen"
        # self.parent.clientConnection.send_command("create")
        # self.parent.clientConnection.print_message(self.parent.clientConnection.receive_response())
        
        pass

    def readPasswords(self):
        
        commandData = json.dumps({"action" : "CRUD", "subaction" : "READ"})
        recvJsonData = self.parent.clientConnection.send_receive(commandData)
        self.passwordList = ast.literal_eval(recvJsonData['additional']['passwords'])
        print self.passwordList

    def onPasswordButtonClick(self, instance):
        print('The button <%s> is being pressed' % instance.text)

        self.currentAccount_pw = str(instance.pw_account)
        self.currentId_pw = str(instance.pw_id)
        self.currentPassword_pw = str(instance.pw_password)
        
        self.ids.password_info.text = "Account: {0}\nPassword: {1}".format(self.currentAccount_pw, self.currentPassword_pw)
        
        self.ids.password_button_container.clear_widgets()
        # self.ids.password_info_container.add_widget
        # self.ids.password_info_container.add_widget
        

        updateButton = Button(text="UPDATE", id="password_button_update")
        deleteButton = Button(text="DELETE", id="password_button_delete")

        updateButton.bind(on_press=self.updatePasswords)
        deleteButton.bind(on_press=self.deletePasswords)

        self.ids.password_button_container.add_widget(updateButton)
        self.ids.password_button_container.add_widget(deleteButton)

    def loadPasswordList_UI(self):
        self.readPasswords()
        self.ids.password_list.clear_widgets()
        for entry in self.passwordList:

            passwordBtn = Button(text=entry['account'])

            passwordBtn.apply_property(pw_username=StringProperty(entry['username']))
            passwordBtn.apply_property(pw_account=StringProperty(entry['account']))
            passwordBtn.apply_property(pw_password=StringProperty(entry['password']))
            passwordBtn.apply_property(pw_id=StringProperty(entry['id']))

            passwordBtn.bind(on_press=self.onPasswordButtonClick)


            # TEST PRINT
            # print passwordBtn.pw_account
            # print passwordBtn.pw_id
            # print passwordBtn.pw_password
            # print passwordBtn.pw_username

            self.ids.password_list.add_widget(passwordBtn)
        

    def updatePasswords(self, instance):
        print "updating"
        print self.currentAccount_pw
        print self.currentId_pw
        print self.currentPassword_pw
        # self.parent.clientConnection.send_command("update")
        # self.parent.clientConnection.print_message(self.parent.clientConnection.receive_response())
        
        pass

    def deletePasswords(self, instance):
        print "deleting"
        print self.currentAccount_pw
        print self.currentId_pw
        print self.currentPassword_pw
        try:
            commandData = json.dumps({"action" : "CRUD", "subaction" : "DELETE", "entry" : {"id" : self.currentId_pw}})
            recvJsonData = self.parent.clientConnection.send_receive(commandData)
            self.loadPasswordList_UI()
            self.ids.password_button_container.clear_widgets()
            self.ids.password_info.text = ""
        except socket.error, e:
            self.parent.clientConnection.terminate_connection()
            self.parent.current = "login_screen"

    def syncPasswords(self):
        
        # self.parent.clientConnection.send_command("sync")
        pass

    def logout(self):
        self.loggedInUser = ""
        self.parent.clientConnection.terminate_connection()
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
    clientConnection = None

    def __init__(self, **kwargs):
        super(ScreenManager, self).__init__(**kwargs)
        self.clientConnection = ClientConnection()

    # connection = None
    # clientSocket = None
    # server_address = None

    # def connect_to_server(self):
    #     try:
    #         self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         self.server_address = ('192.168.0.28', 8000)
    #         self.clientSocket.connect(self.server_address)
    #         self.connection = True
    #     except socket.error, e:
    #         self.connection = None
    
    # def print_message(self, message):
    #     print message


    # def send_command(self, message):
    #     try:
    #         if self.connection:
    #             self.clientSocket.sendall(message)
    #     except socket.error, e:
    #         print "Raised Socket Exception: ", e
    #         self.connection = False
    #         self.clientSocket.close()
    #         self.current = "login_screen"

    # def receive_response(self):
    #     data = self.clientSocket.recv(4096)
    #     if not data:
    #         self.connection = False
    #         self.clientSocket.close()
    #         self.current = "login_screen"
    #         return "Connection Ended"
    #     else:
    #         return json.loads(data.rstrip())

    # def send_receive(self, message):
    #     self.send_command(message)
    #     return self.receive_response()


    

presentation = Builder.load_file("main.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()