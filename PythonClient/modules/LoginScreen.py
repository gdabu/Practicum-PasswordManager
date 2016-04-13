import bcrypt
import json

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

class LoginScreen(Screen):
    loggedInUser = StringProperty('')
    login_status = StringProperty('')
    twoFactor_status = BooleanProperty('')

    def connect(self):
        # self.parent.clientConnection.connect_to_server(HOST, PORT)
        pass

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
