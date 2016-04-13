import json

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

class RegistrationScreen(Screen):
    def register(self, username, password):

        if username == "" or password == "":
            self.ids.registration_status.text = "Text Input Empty"
            return

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

