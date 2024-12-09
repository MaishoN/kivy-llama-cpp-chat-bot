import os
from app_state import ApplicationState as appst
from typing import Callable
import re
import threading
import asyncio


class AsyncioThread:
    def __init__(self):
        self.loop = None
        self.thread = None

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def stop(self):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()
            self.loop = None
            self.thread = None


class ChatManager():

    @staticmethod
    def get_history_entries() -> list:
        state_file = appst.state
        history = ChatManager.read_history(state_file, fix_template = False)

        user_entries = re.findall("<\\|im_start\\|>user [\S\s]*?<\\|im_end\\|>\n", history)
        user_entries = [re.sub("(<\\|im_start\\|>user )|(<\\|im_end\\|>\n)", "", x) for x in user_entries]

        assistant_entries = re.findall("<\\|im_start\\|>assistant [\S\s]*?<\\|im_end\\|>\n", history)
        assistant_entries = [re.sub("(<\\|im_start\\|>assistant )|(<\\|im_end\\|>\n)", "", x) for x in assistant_entries]

        return [{"user" : x[0], "assistant" : x[1]} for x in zip(user_entries, assistant_entries)]

    @staticmethod
    def read_history(state_file: str, fix_template = True) -> str:
        history = ""
        if os.path.exists(state_file):
            with open(state_file, encoding = 'utf-8') as chat_history:
                history = f"{chat_history.read()}"

            if fix_template:
                history = history.replace("<|im_start|>user ", f"{appst.start_token}{appst.user_prompt_mark}\n")
                history = history.replace("<|im_start|>assistant ", f"{appst.start_token}{appst.model_prompt_mark}\n")
                history = history.replace("<|im_end|>", appst.end_token)

        return history


    @staticmethod
    def append_history(state_file: str, user_message: str, model_response: str) -> None:
        with open(state_file, "a", encoding = 'utf-8') as chat_history:
            chat_history.write(f"<|im_start|>user {user_message}<|im_end|>\n<|im_start|>assistant {model_response.strip()}<|im_end|>\n")


    @staticmethod
    def state_saver(func: Callable) -> Callable:
        async def new_func(prompt: str):
            state_file = os.path.join(appst.states_dir, appst.state_file)
            final_response = ""
            async for res in func(prompt):
                final_response = res
                yield res

            ChatManager.append_history(state_file, prompt, final_response)
    
        return new_func



class PromptConstructor():

    @staticmethod
    def construct_prompt() -> str:
        prompt = ""

        if appst.use_system_prompt == "1":
            prompt += f"{appst.start_token}{appst.system_prompt_mark}\n{appst.system_prompt}{appst.end_token}\n"

        if appst.load_chat_history == "1":
            prompt += ChatManager.read_history(os.path.join(appst.states_dir, appst.state_file))

        prompt += f"{appst.start_token}{appst.user_prompt_mark}\n{appst.user_default_message}{appst.end_token}\n"
        prompt += f"{appst.start_token}{appst.model_prompt_mark}\n"

        return prompt


    @classmethod
    def apply_chatbot_template(cls, func: Callable) -> Callable:

        async def new_func(prompt: str):
            full_prompt = cls.construct_prompt()
            full_prompt = full_prompt.format(prompt)

            async for res in func(full_prompt):
                yield res

        return new_func if appst.save_chat_history != "1" else ChatManager.state_saver(new_func)



