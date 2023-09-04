#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import select
import termios
import tty
import pty
from subprocess import Popen
import re
from CSIParser import CSIParser
# from autoshell.globaldata import config as CONFIG

CONFIG = {
    'API_BASE':'https://api.openai.com/v1',
    'API_PROXY':'',
    'API_KEY':'',
    'API_MODEL':'gpt-3.5-turbo-16k',
    'LANGUAGE':'Chinese',
    'ENCODE':'UTF-8'
}

csi = CSIParser()
USER_RANGE = re.compile(r'\x07\x1b\[[\d;]+m.+?\x1b')
ANSI_RANGE = re.compile(r'\x1b\[[\d;]+m')
XOR_RANGE = re.compile(r'[\x1b\x07\x08]')
CONSOLE_RANGE = re.compile(r'\x1b\[[\d;]+m.+?\x1b\[00m[\$\#]{1}')
RN_RANGE = re.compile(r'[\r\n]+')

class CommandHistory:
    def __init__(self):
        self.history = []
        self.command_history = []
        self.command = ''

        # 监听(AutoShell)的变换
        self.host = ''
        self.host_match = False

        # 监听$的变换
        self.console_match = False
        self.console_command_loc = -1
        
    def add_data(self, raw:bytes):
        raw_data = '1'+raw.decode(CONFIG['ENCODE'])+'1'

        data = RN_RANGE.split(raw_data)
        rn_data = RN_RANGE.findall(raw_data)

        data[0] = data[0][1:]
        data[-1] = data[-1][:-1]
        for line_num in range(len(data)):
            if line_num > 0:
                self.history.append(self.command)
                self.command = ''
                self.console_match = False
                self.console_command_loc = -1
                self.host_match = False
            self.command += data[line_num]

            match_console = CONSOLE_RANGE.search(self.command)
            if match_console and not self.console_match:
                self.console_match = True
                data[line_num] = data[line_num][:match_console.regs[0][1] - 1] + data[line_num][match_console.regs[0][1]:]
                self.console_command_loc = match_console.regs[0][1]
                # data[line_num] = data[line_num].replace('\x1b[00m$', '\x1b[00m').replace('\x1b[00m# ', '\x1b[00m')

            match = USER_RANGE.search(self.command)
            if match:
                if not self.host_match:
                    data[line_num] = data[line_num].replace("\x07\x1b[", "\x1b[00m(AutoShell)\x07\x1b[")
                    self.host_match = True
                match.regs[0][0]
                host = re.sub(ANSI_RANGE, '', match.group())
                self.host = re.sub(XOR_RANGE, '', host)
        
        new_data = ''
        for recover in range(len(rn_data)):
            new_data += data[recover] + rn_data[recover]
        new_data += data[-1]
        return new_data.encode(CONFIG['ENCODE'])
    
    def solveCommand(self):
        msg = csi.parse(self.command[self.console_command_loc:]).strip()
        self.command_history.append(msg)
        if msg[0] == '#' or msg[0] == '$':
            return msg[1:]
        
        pass


class Console:
    def __init__(self, base_command = 'bash'):
        self.ch = CommandHistory()

        # open pseudo-terminal to interact with subprocess
        master_fd, slave_fd = pty.openpty()

        # use os.setsid() make it run in a new process group, or bash job control will not be enabled
        p = Popen(base_command,
                preexec_fn=os.setsid,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                universal_newlines=True)

        while p.poll() is None:
            r, w, e = select.select([sys.stdin, master_fd], [], [])
            if sys.stdin in r:
                d = os.read(sys.stdin.fileno(), 10240) #\x15
                if d == b'\r' and self.ch.console_match:
                    self.ch.solveCommand()
                    
                os.write(master_fd, d)
                
            elif master_fd in r:
                o = os.read(master_fd, 10240)
                if o:
                    os.write(sys.stdout.fileno(), self.ch.add_data(o))

        
try:
    # save original tty setting then set it to raw mode
    old_tty = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())
    Console()
except Exception as e:
    raise e
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)