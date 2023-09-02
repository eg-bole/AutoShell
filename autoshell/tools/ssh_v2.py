import paramiko
import os
import select
import pyte
import msvcrt

# 预设用户名、密码和服务器信息
hostname = "roadar.eg-bole.cn"
port = 8088
username = "flyeye"
pem_file_path = "./nvidia.pem"

# 初始化SSH客户端
ssh_client = paramiko.SSHClient()

# 自动添加服务器SSH密钥（这样做可能会导致安全问题）
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 使用PEM密钥文件进行连接
private_key = paramiko.RSAKey(filename=pem_file_path)

# 连接到SSH服务器
try:
    ssh_client.connect(hostname, port, username, pkey=private_key)
except Exception as e:
    print(f"Failed to connect: {e}")
    exit()

# 打开一个交互式Shell会话
channel = ssh_client.invoke_shell(term='xterm')


# 初始化Pyte终端模拟器
screen = pyte.Screen(80, 24)
stream = pyte.Stream(screen)

# 激活接受数据
channel.settimeout(0.0)

def refresh_display(screen):
    os.system('cls' if os.name == 'nt' else 'clear')
    for line in screen.display:
        print(line.rstrip())

def is_input_available():
    return msvcrt.kbhit()

# 在循环中
while True:
    try:
        readlist, writelist, errlist = select.select([channel,], [], [], 0.1)

        if len(readlist) > 0:
            result = channel.recv(1024).decode("utf-8")
            stream.feed(result)
            refresh_display(screen)

        if is_input_available():
            result = os.read(0, 1024)
            if len(result) > 0:
                channel.send(result)
                
    except KeyboardInterrupt:
        print("\nExiting...")
        break

channel.close()
ssh_client.close()