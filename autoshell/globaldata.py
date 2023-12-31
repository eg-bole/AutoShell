import os, yaml
from autoshell.tools.xml import load_xml_note

CONFIG = {}

_BASE_DATA = {
    'API_BASE':'https://api.openai.com/v1',
    'API_PROXY':'',
    'API_KEY':'',
    'API_MODEL':'gpt-3.5-turbo-16k',
    'LANGUAGE':'Chinese',
    'ENV_NAME':'(AutoShell)',
    'DEFAULT': 'query', #query or command
    'BASE_COMMAND': 'bash'
}
MSG = load_xml_note(os.path.join('autoshell', 'msg.xml'))

home_dir = os.path.expanduser("~")
smartshell_dir = os.path.join(home_dir, ".config", "AutoShell")
if not os.path.exists(smartshell_dir):
    os.makedirs(smartshell_dir)
key_file = os.path.join(smartshell_dir, "config.yaml")
if os.path.exists(key_file):
    with open(key_file, 'r') as file:
        data = yaml.safe_load(file)
    if data['API_KEY'] == '':
        data['API_KEY'] = input(MSG['init1'][data['LANGUAGE']])
else:
    data = _BASE_DATA
    data['API_KEY'] = input(MSG['init1'][data['LANGUAGE']])
    data['API_PROXY'] = input(MSG['init2'][data['LANGUAGE']])
    with open(key_file, 'w') as file:
        yaml.dump(data, file)
CONFIG = data