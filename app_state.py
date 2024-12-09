import configparser
import os

config_file = "config.ini"

class ApplicationState():
        
    _config = configparser.ConfigParser()

    _llama_cli_path = None
    _model_name = None
    _models_dir = None
    _states_dir = None
    _state_file = None
    _state = None

    _use_system_prompt = None
    _load_chat_history = None
    _save_chat_history = None
    _system_prompt_mark = None
    _system_prompt = None
    _user_prompt_mark = None
    _model_prompt_mark = None
    _start_token = None
    _end_token = None
    _user_default_message = None

    @classmethod
    def read_config(cls):
        cls._config.read(config_file)

    @classmethod
    def generate_config(cls):
        cls._config["model"] = {
            "llama_cli_path" : "llama.cpp/build/bin/llama-cli",
            "model_name" : "gemma-2-9b-it-Q6_K.gguf",
            "models_dir" : "models",
            "states_dir" : "states",
            "state_file" : "state_1.txt",
            "use_system_prompt" : "0",
            "load_chat_history" : "1",
            "save_chat_history" : "1",
            "system_prompt_mark" : "system",
            "system_prompt" : "You are a helpful assistant",
            "user_prompt_mark" : "user",
            "model_prompt_mark" : "model",
            "start_token" : "<start_of_turn>",
            "end_token" : "<end_of_turn>",
            "user_default_message" : "{0}",

            }
        with open('config.ini', 'w') as configfile:
            cls._config.write(configfile)

        cls._config["model"]["state"] = cls.state

        with open('config.ini', 'w') as configfile:
            cls._config.write(configfile)



    @classmethod
    @property
    def llama_cli_path(cls):
        cls.read_config()
        cls._llama_cli_path = cls._config["model"]["llama_cli_path"]
        return cls._llama_cli_path
    

    @classmethod
    @property
    def model_name(cls):
        cls.read_config()
        cls._model_name = cls._config["model"]["model_name"]
        return cls._model_name
    

    @classmethod
    @property
    def models_dir(cls):
        cls.read_config()
        cls._models_dir = cls._config["model"]["models_dir"]
        return cls._models_dir
    

    @classmethod
    @property
    def states_dir(cls):
        cls.read_config()
        cls._states_dir = cls._config["model"]["states_dir"]
        return cls._states_dir
    

    @classmethod
    @property
    def state_file(cls):
        cls.read_config()
        cls._state_file = cls._config["model"]["state_file"]
        return cls._state_file
    

    @classmethod
    @property
    def state(cls):
        cls._state = os.path.join(*f"{cls.states_dir}/{cls.state_file}".split("/"))
        return cls._state


    @classmethod
    @property
    def use_system_prompt(cls):
        cls.read_config()
        cls._use_system_prompt = cls._config["model"]["use_system_prompt"]
        return cls._use_system_prompt
    

    @classmethod
    @property
    def load_chat_history(cls):
        cls.read_config()
        cls._load_chat_history = cls._config["model"]["load_chat_history"]
        return cls._load_chat_history
    

    @classmethod
    @property
    def save_chat_history(cls):
        cls.read_config()
        cls._save_chat_history = cls._config["model"]["save_chat_history"]
        return cls._save_chat_history
    

    @classmethod
    @property
    def system_prompt_mark(cls):
        cls.read_config()
        cls._system_prompt_mark = cls._config["model"]["system_prompt_mark"]
        return cls._system_prompt_mark
    

    @classmethod
    @property
    def system_prompt(cls):
        cls.read_config()
        cls._system_prompt = cls._config["model"]["system_prompt"]
        return cls._system_prompt
    

    @classmethod
    @property
    def user_prompt_mark(cls):
        cls.read_config()
        cls._user_prompt_mark = cls._config["model"]["user_prompt_mark"]
        return cls._user_prompt_mark
    

    @classmethod
    @property
    def model_prompt_mark(cls):
        cls.read_config()
        cls._model_prompt_mark = cls._config["model"]["model_prompt_mark"]
        return cls._model_prompt_mark
    

    @classmethod
    @property
    def start_token(cls):
        cls.read_config()
        cls._start_token = cls._config["model"]["start_token"]
        return cls._start_token
    

    @classmethod
    @property
    def end_token(cls):
        cls.read_config()
        cls._end_token = cls._config["model"]["end_token"]
        return cls._end_token
    

    @classmethod
    @property
    def user_default_message(cls):
        cls.read_config()
        cls._user_default_message = cls._config["model"]["user_default_message"]
        return cls._user_default_message