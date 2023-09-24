from ptysocket.SocketWrapper import Packet, Server, Client, OutputVar
import threading
import socket
import sys



def server(p):
	def on_receive(packet:Packet):
		print(f"Received: {packet.msg}")
		if packet.msg == "remove-me":
			return Packet("")
		return packet

	def on_send(packet:Packet):
		print(f"Sending: {packet.msg}")
		if packet.msg == "do-not-remove-me":
			return Packet("remove-me")
		return packet

	server = Server(bind_address='0.0.0.0', port=p)
	server.define_recv_callback(on_receive)
	server.define_send_callback(on_send)
	server.start()

	pkt = Packet("hello there!")
	server.send(pkt)

	pkt = Packet("do-not-remove-me")
	server.send(pkt)

	out_packet = OutputVar[packet]()
	server.recv(out_packet)
	packet = out_packet()

	out_packet = OutputVar[packet]()
	server.recv(out_packet)
	packet = out_packet()

	server.stop()



def client(p):
	def on_receive(packet:Packet):
		print(f"Received: {packet.msg}")
		if packet.msg == "remove-me":
			return Packet("")
		return packet

	def on_send(packet:Packet):
		print(f"Sending: {packet.msg}")
		if packet.msg == "do-not-remove-me":
			return Packet("remove-me", header=packet.header)
		return packet

	client = client(bind_address='0.0.0.0', port=p)
	client.define_recv_callback(on_receive)
	client.define_send_callback(on_send)
	client.start()

	pkt = Packet("hello there!")
	client.send(pkt)

	pkt = Packet("do-not-remove-me")
	client.send(pkt)

	out_packet = OutputVar[packet]()
	client.recv(out_packet)
	packet = out_packet()

	out_packet = OutputVar[packet]()
	client.recv(out_packet)
	packet = out_packet()

	client.stop()



if len(sys.argv) != 2:
	print(f"Usage python3 {sys.argv[0]} <port>")
	exit()

port = int(sys.argv[1])

server_thread = threading.Thread(target=server, args=(port,))
client_thread = threading.Thread(target=client, args=(port,))

server_thread.start()
client_thread.start()

server_thread.join()
client_thread.join()