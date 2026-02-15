import sys, os 
os.system('color') 
class ApixDebugger:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    @staticmethod
    def log_var_change(name, value):
        print(f"{ApixDebugger.BLUE}[Debug]:{ApixDebugger.ENDC} Variable {name} -> {value}")
    def report_error(error_type, message, line_num, code_line=""):
        print(f"{ApixDebugger.FAIL}{ApixDebugger.BOLD} Apix {error_type}:{ApixDebugger.ENDC}")
        print(f"  {ApixDebugger.WARNING}Line {line_num}:{ApixDebugger.ENDC} {message}")
        if code_line:
            print(f"  {ApixDebugger.BLUE}Code:{ApixDebugger.ENDC} `{code_line.strip()}`")
        print("-" * 40)
    @staticmethod
    def log_system(message):
        print(f"{ApixDebugger.GREEN}[Apix System]:{ApixDebugger.ENDC} {message}")
