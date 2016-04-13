from kivy.uix.button import Button

class PasswordButton(Button):
    pw_username = None
    pw_account = None
    pw_password = None
    pw_id = None

    def __init__(self, **kwargs):
        super(PasswordButton, self).__init__(**kwargs)
