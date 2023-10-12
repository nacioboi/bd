from ptysocket.SocketWrapper import Packet, Server, Client, OutputVar
import threading
import socket
import sys



def server(p):
	def on_receive(packet:Packet):
		print(f"Server: Received: {packet.msg}")
		if packet.msg == "remove-me":
			return Packet("")
		return packet

	def on_send(packet:Packet):
		print(f"Server: Sending: {packet.msg}")
		if packet.msg == "do-not-remove-me":
			return Packet("remove-me")
		return packet

	_server = Server(bind_address='0.0.0.0', port=p)
	_server.define_recv_callback(on_receive)
	_server.define_send_callback(on_send)
	_server.start()

	pkt = Packet("hello there!")
	_server.send(pkt)

	out_packet = OutputVar[Packet]()
	_server.recv(out_packet)
	packet = out_packet()

	pkt = Packet("do-not-remove-me")
	_server.send(pkt)

	out_packet = OutputVar[Packet]()
	_server.recv(out_packet)
	packet = out_packet()

	_server.stop()



def client(p):
	def on_receive(packet:Packet):
		print(f"Client: Received: {packet.msg}")
		if packet.msg == "remove-me":
			return Packet("")
		return packet

	def on_send(packet:Packet):
		print(f"Client: Sending: {packet.msg}")
		if packet.msg == "do-not-remove-me":
			return Packet("remove-me")
		return packet

	_client = Client(host='0.0.0.0', port=p)
	_client.define_recv_callback(on_receive)
	_client.define_send_callback(on_send)
	_client.start()

	out_packet = OutputVar[Packet]()
	_client.recv(out_packet)
	packet = out_packet()

	pkt = Packet("hello there!")
	_client.send(pkt)

	out_packet = OutputVar[Packet]()
	_client.recv(out_packet)
	packet = out_packet()

	pkt = Packet("do-not-remove-me")
	_client.send(pkt)

	_client.stop()



if len(sys.argv) != 2:
	print(f"Usage python3 {sys.argv[0]} <port>")
	exit()

port = int(sys.argv[1])

server_thread = threading.Thread(target=server, args=(port,))
client_thread = threading.Thread(target=client, args=(port,))

server_thread.start()
client_thread.start()