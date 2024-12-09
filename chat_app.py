from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
import asyncio
import os
import sys
from kivy.lang import Builder
from kivy.uix.widget import Widget
import re
from utility import ChatManager
from app_state import ApplicationState as appst
from kivy.uix.popup import Popup
from settings_window import SettingsWindow
from app_contracts import ChatBotApp
from graphics import *
from utility import AsyncioThread


# Set the default window size
# Window.size = (1220, 880)

# Calculate the center position
# screen_width, screen_height = Window.system_size
# window_width, window_height = Window.size

# Window.left = (screen_width - window_width) / 2
# Window.top = (screen_height - window_height) / 2



Builder.load_string('''
#:import os os                    

<TextInput>:
    cursor_color: 0.4, 0.4, 0.4, 1
    font_name: os.path.join(os.getcwd(), 'fonts', 'NotoSansMono+NotoEmoji.ttf')
    font_size: 35
                    
<CustomLabel@Label>:
    font_name: os.path.join(os.getcwd(), 'fonts', 'NotoSansMono+NotoEmoji.ttf')
    font_size: 35
''')



# This is the chatbot app in Python using Kivi!
class Application(ChatBotApp):

    # ctrl + backspace working functionality (seriously why do i have to implement this)
    # ((thank god gpt exists))

    def __init__(self, async_thread, **kwargs):
        super().__init__(async_thread, **kwargs)
        self.async_thread = async_thread
        self.current_button_function = None
        self.sidebar_visible = True


    def on_start(self):
        self.input_box.focus = True


    def on_stop(self):
        self.async_thread.stop()


    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        # Main float layout
        layout = BoxLayout(orientation = "vertical", size_hint = (1,1))

        # Top FilledBoxLayout for the buttons and label
        top_layout = FilledBoxLayout(orientation='horizontal', size_hint=(1, None), height=100, padding=(20, 10, 20, 10))

        # Toggle Sidebar button
        self.toggle_sidebar_button = RoundedButton(text="Toggle Sidebar", size_hint=(None, 1), size=(250, 100), radius= 25)
        self.toggle_sidebar_button.bind(on_release=self.toggle_sidebar)
        top_layout.add_widget(self.toggle_sidebar_button)

        # Spacer Widget for centering the label
        top_layout.add_widget(Widget(size_hint=(1, 1)))  # Flexible spacer

        # label in the middle
        self.chat_label = CustomLabel(text="New Chat", size_hint=(None, 1), size=(250, 100))
        top_layout.add_widget(self.chat_label)

        # Spacer Widget for centering the New Chat button
        top_layout.add_widget(Widget(size_hint=(1, 1)))  # Flexible spacer

        # New Chat button
        new_chat_button = RoundedButton(text="New", size_hint=(None, 1), size=(125, 100), radius= 25)
        top_layout.add_widget(new_chat_button)
        new_chat_button.bind(on_release= lambda x: self.new_chat_handler(self))
        Clock.schedule_once(lambda x: self.new_chat_handler(self))
        

        # Add a spacer with a fixed width of 20 pixels
        spacer = Widget(size_hint=(None, 1), width=8)
        top_layout.add_widget(spacer)

        # New Del button
        new_del_button = RoundedButton(text="Del", size_hint=(None, 1), size=(125, 100), radius=25, normal_color= (0.8, 0.2, 0.2, 1), pressed_color= (1, 0.3, 0.3, 1))
        top_layout.add_widget(new_del_button)
        new_del_button.bind(on_release=lambda instance: self.delete_chat(new_chat_button))


        layout.add_widget(top_layout)

        # Main horizontal layout for sidebar and main_layout
        main_horizontal_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})

        # Sidebar layout
        self.sidebar = FilledBoxLayout(orientation='vertical', padding= (20, 0, 20, 20), spacing=12, size_hint=(None, 1), width=450)
        
        # Scrollable part of the sidebar
        self.scroll_sidebar = ScrollView(size_hint=(1, 1))
        self.chats_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)


        self.add_chat_buttons(self)

        self.chats_layout.bind(minimum_height=self.chats_layout.setter('height'))

        self.scroll_sidebar.add_widget(self.chats_layout)
        self.sidebar.add_widget(self.scroll_sidebar)

        # Add the fixed button at the bottom of the sidebar
        profile_settings_button = RoundedButton(text="Profile Settings", size_hint=(1, None), height=80)
        self.sidebar.add_widget(profile_settings_button)
        profile_settings_button.bind(on_release=self.open_settings_popup)

        main_horizontal_layout.add_widget(self.sidebar)

        # Main vertical layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(1, 1))

        # Scrollable chat log
        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.chat_log_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=25, padding=(100, 75, 100, 0))
        self.chat_log_layout.bind(minimum_height=self.chat_log_layout.setter('height'))

        self.scroll_view.add_widget(self.chat_log_layout)
        main_layout.add_widget(self.scroll_view)

        # Input box and send button layout
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)

        self.input_box = CustomTextInput(size_hint=(0.8, None), height = 100, multiline=False, background_color=(0.15, 0.15, 0.15, 1), foreground_color=(1, 1, 1, 1))
        self.input_box.bind(on_text_validate=self.send_message)  # Bind Enter key to send_message
        self.send_button = RoundedButton(text="Send", size=(250, 100), size_hint=(None, None), radius=40, normal_color=(0.25, 0.25, 0.25, 1), pressed_color=(0.35, 0.35, 0.35, 1))

        # Send message ON RELEASE
        # 1) to ensure it works intuitively
        # 2) to ensure input_box gets the focus after message send
        # Otherwise, when using on_press, button gets released
        # AFTER message gets sent, meaning button gets focus AFTER the input field
        # (undesired behaviour)
        self.bind_send_message()

        input_layout.add_widget(self.input_box)
        input_layout.add_widget(self.send_button)
        main_layout.add_widget(input_layout)

        # self.toggle_sidebar(None)

        # Bind the Enter key globally to send_message
        Window.bind(on_key_down=self.on_key_down)

        main_horizontal_layout.add_widget(main_layout)

        layout.add_widget(main_horizontal_layout)

        self.active_chat = None
        self.new_chat = None

        return layout
    

    def open_settings_popup(self, instance):
        content = SettingsWindow()
        popup = Popup(title='Settings', content=content, size_hint=(0.8, 0.8))
        content.dismiss = popup.dismiss
        content.bind(on_close=lambda *args: popup.dismiss())
        popup.open()
    

    # Define the method to handle deletion
    def delete_chat(self, new_chat_button):
        app = App.get_running_app()  # Get the app instance
        if app.active_chat and app.active_chat.new_chat != True:

            # Gather the file_path property of the active chat widget
            file_path = app.active_chat.file_path
            
            # Remove the widget from app.chats_layout
            app.chats_layout.remove_widget(app.active_chat)
            
            # Move the file from "states" to "deleted" directory
            import os
            import shutil
            
            states_dir = "states"
            deleted_dir = "deleted"
            
            # Ensure the "deleted" directory exists
            if not os.path.exists(deleted_dir):
                os.makedirs(deleted_dir)
            
            # Find and move the file
            file_name = os.path.basename(file_path)
            src = os.path.join(states_dir, file_name)
            dest = os.path.join(deleted_dir, file_name)
            
            if os.path.exists(src):
                shutil.move(src, dest)
            else:
                print(f"File not found: {src}")
        else:
            print("No active chat to delete.")
            return

        app.new_chat_handler(self)


    # Define the new method
    def new_chat_handler(self, app):
        # Check if there is an existing new_chat button
        if app.new_chat is not None and app.new_chat.new_chat:
            # Trigger the on_release_handler of the existing new_chat button
            app.new_chat.on_release_handler()
            return  # Exit the method
        
        # Specify the directory
        directory = appst.states_dir
        
        # Find the largest number in state files

        files = os.listdir(directory)
        pattern = r'^state_(\d+)\.txt$'

        numbers = []
        for file in files:
            match = re.match(pattern, file)
            if match:
                numbers.append(int(match.group(1)))
        if len(numbers) > 0:
            max_number = max(numbers)
        else:
            max_number = 0  # If no files exist, start with 1
        
        # Generate the next file name
        next_number = max_number + 1
        file_name = f'state_{next_number}.txt'
        
        # Add a new chat button
        button = app.add_chat_button(app, directory, file_name)
        
        # Set new_chat attribute of the app
        app.new_chat = button
        button.new_chat = True
        
        # Call on_release_handler of the new button
        button.on_release_handler()
    

    def load_chat_history(self):
        # Retrieve the chat history entries
        history_entries = ChatManager.get_history_entries()

        # Iterate over each entry and add messages to the chat log
        for entry in history_entries:
            # Add user message
            user_message = entry.get("user", "")
            self.add_message(user_message, is_user_message=True)

            # Add assistant message
            assistant_message = entry.get("assistant", "")
            self.add_message(assistant_message, is_user_message=False)

        Clock.schedule_once(self.scroll_to_bottom)
    

    def add_chat_buttons(self, app, directory = appst.states_dir):
        # List all files in the directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        # Filter files that match the pattern "state_*.txt"
        state_files = [f for f in files if re.match(r'state_\d+\.txt', f)][::-1]
        
        # Create a button for each state file and add it to chats_layout
        for file_name in state_files:
            self.add_chat_button(self, directory, file_name)


    def add_chat_button(self, app, directory, file_name):
        file_path = os.path.join(directory, file_name)
        button = StateButton(app= app, file_path=file_path, size_hint=(1, None), height=80)
        app.chats_layout.add_widget(button)

        return button
    

    def toggle_sidebar(self, instance):
        if self.sidebar_visible:
            self.sidebar.opacity = 0
            self.sidebar.width = 0
            self.sidebar.disabled = True
            self.toggle_sidebar_button.text = "Open Sidebar"
        else:
            self.sidebar.opacity = 1
            self.sidebar.width = 450
            self.sidebar.disabled = False
            self.toggle_sidebar_button.text = "Close Sidebar"
        self.sidebar_visible = not self.sidebar_visible
    

    def unbind_send_button(self):
        # Unbind the previous function if it exists
        if self.current_button_function:
            self.send_button.unbind(on_release = self.current_button_function)
    

    def bind_send_message(self):
        self.unbind_send_button()
        # Bind the send_message function
        self.send_button.bind(on_release = self.send_message)
        self.current_button_function = self.send_message  # Update the reference


    def bind_stop_generating(self, future):
        self.unbind_send_button()
        new_bind = lambda btn: self.stop_generation(future)
        self.send_button.bind(on_release= new_bind)
        self.current_button_function = new_bind


    def send_message(self, instance):
        user_message = self.input_box.text.strip()

        # Clear the input box
        self.input_box.text = ""

        # Set focus back to the input box

        ## self.input_box.focus = True
        # ^^^ apparently this one didn't work cuz on_text_validate causes 
        # input_box to lose it's focus in the current event loop. 
        # The workaround is to set focus in the next event loop
        Clock.schedule_once(lambda dt: setattr(self.input_box, 'focus', True))

        if user_message:
            # Add user message to the chat log
            self.add_message(f"{user_message}", is_user_message= True)

            # Add new bot message to the  chat log
            bot_message_label = self.add_message("Generating...")

            # Schedule scroll to the bottom after the next frame
            Clock.schedule_once(self.scroll_to_bottom)


            # Change button label to "Stop" and disable the text input field
            self.send_button.text = "Stop"
            self.input_box.disabled = True

            # Update bot message field after generation
            # Schedule the coroutine to run in the asyncio event loop
            future = asyncio.run_coroutine_threadsafe(self.update_bot_response(bot_message_label, user_message), self.async_thread.loop)

            # Bind the button to stop the generation process
            self.bind_stop_generating(future)
                
            

    async def update_bot_response(self, bot_message_label, user_message):
        final_response = ""
        try:
            async for response in ChatBotFrontEnd._generate_response(user_message):
                final_response = response
                Clock.schedule_once(lambda dt, text=response: bot_message_label.update_label(text, self))

            Clock.schedule_once(lambda dt: bot_message_label.update_label(final_response, self))
            Clock.schedule_once(lambda dt: setattr(self.send_button, 'text', "Send"))
            self.input_box.disabled = False
            Clock.schedule_once(lambda dt: setattr(self.input_box, 'focus', True))
            self.bind_send_message()

            return final_response

        except Exception as e:
            Clock.schedule_once(lambda dt: bot_message_label.update_label(f"Error: {str(e)}", self))
            print(f"Error in update_bot_response: {e}")


    def stop_generation(self, future):
        print('asdfasdf')
        if not future.done():
            future.cancel()



    def add_message(self, text: str, is_user_message = False):
        
        if self.new_chat is not None and self.new_chat.active:
            print(self.new_chat == None)
            print("moms are gay")
            self.new_chat.new_chat = False
            self.new_chat = None

        # Determine the position hint based on whether it's a user message or assistant message
        pos_hint = {'right': 1} if is_user_message else {'left': 0}

        label = RoundedLabel(
            app = self,
            size_hint_x = None,
            size_hint_y = None,
            halign="left",
            valign='middle',
            radius = 20,
            pos_hint = pos_hint
        )
        if is_user_message:
            label.original_background_color = (0.25, 0.25, 0.25, 1)
            label.brighter_background_color = label.brighter((0.25, 0.25, 0.25, 1))

        label.update_label(text, self)
        label.bind(texture_size=label.setter('size'))
        label.padding = (20, 20)

        self.chat_log_layout.add_widget(label)

        return label


    def scroll_to_bottom(self, dt):

        # Only scroll to the bottom if the chat log exceeds the visible area
        if self.chat_log_layout.height > self.scroll_view.height:

            # idk why but [0] is in fact the last message, no matter how hard 
            # GPT tried to convince me [-1] should be (which is first message smh)
            self.scroll_view.scroll_to(self.chat_log_layout.children[0])

    def on_key_down(self, window, key, *args):
        if key == 13:  # 13 is the keycode for Enter
            self.send_message(None)




class ChatBotFrontEnd():

    def __init__(self):
        self.async_thread = AsyncioThread()


    # _generate_response = staticmethod(lambda user_message: f"[Bot]\nI received your message: {user_message}\n")
    # ^^^^ alternative way
    @staticmethod
    async def _generate_response(user_message):
        yield f"I received your message: {user_message}"
    
    # likewise can be declared as: message_handler = classmethod(...)
    # but it's a pain in the ass to declare it like that
    @classmethod
    def message_handler(cls):
        def decorator(func):
            print("\n\nMessage handler assigned!\n\n")

            async def new_func(user_message):
                final_response = ""
                async for res in func(user_message):
                    final_response = res
                    yield res
                yield final_response
            
            cls._generate_response = staticmethod(new_func)
            return new_func
        
        return decorator


    def start_frontend(self):
        self.async_thread.start()

        try:
            app = Application(self.async_thread)
            app.run()

        # this fucking bullshit. Why the hell is KeyboardInterrupt triggering when I'm rerunning the app?
        except KeyboardInterrupt:
            print("KeyboardInterrupt detected. Cleaning up...")
            self.async_thread.stop()

        except Exception as e:
            print(f"Error in start_frontend: {e}")
            raise
            self.async_thread.stop()


if __name__ == "__main__":
    chat = ChatBotFrontEnd()
    try:
        chat.start_frontend()
    except Exception as e:
        print(f"Error in main: {e}")
        raise
        sys.exit(1)