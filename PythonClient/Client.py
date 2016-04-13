
# import ast
# import bcrypt

import sys
sys.path.insert(0, './util')

from kivy.app import App
from kivy.lang import Builder


from MainScreenOffline import MainScreenOffline
from MainScreenOnline import MainScreenOnline
from NetworkScreen import NetworkScreen
from SyncScreen import SyncScreen
from RegistrationScreen import RegistrationScreen
from TwoFactorLoginScreen import TwoFactorLoginScreen
from LoginScreen import LoginScreen
from AddPasswordScreen import AddPasswordScreen
from AddPasswordScreenLocal import AddPasswordScreenLocal
from PasswordButton import PasswordButton
from ScreenManagement import ScreenManagement

class Client(App):
    def build(self):
        return Builder.load_file("./kivy/main.kv")

if __name__ == '__main__':
    Client().run()