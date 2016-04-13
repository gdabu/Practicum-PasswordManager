import json


from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

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