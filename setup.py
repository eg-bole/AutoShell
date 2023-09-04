from setuptools import setup

setup(
    name='AutoShell',
    version='0.1',
    packages=['autoshell'],
    entry_points={
        'console_scripts': [
            '- = autoshell.bash:main'
        ]
    },
    install_requires=[
        # 列出你的项目所依赖的其他Python库
        "openai",
        "pyyaml",
        "rich",
        "pyte"
    ],
    author='EG-bole',
    author_email='eg-bole@foxmail.com',
    description='Unleash Command-Line Efficiency with GPT Integration!',
    url='https://github.com/eg-bole/AutoShell.git',
)
