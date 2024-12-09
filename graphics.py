from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from app_state import ApplicationState as appst
import re
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import HoverBehavior
import os
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import platform
from kivy.core.clipboard import Clipboard
from kivy.uix.popup import Popup
from app_contracts import ChatBotApp


class CustomLabel(Label):
    pass


class CustomTextInput(TextInput):

        def keyboard_on_key_down(self, window, keycode, text, modifiers):

            if platform.system() == 'Windows':
                self.modifier_key = 'ctrl'
            elif platform.system() == 'Darwin':  # 'Darwin' is the system name for macOS
                self.modifier_key = 'alt'
            else:
                # Default to 'ctrl' for other operating systems
                self.modifier_key = 'ctrl'

            key = keycode[1]

            if (self.modifier_key in modifiers):
                if key == 'backspace':
                    # Handle Ctrl+Backspace to delete the previous word
                    cursor_pos = self.cursor_index()
                    if cursor_pos > 0:
                        # Find the start of the previous word
                        start_pos = cursor_pos
                        while start_pos > 0 and self.text[start_pos - 1].isspace():
                            start_pos -= 1
                        while start_pos > 0 and not self.text[start_pos - 1].isspace():
                            start_pos -= 1
                        # Delete the word
                        self.delete_selection()  # Clear any existing selection
                        self.select_text(start_pos, cursor_pos)
                        self.delete_selection()
                        self.cursor = (start_pos, 0)
                    return
                
                elif key in ('left', 'right'):
                    # Handle Ctrl+Left Arrow and Ctrl+Right Arrow
                    current_pos = self.cursor_index()
                    if key == 'left':
                        new_pos = self.get_start_of_previous_word(current_pos)
                    else:  # key == 'right'
                        new_pos = self.get_end_of_next_word(current_pos)
                    self.cursor = (new_pos, 0)
                    return
                
            super().keyboard_on_key_down(window, keycode, text, modifiers)


        def get_start_of_previous_word(self, pos):
            if pos <= 0:
                return 0
            # Move back to the start of the previous word
            while pos > 0 and self.text[pos - 1].isspace():
                pos -= 1
            while pos > 0 and not self.text[pos - 1].isspace():
                pos -= 1
            return pos

        def get_end_of_next_word(self, pos):
            if pos >= len(self.text):
                return pos
            # Move forward to the end of the next word
            while pos < len(self.text) and self.text[pos].isspace():
                pos += 1
            while pos < len(self.text) and not self.text[pos].isspace():
                pos += 1
            return pos



class FilledBoxLayout(BoxLayout):
    def __init__(self, fill_color=(0.09, 0.09, 0.09, 1), **kwargs):
        super(FilledBoxLayout, self).__init__(**kwargs)
        self.fill_color = fill_color  # Default fill color

        with self.canvas.before:
            self.rect_color = Color(*self.fill_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size





class RoundedButton(Button):
        def __init__(self, radius = 20, normal_color = (1, 1, 1, 0.05), pressed_color = (1, 1, 1, 0.4), **kwargs):
            super().__init__(**kwargs)
            self.normal_color = normal_color  # Default color (0.2, 0.6, 1, 1)
            self.pressed_color = pressed_color  # Color when pressed (0.8, 0.2, 0.2, 1)
            self.background_color=(1, 1, 1, 0)
            self.color=(1, 1, 1, 0.75)
            self.radius = radius

            with self.canvas.before:
                self.rect_color = Color(*self.normal_color)
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])  # Radius of the corners

            self.bind(pos=self.update_rect, size=self.update_rect)
            self.bind(on_press=self.on_press_handler)
            self.bind(on_release=self.on_release_handler)
            self.bind(on_touch_move=self.on_touch_move_handler)

        def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size
            
        def on_press_handler(self, *args):
            self.rect_color.rgba = self.pressed_color

        def on_release_handler(self, *args):
            self.rect_color.rgba = self.normal_color

        def on_touch_move_handler(self, instance, touch):
            if self.collide_point(*touch.pos):
                self.rect_color.rgba = self.pressed_color
            else:
                self.rect_color.rgba = self.normal_color


class StateButton(RoundedButton):
        def __init__(self, file_path, app: "ChatBotApp", **kwargs):
            self.active = False
            self.new_chat = False

            # Extract the number from the file path
            match = re.search(r'state_(\d+).txt', file_path)
            if match:
                num = match.group(1)
                text = f"Chat {num}"
            else:
                text = "Chat"
            
            # Call the superclass constructor with the text and other default attributes
            super().__init__(text=text, **kwargs)
            
            # Store the file path
            self.file_path = file_path
            self.app = app
            


        def on_press_handler(self, *args):
            pass
        
        def on_release_handler(self, *args):
            if not self.active:
                self.app.scroll_view.remove_widget(self.app.chat_log_layout)
                self.app.chat_log_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=25, padding=(100, 75, 100, 0))
                appst.read_config()
                appst._state_file = self.file_path
                config = appst._config

                config["model"]["state_file"] = os.path.basename(self.file_path)
                with open(f'config.ini', 'w') as configfile:
                    config.write(configfile)

                if self.app.active_chat:
                    self.app.active_chat.active = False
                    self.app.active_chat.rect_color.rgba = self.app.active_chat.normal_color

                self.app.active_chat = self
                self.active = True
                self.rect_color.rgba = self.pressed_color

                self.app.load_chat_history() # loading chat history here
                self.app.chat_label.text = self.text
                

                self.app.chat_log_layout.bind(minimum_height=self.app.chat_log_layout.setter('height'))
                self.app.scroll_view.add_widget(self.app.chat_log_layout)


class RoundedLabel(HoverBehavior, ButtonBehavior, CustomLabel):

    def __init__(self, radius=40, background_color=(0.15, 0.15, 0.15, 1), app: "ChatBotApp" = None, **kwargs):
        super().__init__(**kwargs)
        self.original_background_color = background_color
        self.brighter_background_color = self.brighter(self.original_background_color, factor=1.1)
        self.background_color = background_color
        self.radius = radius
        self.color = (1, 1, 1, 1)
        self.app = app
        self.selected = False

        with self.canvas.before:
            self.rect_color = Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def brighter(self, color, factor=1.1):
        return [min(c * factor, 1) for c in color]

    def on_enter(self):
        print("Entered widget")
        self.selected = True
        self.rect_color.rgba = self.brighter_background_color

    def on_leave(self):
        print("Exited widget")
        self.selected = False
        self.rect_color.rgba = self.original_background_color

    def on_press(self):
        Clipboard.copy(self.text)
        popup = Popup(
            title='Success',
            content=Label(text='Message copied to clipboard'),
            size_hint=(0.5, 0.5),
            auto_dismiss=True
        )
        popup.open()

    def update_rect(self, *args):
        print(f"Pos: {self.pos}, Size: {self.size}")
        self.rect.pos = self.pos
        self.rect.size = self.size
        if not self.selected:
            self.rect_color.rgba = self.original_background_color
        self.update_label(self.text, self.app)

    def update_label(self, text: str, app: "ChatBotApp"):
        max_width = app.chat_log_layout.width * 0.7
        temp_label = CustomLabel(
            text=text,
            halign="left",
            valign='middle',
            padding=(20, 20),
            text_size=(None, None)
        )
        temp_label.texture_update()
        text_width, text_height = temp_label.texture_size
        label_width = min(text_width, max_width)
        self.text = text
        if text_width < max_width:
            self.size_hint_x = None
            self.size[0] = text_width
        else:
            self.size_hint_x = 0.7
        self.text_size = (self.size[0], None)