from chat_app import ChatBotFrontEnd as CBF
from app_state import ApplicationState as appst
import os
import asyncio
from utility import PromptConstructor


class ModelRuner():

    @CBF.message_handler()
    @PromptConstructor.apply_chatbot_template
    @staticmethod
    async def generate_response(prompt: str):

        llama_cli_path = os.path.join(*f"{appst.llama_cli_path}".split("/"))
        model = f"{appst.model_name}"
        model_path = os.path.join(*f"{appst.models_dir}/{model}".split("/"))

        command = [
            llama_cli_path, 
            "-m", model_path, 
            "-p", prompt, 
            "-r", f"{appst.end_token}",
            "--threads", "4", 
            #"--chat-template", "gemma",
            "--no-display-prompt"
            ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        response = ""
        buffer = b""

        try:
            while True:
                chunk = await process.stdout.read(1)
                if not chunk:
                    break
                buffer += chunk

                try:
                    decoded_response = buffer.decode("utf-8")
                    response += decoded_response
                    buffer = b"" # Clear the buffer if decoding is successful

                except UnicodeDecodeError as e:
                    print(f"UnicodeDecodeError: {e}")
                    # Handle partial characters by keeping the buffer
                    continue

                except Exception as e:
                    print(f"Unexpected error: {e}")
                    continue

                yield response

            # Handle any remaining buffer
            if buffer:
                try:
                    response += buffer.decode("utf-8")
                except UnicodeDecodeError as e:
                    print(f"UnicodeDecodeError in final buffer: {e}")
                except Exception as e:
                    print(f"Unexpected error in final buffer: {e}")

            stdout, stderr = await process.communicate()
            if stderr:
                print("Subprocess error:", stderr.decode("utf-8"))

            print("response:", response)
            yield ModelRuner.remove_end_of_text_token(response)

        except asyncio.CancelledError:
            process.terminate()

            print(f"Generation cancelled\nresponse: {response}")
            yield ModelRuner.remove_end_of_text_token(response)


    def remove_end_of_text_token(inferenced_output: str) -> str:
        return inferenced_output.strip()[:-14].strip() if inferenced_output.strip().endswith("[end of text]") else inferenced_output.strip()



if __name__ == "__main__":

    print(PromptConstructor.construct_prompt())
    
    chat = CBF()
    chat.start_frontend()
    

