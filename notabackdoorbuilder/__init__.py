import tokenize
import ast
import sys
import os
import re
import io



SETUP_FILE_FOR_CLIENT = (
	"notabackdoorbuilder/___setup_code__client___.py",
	open("notabackdoorbuilder/___setup_code__client___.py", "r").read()
)

SETUP_FILE_FOR_SERVER = (
	"notabackdoorbuilder/___setup_code__server___.py",
	open("notabackdoorbuilder/___setup_code__server___.py", "r").read()
)



# helper functions.

def handle_error(error_message):
	print(f"ERROR: {error_message}")
	exit()

def walk_ast(file):
	return (node for node in ast.walk(ast.parse(file[1])))

def get_char_of_line(file, line):
	char_counter = 0
	line_counter = 0
	for char in file[1]:
		if line_counter == line: break
		if char == "\n":
			line_counter += 1
		char_counter += 1
	return char_counter

def get_all_comments(file):
	comments = []
	with io.BytesIO(file[1].encode("utf-8")) as f:
		for tok in tokenize.tokenize(f.readline):
			if tok.type == tokenize.COMMENT:
				comments.append(tok)
	return comments

def is_matching_lookup_tokens(string_to_compare, lookup_tokens):
	pattern = r"\s*?\s*".join(re.escape(token) for token in lookup_tokens)
	regex = re.compile(f"^{pattern}\\s*?$")
	return bool(regex.match(string_to_compare.strip()))



# functions for handling setup code.

def get_section(mode, section_name):
	setup_file = SETUP_FILE_FOR_CLIENT if mode == "client" else SETUP_FILE_FOR_SERVER
	start_pos_of_section = -1
	end_pos_of_section = -1
	all_comments = get_all_comments(setup_file)
	lookup_tokens = [
		"#",
		"[",
		"begin-insert:",
		section_name,
		"]",
		"#",
	]
	for node in all_comments:
		comment_val = node.string.strip()
		if is_matching_lookup_tokens(comment_val, lookup_tokens):
			if start_pos_of_section != -1:
				print(f"You must only have one declaration for each section in the setup code file.")
				exit()
			start_pos_of_section = get_char_of_line(setup_file, node.start[0]-1)
	lookup_tokens[2] = "end-insert:"
	for node in all_comments:
		comment_val = node.string.strip()
		if is_matching_lookup_tokens(comment_val, lookup_tokens):
			if end_pos_of_section != -1:
				print("You must only have one declaration for each section in the setup code file.")
				exit()
			end_pos_of_section = get_char_of_line(setup_file, node.start[0])
	
	if start_pos_of_section == -1 or end_pos_of_section == -1:
		print("Error: Could not find main section in setup code file.")
		exit()
	
	return setup_file[1][start_pos_of_section:end_pos_of_section]

def get_setup_code(file, mode, pos_of_last_import, pos_of_before_main, pos_of_main):
	contents = file[1]
	protocol = open("protocol.json", "r").read()

	pos = protocol.find("\\u")
	while pos != -1:
		new_protocol = ""
		new_protocol += protocol[:pos] + "\\" + protocol[pos:]
		protocol = new_protocol
		pos = protocol.find("\\u", pos+5)
	
	new_file_contents = ""
	new_file_contents += contents[:pos_of_last_import] 					+ "\n"
	new_file_contents += get_section(mode, "imports") 					+ "\n"
	new_file_contents += contents[pos_of_last_import:pos_of_before_main] 		+ "\n"
	new_file_contents += get_section(mode, "before-main") 				+ "\n"
	new_file_contents += f"___INSERTED_PROTOCOL___ = \"\"\"\n{protocol}\n\"\"\"" 	+ "\n"
	new_file_contents += contents[pos_of_before_main:pos_of_main] 			+ "\n"
	new_file_contents += get_section(mode, "main") 						+ "\n"
	new_file_contents += contents[pos_of_main:] 						+ "\n"
	new_file_contents += "if __name__ == \"__main__\":\n\t__main()" 			+ "\n"

	return new_file_contents

def paste_setup_code(file, mode):
	if not "protocol.json" in os.listdir():
		print("Error: protocol.json not found.")
		return
	
	new_file_name = "___build_candidate__client___.py" if mode == "client" else "___build_candidate__server___.py"

	with open(new_file_name, "w") as f:
		nodes = [node for node in walk_ast(file)]
		nodes_filtered_1 = [node for node in nodes if isinstance(node, ast.Import)]
		nodes_filtered_2 = [node for node in nodes if isinstance(node, ast.FunctionDef) and node.name == "main"]
		nodes_filtered = nodes_filtered_1 + nodes_filtered_2
		pos_of_last_import = 0
		pos_of_main = 0
		pos_of_before_main = 0

		for node in nodes_filtered:
			if isinstance(node, ast.Import):
				pos_of_last_import = get_char_of_line(file, node.lineno)
			elif isinstance(node, ast.FunctionDef):
				pos_of_main = get_char_of_line(file, node.lineno-1)
				pos_of_before_main = get_char_of_line(file, node.lineno-2)

		f.write(get_setup_code(file, mode, pos_of_last_import, pos_of_before_main, pos_of_main))

	with open(new_file_name, "r") as f:
		code = f.read()

	new_file_contents = ""
	nodes = [node for node in ast.walk(ast.parse(code)) if isinstance(node, ast.Call) ]

	start_of_handle_setup_call = None
	for node in nodes:
		try:
			if isinstance(node, ast.Call):
				if node.func.attr == "handle_setup":
					if node.func.value.id == "notabackdoorbuilder":
						start_of_handle_setup_call = get_char_of_line((None, code), node.lineno-1)
						break
		except:
			pass
	
	new_contents = f"{code[:start_of_handle_setup_call]}#{code[start_of_handle_setup_call:]}"

	with open(new_file_name, "w") as f:
		f.write(new_contents)


# functions for handling build code.

def handle_client(client_file):
	paste_setup_code(client_file, "client")

def handle_server(server_file):
	paste_setup_code(server_file, "server")

def handle_setup(mode):
	build()
	if mode == "server":
		with open("___build_candidate__server___.py", "r") as f:
			contents = f.read()
		if len(sys.argv) > 2:
			args = sys.argv[2:]
		else:
			args = []
		os.execl(sys.argv[1], "python", "./___build_candidate__server___.py", *args)
	elif mode == "client":
		with open("___build_candidate__client___.py", "r") as f:
			contents = f.read()
		eval(compile(contents, "___build_candidate__client___.py", "exec"))

def get_files_in_directory():
	file_names = [file_name for file_name in os.listdir() if os.path.isfile(file_name) and file_name != "build.py"]
	file_names = [file_name for file_name in file_names if file_name != "___build_candidate__client___.py"]
	file_names = [file_name for file_name in file_names if file_name != "___build_candidate__server___.py"]
	return [(file_name,open(file_name, "r").read()) for file_name in file_names if file_name.endswith(".py")]

def filter_files(files):
	objects = [(file, node) for file in files for node in walk_ast(file) if isinstance(node, ast.Import)]
	return [obj[0] for obj in objects for alias in obj[1].names if alias.name == __name__]

def check_main_function_declared(files_to_modify):
	return all(any(node.name == "main" for node in walk_ast(file) if isinstance(node, ast.FunctionDef)) for file in files_to_modify)

def check_main_function_called(files_to_modify):
	for file in files_to_modify:
		if any(node.func.id == "main" for node in walk_ast(file) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
			return False
	return True

def determine_files(files_to_modify):
	client_file, server_file = None, None
	for file in files_to_modify:
		nodes = [node for node in walk_ast(file) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
		nodes = [node for node in nodes if node.func.attr == "handle_setup" and node.func.value.id == __name__]
		for node in nodes:
			if node.args[0].s == "client":
				client_file = file
			else:
				server_file = file
	return client_file, server_file

def check_setup_code():
	return SETUP_FILE_FOR_CLIENT[1] != None and SETUP_FILE_FOR_SERVER[1] != None



def build():
	if not check_setup_code(): handle_error("Setup code could not be found.")

	files = get_files_in_directory()

	if len(files) != 2: handle_error("There must be exactly one backdoor file and one server file.")

	files_to_modify = filter_files(files)

	if not check_main_function_declared(files_to_modify): handle_error("Both files must have a main function declared.")

	if not check_main_function_called(files_to_modify): handle_error("The main function must not be called.")

	client_file, server_file = determine_files(files_to_modify)

	handle_client(client_file)
	handle_server(server_file)
	