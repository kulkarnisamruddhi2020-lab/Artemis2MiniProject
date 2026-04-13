import os
import time

# Enable ANSI escape sequences on Windows
os.system("")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

class Console:
    @staticmethod
    def print_header(title):
        print(f"\n{Colors.CYAN}{'='*50}")
        print(f" {title}")
        print(f"{'='*50}{Colors.RESET}")

    @staticmethod
    def print_log(timestamp, stage, msg):
        time_str = f"T+{timestamp:05.1f}h"
        print(f"{Colors.GREEN}[{time_str}] [{stage:^12}] {msg}{Colors.RESET}")

    @staticmethod
    def print_warning(msg):
        print(f"{Colors.YELLOW}[WARNING] {msg}{Colors.RESET}")

    @staticmethod
    def print_error(msg):
        print(f"{Colors.RED}[CRITICAL] {msg}{Colors.RESET}")

    @staticmethod
    def input_prompt(msg):
        return input(f"{Colors.BLUE}{msg} {Colors.RESET}").strip().lower()

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
