import re

text = "\r\n12\r145\r\n24"
RN_RANGE = re.compile(r'[\r\n]+')

result = RN_RANGE.split(text)
result1 = RN_RANGE.findall(text)

for item in result:
    print(item)
