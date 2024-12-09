from __future__ import annotations

from kivy.app import App
from graphics import *
from utility import AsyncioThread
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from app_state import ApplicationState as appst

class ChatBotApp(App):

    input_box: CustomTextInput
    toggle_sidebar_button: RoundedButton
    chat_label: CustomLabel
    sidebar: FilledBoxLayout
    send_button: RoundedButton

    scroll_sidebar: ScrollView
    chats_layout: BoxLayout
    scroll_view: ScrollView
    chat_log_layout: BoxLayout

    active_chat: StateButton
    new_chat: StateButton

    def __init__(self, async_thread, **kwargs):
        super().__init__(**kwargs)
        self.async_thread: AsyncioThread

        self.current_button_function: bool
        self.sidebar_visible: bool
        

    def on_start(self): ...


    def on_stop(self): ...


    def build(self): ...
    

    def open_settings_popup(self, instance): ...
    

    def delete_chat(self, new_chat_button): ...
        

    def new_chat_handler(self, app): ...
    

    def load_chat_history(self): ...
    

    def add_chat_buttons(self, app, directory = appst.states_dir): ...


    def add_chat_button(self, app, directory, file_name): ...
    

    def toggle_sidebar(self, instance): ...
    

    def unbind_send_button(self): ...
    

    def bind_send_message(self): ...


    def bind_stop_generating(self, future): ...


    def send_message(self, instance): ...
                
            
    async def update_bot_response(self, bot_message_label, user_message): ...


    def stop_generation(self, future): ...


    def add_message(self, text: str, is_user_message = False) -> RoundedLabel: ...


    def scroll_to_bottom(self, dt): ...


    def on_key_down(self, window, key, *args): ...