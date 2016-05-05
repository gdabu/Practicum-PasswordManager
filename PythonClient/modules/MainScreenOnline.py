import json
from AESCipher import *

from PasswordButton import PasswordButton
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.uix.button import Button

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
        print recvJsonData

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

        # self.ids.password_button_container.add_widget(updateButton)
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

