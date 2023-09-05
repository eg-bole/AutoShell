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
import locale
import abc

from autoshell.globaldata import CONFIG
import autoshell.support as x
from autoshell.tools.CSIParser import CSIParser, parse

CONSOLE_RANGE = re.compile(r'^[a-zA-Z0-9\(\)]+@{1}\S+:{1}.+[\$\#]{1}')
CONSOLE_LOC = re.compile(r'[\$\#]{1}\s')
COMMAND_ABLE = re.compile(r'^[\$\#\-]{1}')
RN_RANGE = re.compile(r'[\r\n]+')
ENCODE = locale.getpreferredencoding()

if CONFIG['DEFAULT'].lower() == 'query':
    QUERY_DEFAULT = True
else:
    QUERY_DEFAULT = False

class _Console(abc.ABC):
    def __init__(self, base_command='bash'):
        pass

    @abc.abstractmethod
    def __tty(self, base_command):
        pass

    @abc.abstractmethod
    def getUpdate(self) -> (bytes, bytes):
        """
        在阻塞模式下获取更新。

        该函数等待直到有数据可从sys.stdin或self.master_fd中读取。
        当从sys.stdin中有数据可读时，读取并返回该数据；当从self.master_fd中有数据可读时，读取并返回该数据。

        返回:
            (bytes, bytes)：第一个bytes是从sys.stdin读取的数据（如果有），否则为None；
                        第二个bytes是从self.master_fd读取的数据（如果有），否则为None。

        示例:
            d, o = obj.getUpdate()
            if d:
                # 处理从sys.stdin读取的数据
            if o:
                # 处理从self.master_fd读取的数据
        """
        pass

    @abc.abstractmethod
    def write_tty_in(self, data: bytes):
        pass

    @abc.abstractmethod
    def write_std_out(self, data: bytes):
        pass

class CommandHistory:
    def __init__(self):
        # 用于外部监听行数变化情况
        self.line_count = 0
        self.history = []

        # 监听$的变换
        self.console_match = False
        self.console_command_loc = -1

        size = os.get_terminal_size()
        self.csi = CSIParser(cols=size.columns, rows=size.lines)
        
    def add_data(self, raw:bytes):
        raw_data = raw.decode(ENCODE)

        rn_data = RN_RANGE.findall(raw_data)
        if len(rn_data) == 0:
            new_data = self.__deal(raw_data)
            return new_data.encode(ENCODE)

        raw_data = '1' + raw_data + '1'
        data = RN_RANGE.split(raw_data)
        data[0] = data[0][1:]
        data[-1] = data[-1][:-1]

        for line_num in range(len(data)):
            if line_num > 0:
                self.line_count += 1
                self.console_match = False
                self.console_command_loc = -1
                self.csi.reset()
            data[line_num] = self.__deal(data[line_num])
            
        new_data = ''
        for recover in range(len(rn_data)):
            new_data += data[recover] + rn_data[recover]
        new_data += data[-1]
        return new_data.encode(ENCODE)
    
    def __deal(self, input_str:str) -> str:
        self.csi.feed(input_str)
        if not self.console_match:
            last_line = self.csi.getDisplay(0)
            match_console = CONSOLE_RANGE.search(last_line)
            if match_console:
                self.console_match = True
                self.console_command_loc = re.search(CONSOLE_LOC, last_line).end()
                if QUERY_DEFAULT: input_str = re.sub(CONSOLE_LOC, " ", input_str, count=1)
                input_str = CONFIG['ENV_NAME'] + input_str
        return input_str
    
    def solveCommand(self, input_str, con:_Console):
        command = self.csi.getDisplay(0)[self.console_command_loc:].strip()
        command_able = COMMAND_ABLE.search(command)
        if command_able: command_able = True
        else: command_able = False
        if command_able: command = re.sub(COMMAND_ABLE, '', command)
        if command_able != QUERY_DEFAULT:
            # print(f'\r\nquery:{command}', end="")
            self.add_data(b'\x15\x0b\r')
            con.write_tty_in(b'\x15\x0b\r')
            last_len = self.line_count
            while self.line_count == last_len or self.console_match is False:
                stdin, ttyout = con.getUpdate()
                self.add_data(ttyout)
            con.write_tty_in(input_str)
            x.llm(command)
            return
        if command_able:
            self.add_data(b'\x15\x0b\r')
            con.write_tty_in(b'\x15\x0b\r' + command.encode(ENCODE))
            last_len = self.line_count
            while self.line_count == last_len or self.console_match is False:
                stdin, ttyout = con.getUpdate()
                self.add_data(ttyout)
        con.write_tty_in(input_str)


class Console(_Console):
    def __init__(self, base_command = 'bash'):
        size = os.get_terminal_size()
        self.csi = CSIParser(cols=size.columns, rows=size.lines)
        self.ch = CommandHistory()
        self.old_tty = termios.tcgetattr(sys.stdin)
        try:
            x.setBashInput(self.run_command, print)
            self.__tty(base_command)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_tty)

    def __tty(self, base_command):
        tty.setraw(sys.stdin.fileno())
        # open pseudo-terminal to interact with subprocess
        self.master_fd, slave_fd = pty.openpty()

        # use os.setsid() make it run in a new process group, or bash job control will not be enabled
        p = Popen(base_command,
                preexec_fn=os.setsid,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                universal_newlines=True,
                encoding=ENCODE)

        while p.poll() is None:
            r, w, e = select.select([sys.stdin, self.master_fd], [], [])
            if sys.stdin in r:
                d = os.read(sys.stdin.fileno(), 10240)
                if d == b'\r' and self.ch.console_match:
                    self.ch.solveCommand(d, self)
                else:
                    os.write(self.master_fd, d)
                
            elif self.master_fd in r:
                o = os.read(self.master_fd, 10240)
                if o:
                    o = self.ch.add_data(o)
                    os.write(sys.stdout.fileno(), o)
                    self.csi.feed(o.decode(ENCODE))

    def getUpdate(self) -> (bytes, bytes):
        """
        在阻塞模式下获取更新。

        该函数等待直到有数据可从sys.stdin或self.master_fd中读取。
        当从sys.stdin中有数据可读时，读取并返回该数据；当从self.master_fd中有数据可读时，读取并返回该数据。

        返回:
            (bytes, bytes)：第一个bytes是从sys.stdin读取的数据（如果有），否则为None；
                        第二个bytes是从self.master_fd读取的数据（如果有），否则为None。

        示例:
            d, o = obj.getUpdate()
            if d:
                # 处理从sys.stdin读取的数据
            if o:
                # 处理从self.master_fd读取的数据
        """
        r, w, e = select.select([sys.stdin, self.master_fd], [], [])
        d = o = None
        if sys.stdin in r:
            d = os.read(sys.stdin.fileno(), 10240) #\x15
        elif self.master_fd in r:
            o = os.read(self.master_fd, 10240)
        return d,o

    def write_tty_in(self, data:bytes):
        os.write(self.master_fd, data)

    def write_std_out(self, data:bytes):
        os.write(sys.stdout.fileno(), data)
        self.csi.feed(data.decode(ENCODE))
    
    def run_command(self, command:str):
        self.write_tty_in(command.encode(ENCODE) + b'\r')
        

