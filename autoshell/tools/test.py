from rich.console import Console
from rich.text import Text

# 创建 Console 对象
console = Console()

# 创建一个含有 ANSI 转义码的 Text 对象
text = Text.from_ansi("\x1b[31mHello\x1b[0m \x1b[32mWorld\x1b[0m")

# 使用 Console 对象打印 Text 对象
console.print(text)
