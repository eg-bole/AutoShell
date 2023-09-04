import re
escaped_text = b'\x1b[?2004h\x1b]0;bole@DESKTOP-IGHIT78: /mnt/g/Program/\xe7\xa7\x91\xe5\x88\x9b\xe9\xa1\xb9\xe7\x9b\xae/flyeye/AutoShell/autoshell\x07\x1b[01;32mbole@DESKTOP-IGHIT78\x1b[00m:\x1b[01;34m/mnt/g/Program/\xe7\xa7\x91\xe5\x88\x9b\xe9\xa1\xb9\xe7\x9b\xae/flyeye/AutoShell/autoshell\x1b[00m$'
decoded_text = escaped_text.decode('unicode_escape')
result = re.sub(r'\x1b\[[0-9;]*[mGK]', '', decoded_text)
print(result)