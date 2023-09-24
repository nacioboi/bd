from ptysocket.SocketWrapper import Packet, Server, Client, OutputVar
import threading
import socket
import sys



def server(p):
	server = Server(bind_address='0.0.0.0', port=p, *(), **{
		"family": socket.AF_INET,
		"type": socket.SOCK_STREAM,
		"proto": 0,
		"fileno": None
	})
	server.start()

	pkt = Packet("hello there!")
	server.send(pkt)

	out_packet = OutputVar[Packet]()
	server.recv(out_packet)
	packet = out_packet()

	server.stop()



def client(p):
	client = Client(host='127.0.0.1', port=p, *(), **{
		"family": socket.AF_INET,
		"type": socket.SOCK_STREAM,
		"proto": 0,
		"fileno": None
	})
	client.start()

	out_packet = OutputVar[Packet]()
	client.recv(out_packet)
	packet = out_packet()

	pkt = Packet("hello there!")
	client.send(pkt)

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