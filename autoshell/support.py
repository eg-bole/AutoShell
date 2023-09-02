import importlib

def llm(question: str) -> str: # 输入问题，基于大模型进行回答
    module_name = "autoshell.roles.base"
    class_name = "Base"

    module = importlib.import_module(module_name)
    role_class = getattr(module, class_name)
    role = role_class()
    result = role.run(question)

    return result
    
def bash(shell: str) -> str: # 输入shell，系统将执行并返回结果
    execute_external_command(shell)
    pass
def send(message: str) -> None: # 输入message，系统将把你的消息反馈给用户
    # console_print(f'[AutoShell] {message}')
    pass

def setBashInput(func1, func2) -> None:
    global execute_external_command, console_print
    execute_external_command = func1
    console_print = func2