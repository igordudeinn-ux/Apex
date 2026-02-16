import sys, time, os
os.system('color')
from a_engine import Apix_Compiler
from debugger import ApixDebugger as deb
def main():
    if len(sys.argv) < 2:
        print("Usage: apix <filename>.a")
        return
    start_time = time.time()
    deb.log_system("Initializing Apix Engine...")
    compiler = Apix_Compiler()
    compiler.run_file(sys.argv[1])
    end_time = time.time()
    execution_time = round((end_time - start_time) * 1000, 2)
    deb.log_system(f"Execution finished in {execution_time}ms")
if __name__ == "__main__":
    main()
#
