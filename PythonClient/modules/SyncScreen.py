import json
from AESCipher import *
from PasswordCrud import *

from PasswordButton import PasswordButton

from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

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
        cipher = AESCipher("nv93h50sk1zh508v");
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

