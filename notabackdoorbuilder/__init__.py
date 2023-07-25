import tokenize
import ast
import os
import re
import io



SETUP_CODE_FOR_CLIENT = open("notabackdoorbuilder/___setup_code__client___.py", "r").read()
SETUP_CODE_FOR_SERVER = open("notabackdoorbuilder/___setup_code__server___.py", "r").read()



def get_char_of_line(file, line):
	char_counter = 0
	line_counter = 0
	for char in file[1]:
		if line_counter == line: break
		if char == "\n":
			line_counter += 1
		char_counter += 1

def get_all_comments(file):
	comments = []
	with io.BytesIO(file[1].encode("utf-8")) as f:
		for tok in tokenize.tokenize(f.readline):
			if tok.type == tokenize.COMMENT:
				comments.append(tok)
	return comments

def is_matching_lookup_tokens(string_to_compare, lookup_tokens):
	pattern = r"\s*?\s*".join(re.escape(token) for token in lookup_tokens)
	regex = re.compile(f"^{pattern}\s*?$")
	return bool(regex.match(string_to_compare.strip()))

def get_import_section(file, mode, pos):
	contents = file[1][pos:]
	setup_file_name = "___setup_code__client___.py" if mode == "client" else "___setup_code__server___.py"
	setup_file = (setup_file_name, open(f"notabackdoorbuilder/{setup_file_name}", "r").read())
	setup_file_contents = setup_file[1]
	start_pos_of_section = -1
	end_pos_of_section = -1
	all_comments = get_all_comments(setup_file)
	for node in all_comments:
		comment_val = node.string.strip()
		print(comment_val)
		lookup_tokens = [
			"#",
			"[",
			"begin-insert:",
			"imports",
			"]",
			"#",
		]
		if is_matching_lookup_tokens(comment_val, lookup_tokens):
			if start_pos_of_section != -1:
				# we had two definitions of the same section, we report error
				print(f"You must only have one declaration for each section in the setup code file.")
			start_pos_of_section = get_char_of_line(setup_file, node.start[0])
	for node in all_comments:
		comment_val = node.string.strip()
		lookup_tokens = [
			"#",
			"[",
			"end-insert:",
			"imports",
			"]",
			"#",
		]
		if is_matching_lookup_tokens(comment_val, lookup_tokens):
			if end_pos_of_section != -1:
				print("You must only have one declaration for each section in the setup code file.")
			end_pos_of_section = get_char_of_line(setup_file, node.start[0])
	print(start_pos_of_section, end_pos_of_section)
	


def paste_protocol(file, mode):
	"""
	Modifies the given file to include the protocol.
	"""
	if not "protocol.json" in os.listdir():
		print("Error: protocol.json not found.")
		return
	
	new_file_name = "___build_candidate__client___.py" if mode == "client" else "___build_candidate__server___.py"
	
	new_file_contents = ""
	protocol = open("protocol.json", "r").read()

	pos = protocol.find("\\u")
	while pos != -1:
		new_protocol = ""
		new_protocol += protocol[:pos] + "\\" + protocol[pos:]
		protocol = new_protocol
		pos = protocol.find("\\u", pos+5)

	with open(new_file_name, "w") as f:
		contents = file[1]
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
				pos_of_main = get_char_of_line(file, node.lineno)
				pos_of_before_main = get_char_of_line(file, node.lineno-1)
		new_file_contents = ""
		new_file_contents += contents[:pos_of_last_import]
		new_file_contents += get_import_section(file, mode, pos_of_last_import)
		new_file_contents += contents[pos_of_last_import:pos_of_before_main]
		new_file_contents += get_before_main_section(file, mode, pos_of_before_main)
		new_file_contents += f"___INSERTED_PROTOCOL___ = \"\"\"\n{protocol}\n\"\"\"\n\n"
		new_file_contents += contents[pos_of_before_main:pos_of_main]
		new_file_contents += get_main_section(file, mode,  pos_of_main)
		new_file_contents += contents[pos_of_main:]
		f.write(new_file_contents)

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

def walk_ast(file):
	return (node for node in ast.walk(ast.parse(file[1])))

def get_files_to_modify(files):
	objects = [(file, node) for file in files for node in walk_ast(file) if isinstance(node, ast.Import)]
	return [obj[0] for obj in objects for alias in obj[1].names if alias.name == __name__]

def check_main_function_declared(files_to_modify):
	do_have_main_declared = [False, False]
	for i, file in enumerate(files_to_modify):
		do_have_main_declared[i] = any(node.name == "main" for node in walk_ast(file) if isinstance(node, ast.FunctionDef))
	return all(do_have_main_declared)

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
	return SETUP_CODE_FOR_CLIENT != None and SETUP_CODE_FOR_SERVER != None

def build():
	if not check_setup_code():
		print("Error: Setup code could not be found.")
		return

	files = get_file_content()

	print(f"files: {[file[0] for file in files]}")

	if len(files) != 2:
		print("Error: There must be exactly one backdoor file and one server file.")
		return

	files_to_modify = get_files_to_modify(files)

	print(f"files_to_modify: {[file[0] for file in files_to_modify]}")

	if not check_main_function_declared(files_to_modify):
		print("Error: Both files must have a main function declared.")
		return

	if not check_main_function_called(files_to_modify):
		print("Error: The main function must not be called.")
		return

	client_file, server_file = determine_files(files_to_modify)

	handle_client(client_file)
	handle_server(server_file)