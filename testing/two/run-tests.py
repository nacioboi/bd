import subprocess
import time
import sys
import os

if len(sys.argv) < 2:
	print("Usage: python3 run-tests.py <port>")
	sys.exit(1)

def run_test(test):
	proc = subprocess.Popen(["/bin/bash", "-c", test], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return (proc.stdout.read() + proc.stderr.read()).decode()


port = int(sys.argv[1])

print("running args-test.py...")
print(run_test(f"python3 {os.getcwd()}/args-test.py {port}"))
print("running callback-test.py...")
print(run_test(f"python3 {os.getcwd()}/callback-test.py {port+1}"))
print("running header-test.py...")
print(run_test(f"python3 {os.getcwd()}/header-test.py {port+2}"))