from ptysocket.SocketWrapper import PacketHeader, Packet, Server, Client, OutputVar
import threading
import sys



def server(p):
	server = Server(bind_address='0.0.0.0', port=p)
	server.start()

	pkt = Packet("hello there!", PacketHeader(header_1=2, header_2='test', header_3=True))
	assert pkt.header["header_1"] == 2
	assert pkt.header["header_2"] == 'test'
	assert pkt.header["header_3"] == True
	assert pkt.msg == 'hello there!'
	assert pkt.header == {"header_1": 2, "header_2": "test", "header_3": True}
	assert pkt.decode(True) == "{'header_1': 2, 'header_2': 'test', 'header_3': True}'\\U000f0000'hello there!"

	server.send(pkt)

	out_packet = OutputVar[Packet]()
	server.recv(out_packet)
	packet = out_packet()
	assert packet.header["header_1"] == 2
	assert packet.header["header_2"] == 'test'
	assert packet.header["header_3"] == True
	assert packet.msg == 'hello there!'
	assert packet.header == {"header_1": 2, "header_2": "test", "header_3": True}
	assert packet.decode(True) == "{'header_1': 2, 'header_2': 'test', 'header_3': True}'\\U000f0000'hello there!"

	server.stop()



def client(p):
	client = Client(host='127.0.0.1', port=p)
	client.start()

	out_packet = OutputVar[Packet]()
	client.recv(out_packet)
	packet = out_packet()
	assert packet.header["header_1"] == 2
	assert packet.header["header_2"] == 'test'
	assert packet.header["header_3"] == True
	assert packet.msg == 'hello there!'
	assert packet.header == {"header_1": 2, "header_2": "test", "header_3": True}
	assert packet.decode(True) == "{'header_1': 2, 'header_2': 'test', 'header_3': True}'\\U000f0000'hello there!"

	pkt = Packet("hello there!", PacketHeader(header_1=2, header_2='test', header_3=True))
	assert pkt.header["header_1"] == 2
	assert pkt.header["header_2"] == 'test'
	assert pkt.header["header_3"] == True
	assert pkt.msg == 'hello there!'
	assert pkt.header == {"header_1": 2, "header_2": "test", "header_3": True}
	assert pkt.decode(True) == "{'header_1': 2, 'header_2': 'test', 'header_3': True}'\\U000f0000'hello there!"

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