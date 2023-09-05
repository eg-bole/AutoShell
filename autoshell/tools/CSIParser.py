import pyte
import re
import os

BLANK_BEGIN = re.compile(r'^\s*')
BLANK_END = re.compile(r'\s*$')

class CSIParser:
    def __init__(self, cols=200, rows=30):
        """Initialize the CSIParser with a screen size."""
        self.cols = cols
        self.rows = rows
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream(self.screen)
        self.reset()
    
    def feed(self, input_str):
        self.stream.feed(input_str)

    def reset(self):
        self.screen.reset()

    def analyse(self):
        return '\r\n'.join(self.screen.display).strip()
    
    def last(self):
        """Efficiently locate the last non-empty line using the dirty lines feature of pyte.Screen."""

        # First, check the dirty lines as they were recently modified.
        for idx in sorted(self.screen.dirty, reverse=True):
            if self.screen.display[idx].strip():
                return idx

        # If no non-empty line found in dirty lines, fall back to the standard approach.
        for i in range(self.rows - 1, -1, -1):
            if self.screen.display[i].strip():
                return i

        return 0

    def getLast(self):
        return self.screen.display[self.last()]
    
    def getDisplay(self, index:int=None):
        if index is not None:
            return self.screen.display[index]
        return self.screen.display

size = os.get_terminal_size()
fast_screen = pyte.Screen(size.columns, size.lines)
fast_stream = pyte.Stream(fast_screen)
def parse(input_str):
    fast_screen.reset()
    begin = BLANK_BEGIN.findall(input_str)[0]
    end = BLANK_END.findall(input_str)[0]
    fast_stream.feed(input_str)
    parsed_output = '\r\n'.join(fast_screen.display).strip()
    return begin + parsed_output + end
    


# # Testing
# parser = CSIParser(cols=size.columns, rows=size.lines)
# input_str1 = "\x1b[?2004h\x1b]0;bole@DESKTOP-IGHIT78: ~/flyeye/AutoShell/autoshell/tools\x07\x1b[01;32mbole@DESKTOP-IGHIT78\x1b[00m:\x1b[01;34m~/flyeye/AutoShell/autoshell/tools\x1b[00m$"

# parser.feed(input_str1)
# print(parser.getLast())
  # Expected: python3 --version

# escaped_text = b'\x1b[?2004h\x1b]0;bole@DESKTOP-IGHIT78: /mnt/g/Program/\xe7\xa7\x91\xe5\x88\x9b\xe9\xa1\xb9\xe7\x9b\xae/flyeye/AutoShell/autoshell\x07\x1b[01;32mbole@DESKTOP-IGHIT78\x1b[00m:\x1b[01;34m/mnt/g/Program/\xe7\xa7\x91\xe5\x88\x9b\xe9\xa1\xb9\xe7\x9b\xae/flyeye/AutoShell/autoshell\x1b[00m$'
# input_str2 = escaped_text.decode('unicode_escape')

# parsed2 = parser.parse(input_str2)
# print(parsed2)  # Expected: helworld
