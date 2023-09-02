import openai
from autoshell.globaldata import config

class GPT:
    def __init__(self):
        self.messages = []
        self.response = None

    def send_messages(self):
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=self.messages,
            temperature=0.0,  # Set Temperature to 0
            frequency_penalty=0.0,  # Set Frequency Penalty to 0
            presence_penalty=0.0  # Set Presence Penalty to 0
        )
        self.messages.append({"role":response.choices[0].message['role'], "content":response.choices[0].message['content']})
        self.last_response = response
        self.last_content = response.choices[0].message['content']
        return self.last_content

    def add_user_message(self, usr_msg):
        self.messages.append({"role": "user", "content": usr_msg})

    def add_system_message(self, sys_msg):
        self.messages.append({"role": "system", "content": sys_msg})

    def add_assistant_message(self, ass_msg):
        self.messages.append({"role": "assistant", "content": ass_msg})

    def add_msg(self, msg:list or tuple):
        self.messages += msg

    def get_last_response(self):
        if self.response is None:
            self.response = self.send_messages()
        return self.response.choices[0].message['content']
    
    def clear_message(self):
        self.messages = []

# 设置代理
if config['API_PROXY']:
    openai.proxy = config['API_PROXY']
openai.api_key = config['API_KEY']
openai.api_base = config['API_BASE']
OPENAI_MODEL = config['API_MODEL']
