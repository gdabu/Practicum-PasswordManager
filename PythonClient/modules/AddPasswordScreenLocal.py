import socket
from AESCipher import *
from PasswordCrud import *
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

class AddPasswordScreenLocal(Screen):
    loggedInUser = StringProperty('')

    def addPasswordLocal(self, new_account, new_password):
        if new_account == "" or new_password == "":
            self.ids.add_password_status.text = "Text Input Empty"
            return

        cipher = AESCipher("nv93h50sk1zh508v");

        try:
            encrypted_password = cipher.encrypt(new_password)
        except Exception, e:
            self.ids.add_password_status.text = "Unable To Encrypt Password"
            return

        PasswordCreate(self.parent.db, self.loggedInUser, new_account, encrypted_password)
        self.ids.add_password_status.text = "Password Added"
        self.screenRedirect("main_screen_offline")

    def screenRedirect(self, screen):
        self.ids.new_account.text = ""
        self.ids.new_password.text = ""
        self.ids.add_password_status.text = ""
        self.parent.current = screen

