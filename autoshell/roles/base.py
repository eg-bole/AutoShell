from autoshell.prompts.p_base import *
from .role import Role
from autoshell.globaldata import  CONFIG
import re
import autoshell.support as x

class Base(Role):
    def __init__(self):
        super().__init__()
        super().add_msg(MESSAGE['init'][CONFIG['LANGUAGE']])
    def run(self, question):
        super().add_user_message(MESSAGE['input'][CONFIG['LANGUAGE']].format(**{'input':question}))
        response = super().send_messages()
        matches = pattern.findall(response)
        for match in matches:
            exec(match)
        
pattern = re.compile(r'```python(.*?)```', re.DOTALL)