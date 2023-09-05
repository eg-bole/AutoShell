import subprocess
import os
from rich import print
from rich.console import Console
import readline  # For tab completion
import platform  # To identify the OS

console = Console()

def run_command(command):
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
        console.print(result)
    except subprocess.CalledProcessError as e:
        console.print(e.output, style="red")

def execute_external_command(command):
    prompt = f"[blue]GPT[/blue]@[green]{hostname}[/green]:[magenta]{current_path}[/magenta] [yellow]${command}[/yellow]"
    console.print(prompt)
    run_command(command)

def completer(text, state):
    # Set the directory to look for executables based on the operating system
    directory = current_path
    # if current_os == 'Windows':

    # Handle the case where the directory does not exist
    if not os.path.exists(directory):
        return None

    # Simple tab completion from available commands in the directory
    options = [cmd for cmd in os.listdir(directory) if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

def main():
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    import autoshell.app, autoshell.support as x

    def console_print(msg):
        console.print(msg, style="yellow")

    autoshell.app.main()
    x.setBashInput(execute_external_command, console_print)

    while True:
        global current_path, hostname, current_path, user
        try:
            # Get user and current path for the prompt
            user = os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
            
            # Check for OS type to get hostname
            if platform.system() == 'Windows':
                hostname = os.environ.get('COMPUTERNAME') or 'unknown'
            else:
                hostname = os.uname().nodename
                
            current_path = os.getcwd()

            # Using rich for colorful prompt
            prompt = f"[blue]{user}[/blue]@[green]{hostname}[/green]:[magenta]{current_path}[/magenta] "

            # Get command input
            command = console.input(prompt).strip()

            if command and command[0] != '$':
                x.llm(prompt + command[1:].strip())
                continue
            command = command[1:]

            if command.strip() == "exit":
                console.print("Goodbye!", style="yellow")
                break
            elif command.strip():
                run_command(command)
        except KeyboardInterrupt:
            # Handle Ctrl+C
            console.print("\nInterrupted", style="yellow")
