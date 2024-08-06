import random
import string
import os
import subprocess
from os import system, _exit, path, urandom

system("mode 80,18 & title Unique & powershell $H=get-host;$W=$H.ui.rawui;$B=$W.buffersize;$B.width=80;$B.height=9999;$W.buffersize=$B;")

ERROR = "\x1b[38;5;255m[\x1b[31m-\x1b[38;5;255m]"
SUCCESS = "\x1b[38;5;255m[\x1b[32m+\x1b[38;5;255m]"


class wlc:
    def exit_():
        system("echo Press any key to exit . . . & pause >nul")
        _exit(0)
        
    def wlc(self, file):
        self.file = file
        input(f"tigger file: {self.file} press any key to continue")
        
    @staticmethod
    def randint(a, b, seed=[0]):
        seed[0] = (1664525 * seed[0] + 1013904223) % 2 ** 32
        return int(a + (1 + b - a) * seed[0] / 2 ** 32)

    @staticmethod
    def generate_random_comment(length=50):
        comment = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        return f'# {comment}'
    
    @staticmethod
    def gen_random(length=12, chars=string.ascii_lowercase):
        return ''.join(random.choice(chars) for _ in range(length))

                
    def random_comment(self):
        if not path.exists(self.file):
            print(f"{ERROR} File does not exist.\n")
            self.exit_
        with open(self.file, "a") as f:
            for _ in range(1, self.randint(4, 10)):
                f.write(f"\n#{urandom(16).hex()}")
        print(f"{SUCCESS} File was made unique.\n")     

    def main(self, files):
        for file in files:
            self.wlc(file)
            self.random_comment()
        subprocess.run(f"nuitka menu.py --onefile --output-dir={self.gen_random()} --windows-disable-console --company-name={self.gen_random()} --product-name={self.gen_random()} --output-file={self.gen_random()}.exe --file-version={self.randint(1, 50)}.{self.randint(1, 50)}.{self.randint(1, 50)} --product-version={self.randint(1, 50)} --file-description={self.gen_random()} --copyright={self.gen_random()} --trademarks={self.gen_random()}", shell=True)

files = ["screen.py", "utils.py", "menu.py"]
wlc().main(files)
