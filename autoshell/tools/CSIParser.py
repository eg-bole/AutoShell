import pyte

class CSIParser:
    def __init__(self, cols=800, rows=10):
        """Initialize the CSIParser with a screen size."""
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream(self.screen)
        self.display = self.screen.display
        self.screen.reset()
    
    def feed(self, input_str):
        self.stream.feed(input_str)

    def reset(self):
        self.screen.reset()

    def analyse(self):
        return '\r\n'.join(self.display).strip()

# # Testing
# parser = CSIParser()
# input_str1 = "python \x08\x1b[K3 --versi\x08\x1b[K\x08\x1b[Ksion"
# parsed1 = parser.parse(input_str1)
# print(parsed1)  # Expected: python3 --version

# escaped_text = b'\x1b[?2004h\x1b]0;bole@DESKTOP-IGHIT78: /mnt/g/Program/\xe7\xa7\x91\xe5\x88\x9b\xe9\xa1\xb9\xe7\x9b\xae/flyeye/AutoShell/autoshell\x07\x1b[01;32mbole@DESKTOP-IGHIT78\x1b[00m:\x1b[01;34m/mnt/g/Program/\xe7\xa7\x91\xe5\x88\x9b\xe9\xa1\xb9\xe7\x9b\xae/flyeye/AutoShell/autoshell\x1b[00m$'
# input_str2 = escaped_text.decode('unicode_escape')

# parsed2 = parser.parse(input_str2)
# print(parsed2)  # Expected: helworld
