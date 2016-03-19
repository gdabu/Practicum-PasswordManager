import socket
import json
import ast

# HOST = '192.168.0.28'
HOST = '142.232.169.184'
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
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.uix.button import Button

class TwoFactorLoginScreen(Screen):

    def enterKey(self, secret):
        commandData = json.dumps({"action" : "2FA_LOGIN", "secret" : secret})
        recvJsonData = self.parent.clientConnection.send_receive(commandData)

        if recvJsonData['status'] == 200:
            self.parent.current = "main_screen_online"
        else:
            self.ids.key_status.text = "Incorrect Key"
            self.parent.current = "login_screen"

        self.ids.secret_key.text = ""
        self.ids.key_status.text = ""


    def backToLogin(self):
        self.parent.current = "login_screen"


class LoginScreen(Screen):
    loggedInUser = StringProperty('')
    login_status = StringProperty('')
    twoFactor_status = BooleanProperty('')

    def login(self, username, password, connectivity):
        recvJsonData = None

        # Connect to server if connectivity switch is True
        if connectivity == True:    
            self.parent.clientConnection.connect_to_server(HOST, PORT)
            
            # If a server connection exists
            if self.parent.clientConnection.connection != None:
                self.loggedInUser = username

                commandData = json.dumps({"action" : "LOGIN", "username":username, "password":password})
                recvJsonData = self.parent.clientConnection.send_receive(commandData)

                if recvJsonData['action'] == 'LOGIN' and recvJsonData['status'] == 200:
                    self.twoFactor_status = recvJsonData['additional']['tfa_enabled']

                    if recvJsonData['additional']['tfa_enabled'] == False:
                        print recvJsonData['additional']['tfa_enabled']
                        self.login_status = ""
                        self.parent.current = "main_screen_online"
                    else:
                        print recvJsonData['additional']['tfa_enabled']
                        self.parent.current = "login_2fa_screen"

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

class AddPasswordScreen(Screen):

    def addPassword(self, new_account, new_password):
        print new_account, new_password

        if new_account == "" or new_password == "":
            self.ids.add_password_status.text = "Text Input empty"
            return

        try:
            commandData = json.dumps({"action" : "CRUD", "subaction" : "CREATE", "entry" : {"account" : new_account, "accountPassword" : new_password}})
            recvJsonData = self.parent.clientConnection.send_receive(commandData)
            self.ids.add_password_status.text = "Password Added"
            self.parent.current = "main_screen_online"

        except socket.error, e:
            self.parent.clientConnection.terminate_connection()
            self.parent.current = "login_screen"

    def backToMainMenu(self):
        self.ids.new_account.text = ""
        self.ids.new_password.text = ""
        self.ids.add_password_status.text = ""
        self.parent.current = "main_screen_online"


class MainScreenOnline(Screen):
    loggedInUser = StringProperty('')
    
    twoFactor_status = BooleanProperty('')

    passwordList = ListProperty([])
    currentAccount_pw = StringProperty('')
    currentPassword_pw = StringProperty('')
    currentId_pw = StringProperty('')
    
    def on_enter(self):
        self.ids.twofactor_switch.active = self.twoFactor_status
        
    def switchTwoFactor(self, active):
        commandData = json.dumps({"action" : "2FA_ENABLE", "enabled" : active})
        recvJsonData = self.parent.clientConnection.send_receive(commandData)

    def createPasswords(self):
        self.parent.current = "add_password_screen"

    def readPasswords(self):

        commandData = json.dumps({"action" : "CRUD", "subaction" : "READ"})
        recvJsonData = self.parent.clientConnection.send_receive(commandData)
        self.passwordList = ast.literal_eval(recvJsonData['additional']['passwords'])

    def onPasswordButtonClick(self, instance):
        
        for button in self.ids.password_list.children:
            button.background_color = (1,1,1,1)
        instance.background_color = (0.2, 0.60, 0.86, 1)

        self.currentAccount_pw = str(instance.pw_account)
        self.currentId_pw = str(instance.pw_id)
        self.currentPassword_pw = str(instance.pw_password)
        
        self.ids.password_info.text = "Account: {0}\nPassword: {1}".format(self.currentAccount_pw, self.currentPassword_pw)
        
        # Create and Add the update and delete buttons for the password
        self.ids.password_button_container.clear_widgets()

        updateButton = Button(text="UPDATE", id="password_button_update")
        deleteButton = Button(text="DELETE", id="password_button_delete")

        updateButton.bind(on_release=self.updatePasswords)
        deleteButton.bind(on_release=self.deletePasswords)

        self.ids.password_button_container.add_widget(updateButton)
        self.ids.password_button_container.add_widget(deleteButton)

    def loadPasswordList_UI(self):
        self.readPasswords()
        self.ids.password_list.clear_widgets()
        for entry in self.passwordList:

            passwordBtn = Button(text=entry['account'], background_color=(0.93,0.93,0.93,1))

            passwordBtn.apply_property(pw_username=StringProperty(entry['username']))
            passwordBtn.apply_property(pw_account=StringProperty(entry['account']))
            passwordBtn.apply_property(pw_password=StringProperty(entry['password']))
            passwordBtn.apply_property(pw_id=StringProperty(entry['id']))

            passwordBtn.bind(on_release=self.onPasswordButtonClick)

            self.ids.password_list.add_widget(passwordBtn)
        

    def updatePasswords(self, instance):
        print "updating"
        print self.currentAccount_pw
        print self.currentId_pw
        print self.currentPassword_pw
        
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
    twoFactor_status = BooleanProperty('')

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


presentation = Builder.load_file("main.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()