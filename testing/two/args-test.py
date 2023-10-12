from ptysocket.SocketWrapper import Packet, Server, Client, OutputVar
import threading
import socket
import sys



def server(p):
	_server = Server(bind_address='0.0.0.0', port=p, *(), **{
		"family": socket.AF_INET,
		"type": socket.SOCK_STREAM,
		"proto": 0,
		"fileno": None
	})
	_server.start()

	print("Server: Sending `hello there!`")
	pkt = Packet("hello there!")
	_server.send(pkt)

	out_packet = OutputVar[Packet]()
	_server.recv(out_packet)
	packet = out_packet()
	print("Server: Received", packet.msg)

	_server.stop()



def client(p):
	_client = Client(host='127.0.0.1', port=p, *(), **{
		"family": socket.AF_INET,
		"type": socket.SOCK_STREAM,
		"proto": 0,
		"fileno": None
	})
	_client.start()

	out_packet = OutputVar[Packet]()
	_client.recv(out_packet)
	packet = out_packet()
	print("Client: Received", packet.msg)

	print("Client: Sending `hello there!`")
	pkt = Packet("hello there!")
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