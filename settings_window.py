from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from graphics import CustomTextInput, RoundedButton, FilledBoxLayout


class SettingsWindow(BoxLayout):

    def __init__(self, dismiss=None, **kwargs):

        self.dismiss = dismiss
        super(SettingsWindow, self).__init__(**kwargs)

        text_input_box = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        self.text_input = CustomTextInput(background_color=(0.15, 0.15, 0.15, 1), foreground_color=(1, 1, 1, 1))
        text_input_box.add_widget(self.text_input)

        # Main float layout
        layout = BoxLayout(orientation = "vertical", size_hint = (1,1))

        # Top FilledBoxLayout for the buttons and label
        bottom_layout = FilledBoxLayout(orientation='horizontal', size_hint=(1, None), height=100, padding=(20, 10, 20, 10))

        # Toggle Sidebar button
        close_button = RoundedButton(text="Close", size_hint=(None, 1), size=(250, 100), radius= 25)
        bottom_layout.add_widget(close_button)
        close_button.bind(on_release=self.close_window)

        # Spacer Widget for centering the label
        bottom_layout.add_widget(Widget(size_hint=(1, 1)))  # Flexible spacer

        # New Chat button
        save_button = RoundedButton(text="Save", size_hint=(None, 1), size=(250, 100), radius= 25)
        bottom_layout.add_widget(save_button)
        save_button.bind(on_release= self.save_config)

        text = ""

        with open('config.ini', 'r') as f:
            text = f.read()
            self.text_input.text = text

        layout.add_widget(text_input_box)
        layout.add_widget(bottom_layout)

        self.add_widget(layout)

    def save_config(self, instance):
        with open('config.ini', 'w') as f:
            f.write(self.text_input.text)

        self.close_window()

    def close_window(self, instance= None):
        # Stop the settings app
        if self.dismiss:
            self.dismiss()

class SettingsApp(App):
    def __init__(self, **kwargs):
        super(SettingsApp, self).__init__(**kwargs)

    def build(self):
        settings_layout = SettingsWindow(dismiss=Popup().dismiss)
        return settings_layout

if __name__ == '__main__':
    SettingsApp().run()