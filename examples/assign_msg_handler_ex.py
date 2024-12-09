import sys
import os

# Get the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path
sys.path.append(parent_dir)

# Example starts here
from chat_app import ChatBotFrontEnd as CBF


# this is an example of how to assign custom message handler
chat = CBF()

# comment this decorator for default implementation to be used
@chat.message_handler()
# function should be async (cuz waiting for model's response would hang the app otherwise)
# yield instead of return for dynamic response update
async def your_mom(user_message):
    yield "yo mama"


if __name__ == "__main__":
    chat.start_frontend()