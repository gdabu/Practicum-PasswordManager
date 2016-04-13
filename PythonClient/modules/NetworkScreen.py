import json
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty

class NetworkScreen(Screen):
    hostList = ListProperty([])
    loggedInUser = StringProperty('')

    def getHosts(self):
        try:
            commandData = json.dumps({"action" : "SCAN"})
            recvJsonData = self.parent.clientConnection.send_receive(commandData)
            self.hostList = recvJsonData['additional']['hosts']
        except Exception, e:
            print e
            raise

    def loadHostList_UI(self):
        
        self.ids.host_list.clear_widgets()
        self.getHosts()
        
        for entry in self.hostList:
            print entry
            hostBtn = Button(text=entry['host'], background_color=(0.93,0.93,0.93,1))

            self.ids.host_list.add_widget(hostBtn)
