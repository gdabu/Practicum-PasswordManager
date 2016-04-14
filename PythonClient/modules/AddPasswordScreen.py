import json
import socket

from AESCipher import *
from PasswordCrud import *
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

class AddPasswordScreen(Screen):
    loggedInUser = StringProperty('')

    def addPassword(self, new_account, new_password):
        print new_account, new_password

        if new_account == "" or new_password == "":
            self.ids.add_password_status.text = "Text Input Empty"
            return

        try:
            cipher = AESCipher("nv93h50sk1zh508v");

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

        return recvJsonData

    def screenRedirect(self, screen):
        self.ids.new_account.text = ""
        self.ids.new_password.text = ""
        self.ids.add_password_status.text = ""
        self.parent.current = screen

