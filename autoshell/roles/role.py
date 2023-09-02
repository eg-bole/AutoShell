from autoshell.llm import LLM
import asyncio
"""
@Time    : 2023/8/15 15:18
@Author  : EG-bole
@File    : role.py
"""
class Role(LLM):
    def __init__(self):
        """
        初始化角色对象的基本信息。
        """
        super().__init__()
        self.stop_event = asyncio.Event()

    def send_messages(self) -> str:
        return super().send_messages()
    def add_user_message(self, usr_msg):
        return super().add_user_message(usr_msg)
    def add_system_message(self, sys_msg):
        return super().add_system_message(sys_msg)
    def add_assistant_message(self, ass_msg):
        return super().add_assistant_message(ass_msg)
    def add_msg(self, msg:list or tuple):
        return super().add_msg(msg)
    def get_last_response(self) -> dict:
        return super().get_last_response()
    def get_last_response(self) -> str:
        return super().get_last_response()
    def clear_message(self):
        return super().clear_message()
    def stop_running(self):
        '''停止该角色的运行'''
        self.stop_event.set()
def host() -> Role:
    return Role('host')