from ptysocket.SocketWrapper import PacketHeader, Packet, Server, Client, OutputVar
import threading
import sys



def server(p):
	_server = Server(bind_address='0.0.0.0', port=p)
	_server.start()

	pkt = Packet("hello there!", PacketHeader(header_1=2, header_2='test', header_3=True))
	assert pkt.header["header_1"] == 2
	assert pkt.header["header_2"] == 'test'
	assert pkt.header["header_3"] == True
	assert pkt.msg == 'hello there!'
	assert pkt.header == {"header_1": 2, "header_2": "test", "header_3": True}
	assert pkt.decode(True) == "{'header_1': 2, 'header_2': 'test', 'header_3': True}'\\U000f0000'hello there!"
	print(f"Server: Sending packet {pkt.msg}")
	_server.send(pkt)

	out_packet = OutputVar[Packet]()
	_server.recv(out_packet)
	packet = out_packet()
	print(f"Server: Received packet {packet.msg}")
	assert packet.header["header_1"] == 2
	assert packet.header["header_2"] == 'test'
	assert packet.header["header_3"] == True
	assert packet.msg == 'hello there!'
	assert packet.header == {"header_1": 2, "header_2": "test", "header_3": True}
	assert packet.decode(True) == "{'header_1': 2, 'header_2': 'test', 'header_3': True}'\\U000f0000'hello there!"

	_server.stop()



def client(p):
	_client = Client(host='127.0.0.1', port=p)
	_client.start()

	out_packet = OutputVar[Packet]()
	_client.recv(out_packet)
	packet = out_packet()
	print(f"Client: Received packet {packet.msg}")
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
	print(f"Client: Sending packet {pkt.msg}")
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