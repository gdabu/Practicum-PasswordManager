import json
import ast
import MySQLdb
import bcrypt
import socket

from ClientConnection import ClientConnection
from PasswordCrud import *
from AesEncryption import *
from AESCipher import *

HOST = '192.168.0.245'
# HOST = '142.232.169.214'
# HOST = '142.232.169.184'
PORT = 8000

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.uix.button import Button, Label

class NetworkScreen(Screen):
    hostList = ListProperty([])
    loggedInUser = StringProperty('')

    def getHosts(self):
        try:
            commandData = json.dumps({"action" : "SCAN"})
            recvJsonData = self.parent.clientConnection.send_receive(commandData)
            self.hostList = recvJsonData['additional']['hosts']
        except Exception, e:
            raise
        else:
            pass
        finally:
            pass



    def loadHostList_UI(self):
        
        self.ids.host_list.clear_widgets()
        self.getHosts()
        
        for entry in self.hostList:
            print entry
            hostBtn = Button(text=entry['host'], background_color=(0.93,0.93,0.93,1))

            # passwordBtn = PasswordButton(text=entry['account'], background_color=(0.93,0.93,0.93,1))

            # passwordBtn.pw_username = entry['username']
            # passwordBtn.pw_account=entry['account']
            # passwordBtn.pw_password=entry['password']
            # passwordBtn.pw_id=entry['id']

            # passwordBtn.bind(on_release=self.onPasswordButtonClick)

            self.ids.host_list.add_widget(hostBtn)


class SyncScreen(Screen):
    loggedInUser = StringProperty('')
    localPasswordList = ListProperty([])
    remotePasswordList = ListProperty([])

    def syncWithRemote(self):
        print "sync with remote"
        commandData = json.dumps({"action" : "SYNC", "subaction" : "PULL"})
        recvJsonData = self.parent.clientConnection.send_receive(commandData)

        self.parent.cursor.execute("delete from passwords where username='" + self.loggedInUser + "'" )
        pushPasswordData = recvJsonData['additional']['passwords']

        for password in pushPasswordData:
            self.parent.cursor.execute("insert into passwords (username, account, password) values ('" + self.loggedInUser + "', '" + password['account'] + "', '" + password['password'] + "')" )

        self.parent.db.commit()

        self.loadPasswordList_UI()

    def syncWithLocal(self):
        print "sync with local"
        commandData = json.dumps({"action" : "SYNC", "subaction" : "PUSH", "passwords" : str(self.localPasswordList)})
        recvJsonData = self.parent.clientConnection.send_receive(commandData)

        self.loadPasswordList_UI()

    def onPasswordButtonClick(self, instance):
        
        for button in self.ids.local_password_list.children:
            button.background_color = (1,1,1,1)
        for button in self.ids.remote_password_list.children:
            button.background_color = (1,1,1,1)

        instance.background_color = (0.8, 0.8, 0.8, 1)

        self.currentAccount_pw = str(instance.pw_account)
        self.currentId_pw = str(instance.pw_id)
        self.currentPassword_pw = str(instance.pw_password)
        
        self.ids.password_info.text = "Account: {0}\nPassword: {1}".format(self.currentAccount_pw, self.currentPassword_pw)
        self.ids.password_location.text = "Location: {0}".format(instance.pw_location)

    def readPasswords(self):
        commandData = json.dumps({"action" : "CRUD", "subaction" : "READ"})
        recvJsonData = self.parent.clientConnection.send_receive(commandData)
        self.remotePasswordList = recvJsonData['additional']['passwords']

        passwordList = PasswordRead(self.parent.db, self.loggedInUser)
        self.localPasswordList = passwordList
    
    def loadPasswordList_UI(self):
        self.readPasswords()
        self.ids.remote_password_list.clear_widgets()
        self.ids.local_password_list.clear_widgets()

        self.ids.remote_password_list.add_widget(Label(text="Remote Password List"))
        self.ids.local_password_list.add_widget(Label(text="Local Password List"))

        for entry in self.localPasswordList:

            passwordBtn = PasswordButton(text=entry['account'], background_color=(0.93,0.93,0.93,1))

            passwordBtn.pw_username = entry['username']
            passwordBtn.pw_account=entry['account']
            try:
                passwordBtn.pw_password=cipher.decrypt(entry['password'])
            except Exception, e:
                print e
                passwordBtn.pw_password="Unable to Decrypt"
            passwordBtn.pw_id=entry['id']
            passwordBtn.pw_id=entry['id']

            passwordBtn.pw_location = "Local"

            passwordBtn.bind(on_release=self.onPasswordButtonClick)

            self.ids.local_password_list.add_widget(passwordBtn)

        for entry in self.remotePasswordList:

            passwordBtn = PasswordButton(text=entry['account'], background_color=(0.93,0.93,0.93,1))

            passwordBtn.pw_username = entry['username']
            passwordBtn.pw_account=entry['account']
            try:
                passwordBtn.pw_password=cipher.decrypt(entry['password'])
            except Exception, e:
                print e
                passwordBtn.pw_password="Unable to Decrypt"
            passwordBtn.pw_id=entry['id']
            passwordBtn.pw_id=entry['id']

            passwordBtn.pw_location = "Remote"

            passwordBtn.bind(on_release=self.onPasswordButtonClick)

            self.ids.remote_password_list.add_widget(passwordBtn)

class RegistrationScreen(Screen):
    def register(self, username, password):

        if username == "" or password == "":
            self.ids.registration_status.text = "Text Input Empty"
            return

        # connectivity = self.parent.clientConnection.connect_to_server(HOST, PORT)

        if self.parent.clientConnection.connection != None:

            commandData = json.dumps({"action" : "REGISTER", "username":username, "password":password})
            recvJsonData = self.parent.clientConnection.send_receive(commandData)

            if recvJsonData['status'] == 200:
                self.parent.cursor.execute("insert into users (username, password) values ('" + recvJsonData['additional']['username'] + "', '" + recvJsonData['additional']['password'] + "')")
                self.parent.db.commit()
                self.parent.current = "login_screen"
            else:
                self.ids.registration_status.text = "Unable to register"
        else:
            self.ids.registration_status.text = "Unable to connect to server"

        self.ids.new_user.text = ""
        self.ids.new_password.text = ""
    
    def backToLogin(self):
        self.parent.current = "login_screen"

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

    def connect(self):
        self.parent.clientConnection.connect_to_server(HOST, PORT)

    def login(self, username, password, connectivity):
        recvJsonData = None

        # Connect to server if connectivity switch is True
        if connectivity == True:    
            
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
            self.parent.cursor.execute("select * from users where username = '" + username + "'")
            user = self.parent.cursor.fetchall()
            try:
                if len(user) == 0:
                    print "User not found"
                else:
                    for row in user:
                        if row[1] == bcrypt.hashpw(password.encode('utf-8'), row[1]):
                            self.loggedInUser = row[0]
                            self.login_status = ""
                            self.parent.current = "main_screen_offline"
                            return
                        break
            except ValueError,e:
                print e
            
            self.login_status = "Unsuccessful Login"
            return


    def goToRegistrationScreen(self):
        if self.parent.clientConnection.connection != None:
            self.parent.current = "registration_screen"
        else:
            self.login_status = "Unable to Connect" 

class AddPasswordScreen(Screen):
    loggedInUser = StringProperty('')

    def addPassword(self, new_account, new_password):
        print new_account, new_password

        if new_account == "" or new_password == "":
            self.ids.add_password_status.text = "Text Input Empty"
            return

        try:
            cipher = AESCipher("nv93h50sk1zh508v");

            # encrypted = cipher.encrypt("HELLO IM A FUCKING CUNT NUGGET WHORE BITCH. IM HERE TO STEAL YOUR WIFE. HELLO NIGGER");
            try:
                encrypted_password = cipher.encrypt(new_password)
            except Exception, e:
                self.ids.add_password_status.text = "Unable To Encrypt Password"
                return
            
            commandData = json.dumps({"action" : "CRUD", "subaction" : "CREATE", "entry" : {"account" : new_account, "accountPassword" : encrypted_password}})
            recvJsonData = self.parent.clientConnection.send_receive(commandData)
            PasswordCreate(self.parent.db, self.loggedInUser, new_account, encrypted_password)
            self.ids.add_password_status.text = "Password Added"
            self.screenRedirect("main_screen_online")

        except socket.error, e:
            self.parent.clientConnection.terminate_connection()
            self.parent.current = "login_screen"

    def screenRedirect(self, screen):
        self.ids.new_account.text = ""
        self.ids.new_password.text = ""
        self.ids.add_password_status.text = ""
        self.parent.current = screen

class AddPasswordScreenLocal(Screen):
    loggedInUser = StringProperty('')

    def addPasswordLocal(self, new_account, new_password):
        if new_account == "" or new_password == "":
            self.ids.add_password_status.text = "Text Input Empty"
            return

        PasswordCreate(self.parent.db, self.loggedInUser, new_account, new_password)
        self.ids.add_password_status.text = "Password Added"
        self.screenRedirect("main_screen_offline")

    def screenRedirect(self, screen):
        self.ids.new_account.text = ""
        self.ids.new_password.text = ""
        self.ids.add_password_status.text = ""
        self.parent.current = screen

class PasswordButton(Button):
    pw_username = None
    pw_account = None
    pw_password = None
    pw_id = None

    def __init__(self, **kwargs):
        super(PasswordButton, self).__init__(**kwargs)

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

    def goToAddPasswordScreen(self):
        self.parent.current = "add_password_screen"

    def readPasswords(self):

        commandData = json.dumps({"action" : "CRUD", "subaction" : "READ"})
        recvJsonData = self.parent.clientConnection.send_receive(commandData)
        self.passwordList = recvJsonData['additional']['passwords']

    def onPasswordButtonClick(self, instance):
        
        for button in self.ids.password_list.children:
            button.background_color = (1,1,1,1)
        instance.background_color = (0.8, 0.8, 0.8, 1)

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
        cipher = AESCipher("nv93h50sk1zh508v");
        for entry in self.passwordList:

            passwordBtn = PasswordButton(text=entry['account'], background_color=(0.93,0.93,0.93,1))

            passwordBtn.pw_username = entry['username']
            passwordBtn.pw_account=entry['account']
            try:
                passwordBtn.pw_password=cipher.decrypt(entry['password'])
            except Exception, e:
                print e
                passwordBtn.pw_password="Unable to Decrypt"
            passwordBtn.pw_id=entry['id']
            passwordBtn.pw_id=entry['id']

            passwordBtn.bind(on_release=self.onPasswordButtonClick)

            self.ids.password_list.add_widget(passwordBtn)
        

    def updatePasswords(self, instance):
        print "updating"
        print self.currentAccount_pw
        print self.currentId_pw
        print self.currentPassword_pw
        
        pass

    # NOTE: Deleting passwords both remotely and locally will not work because the password ID numbers wont 
    # always be matching. Need to delete by account name, which means the account field needs to become unique.
    def deletePasswords(self, instance):
        print "deleting"
        print self.currentAccount_pw
        print self.currentId_pw
        print self.currentPassword_pw
        try:
            commandData = json.dumps({"action" : "CRUD", "subaction" : "DELETE", "entry" : {"id" : self.currentId_pw}})
            recvJsonData = self.parent.clientConnection.send_receive(commandData)
            # PasswordDelete(self.parent.db, self.loggedInUser, self.currentId_pw)
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

    passwordList = ListProperty([])
    currentAccount_pw = StringProperty('')
    currentPassword_pw = StringProperty('')
    currentId_pw = StringProperty('')
    
    def goToAddPasswordScreen(self):
        self.parent.current = "add_password_screen_local"

    def readPasswords(self):
        passwordList = PasswordRead(self.parent.db, self.loggedInUser)
        self.passwordList = passwordList

    def onPasswordButtonClick(self, instance):
        
        for button in self.ids.password_list.children:
            button.background_color = (1,1,1,1)
        instance.background_color = (0.8, 0.8, 0.8, 1)

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
        cipher = AESCipher("nv93h50sk1zh508v");
        for entry in self.passwordList:

            passwordBtn = PasswordButton(text=entry['account'], background_color=(0.93,0.93,0.93,1))

            passwordBtn.pw_username = entry['username']
            passwordBtn.pw_account=entry['account']
            try:
                passwordBtn.pw_password=cipher.decrypt(entry['password'])
            except Exception, e:
                print e
                passwordBtn.pw_password="Unable to Decrypt"
            passwordBtn.pw_id=entry['id']

            passwordBtn.bind(on_release=self.onPasswordButtonClick)

            self.ids.password_list.add_widget(passwordBtn)
        
    def updatePasswords(self, instance):
        print "updating"
        print self.currentAccount_pw
        print self.currentId_pw
        print self.currentPassword_pw
        
        pass

    def deletePasswords(self, instance):
        PasswordDelete(self.parent.db, self.loggedInUser, self.currentId_pw)
        self.loadPasswordList_UI()
        self.ids.password_button_container.clear_widgets()
        self.ids.password_info.text = ""

    def syncPasswords(self):
        
        # self.parent.clientConnection.send_command("sync")
        pass

    def logout(self):
        self.loggedInUser = ""
        self.parent.clientConnection.terminate_connection()
        self.parent.current = "login_screen"
        pass

class ScreenManagement(ScreenManager):
    clientConnection = None
    connected = None
    db = None
    cursor = None

    def __init__(self, **kwargs):
        super(ScreenManager, self).__init__(**kwargs)
        self.clientConnection = ClientConnection()
        self.connected = self.clientConnection.connect_to_server(HOST, PORT)
        self.db = MySQLdb.connect(host="localhost", user="root", passwd="bastard11", db="pwd_manager")
        self.cursor = self.db.cursor()
        

        print self.db
        print self.cursor

presentation = Builder.load_file("main.kv")

class MainApp(App):
    def build(self):
        return presentation

if __name__ == '__main__':
    MainApp().run()