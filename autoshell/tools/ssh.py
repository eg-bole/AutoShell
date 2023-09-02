import re
from rich.console import Console
from rich.text import Text
import paramiko
import select
import threading

console = Console()

def colorize_prompt(text):
    # 使用正则表达式匹配用户名、'@'、主机名和路径
    match = re.search(r'(\w+)@(\w+):([\w/~]+)\$', text)
    if match:
        user, host, path = match.groups()
        colored_prompt = f"[bold green]{user}[/bold green]@[bold green]{host}[/bold green]:[bold blue]{path}[/bold blue]$"
        return re.sub(r'\w+@\w+:[\w/~]+\$', colored_prompt, text)
    else:
        return text

def receive_thread(channel):
    skip_first_line = True  # 用于跳过首个输出行（即输入的命令）
    while True:
        rl, wl, xl = select.select([channel], [], [], 0.5)
        if len(rl) > 0:
            recv = channel.recv(1024)
            if len(recv) > 0:
                text = recv.decode('utf-8') + '\n'
                if skip_first_line:
                    text = text.split('\n', 1)[-1]  # 移除第一行
                    skip_first_line = False  # 仅移除首次输出的第一行
                text = Text.from_ansi(text)
                console.print(text, end="")


def execute_interactive_command(ssh_client):
    channel = ssh_client.invoke_shell()

    receiver = threading.Thread(target=receive_thread, args=(channel,))
    receiver.daemon = True  # 守护线程，主线程结束时该线程也会结束
    receiver.start()

    while True:
        user_input = console.input()
        if user_input.lower() == 'exit':
            console.print("Exiting SSH session.", style="bold red")
            break
        channel.send(f"{user_input}\n")

def main():
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    host = "roadar.eg-bole.cn"
    port = 8088
    username = "flyeye"
    
    private_key_path = "./nvidia.pem"
    mykey = paramiko.RSAKey(filename=private_key_path)
    
    console.print(f"Connecting to {host}:{port} ...", style="bold blue")
    ssh_client.connect(host, port, username, pkey=mykey)
    console.print("Connected successfully!", style="bold green")
    
    execute_interactive_command(ssh_client)
    
    ssh_client.close()

if __name__ == "__main__":
    main()
