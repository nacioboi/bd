import ptysocket.SocketWrapper as SocketWrapper

from woody import DebugContext
from woody import Woody

import multiprocessing
import threading
import socket
import time



""" Setup logging """

Woody()

DEBUG = DebugContext("debug",
	do_save_logs=False,
	do_use_time=True
)



""" Setup tests """

"""
We are testing the ptysocket.SocketWrapper module.
We must test the following of its features:
	- Any encoding.
	- No worry about buffer sizes.
	- Any suffix.
	- Any split char.
	- Packet class with headers.
	- *args and **kwargs for the socket object.
	- Callbacks for sending and receiving.
	- Handshake system.
	- Bandwidth saving.

Full documentation of the module's features:
	- Set your own encoding.
	- Don't worry about buffer sizes anymore as the module, when receiving, will wait until receiving the suffix. Once the suffix is
		received, the module will stop receiving and return the message.
	- Set your own suffix.
	- Set your own split char. The split char is the character that splits the header and the message.
	- Packet class makes life easier by allowing you to send headers and messages in one packet.
	- Set *args and **kwargs for the socket object.
	- Set callbacks for receiving and sending.
		- The callback for sending will be called before sending the packet, allowing you to modify the packet before sending it.
		- The callback for receiving will be called after receiving the packet, allowing you to modify the packet 
			after receiving it.
		- Each callback will be called every time a packet is sent/received.
	- Handshake system to make sure the server and the client are compatible.
	- Saves on bandwidth by only sending the header when it changes. This module does not however save on bandwidth on the message
		itself. This is because the message should be quick to access and modify, and since the message is usually larger than the
		header, it would take too much time to compress it.

Each test class will have a server and client thread.
We will also have a master thread to handle cleanup incase of an error.
"""



WATCHED_PROCESSES = {}

def CLIENT_CALLBACK_WRAPPER(client:"SocketWrapper.Client", callback:callable, *args, **kwargs):
	global WATCHED_PROCESSES
	done = False
	try:
		callback(client, *args, **kwargs)
		done = True
	except Exception as e:
		done = True
		raise e
	finally:
		while not done:
			time.sleep(0.1)
		client.stop()
		DEBUG.log_line("Stopping client...")
		time.sleep(1)
		proc = WATCHED_PROCESSES.get("client")
		if proc:
			proc.terminate()
			WATCHED_PROCESSES["client"] = None
		DEBUG.log_line("Client stopped.")

def SERVER_CALLBACK_WRAPPER(server:"SocketWrapper.Server", callback:callable, *args, **kwargs):
	global WATCHED_PROCESSES
	done = False
	try:
		callback(server, *args, **kwargs)
		done = True
	except Exception as e:
		done = True
		raise e
	finally:
		while not done:
			time.sleep(0.1)
		server.stop()
		DEBUG.log_line("Stopping server...")
		time.sleep(1)
		proc = WATCHED_PROCESSES.get("server")
		if proc:
			proc.terminate()
			WATCHED_PROCESSES["server"] = None
		DEBUG.log_line("Server stopped.")

def CLIENT_WRAPPER(client:"SocketWrapper.Client", callback:callable, *args, **kwargs):
	global CLIENT_CALLBACK_WRAPPER
	global WATCHED_PROCESSES

	time.sleep(2)
	DEBUG.log_line("Starting client...")
	threading.Thread(target=client.start).start()
	time.sleep(0.5)

	DEBUG.log_line("Starting client callback...")
	proc = multiprocessing.Process(target=CLIENT_CALLBACK_WRAPPER, args=(client, callback, *args), kwargs=kwargs)
	proc.start()
	WATCHED_PROCESSES["client"] = proc

def SERVER_WRAPPER(server:"SocketWrapper.Server", callback:callable, *args, **kwargs):
	global SERVER_CALLBACK_WRAPPER
	global WATCHED_PROCESSES

	DEBUG.log_line("Starting server...")
	threading.Thread(target=server.start).start()
	time.sleep(0.5)

	DEBUG.log_line("Starting server callback...")
	proc = multiprocessing.Process(target=SERVER_CALLBACK_WRAPPER, args=(server, callback, *args), kwargs=kwargs)
	proc.start()
	WATCHED_PROCESSES["server"] = proc



class HandshakeSystemTest():
	def __init__(self):
		self.run_test()

	def handle_client(self, client:"SocketWrapper.Client"):
		time.sleep(5)

	def handle_server(self, server:"SocketWrapper.Server"):
		time.sleep(5)

	def run_test(self):
		DEBUG.log_line("Starting handshake system test...")

		server = SocketWrapper.Server("127.0.0.1", 1234)
		client = SocketWrapper.Client("127.0.0.1", 1234)

		SERVER_WRAPPER(server, self.handle_server)
		CLIENT_WRAPPER(client, self.handle_client)



class EncodingTest():
	def __init__(self, list_of_encodings=list[str]):
		for encoding in list_of_encodings:
			self.run_test(encoding)

	def handle_client(self, client:"SocketWrapper.Client"):
		out_pkt_r = SocketWrapper.OutputVar[SocketWrapper.Packet](None)
		client.recv(out_pkt_r)
		pkt_r = out_pkt_r.get()

		assert pkt_r.message == "Hello there!"

		pkt_s = SocketWrapper.Packet("Hello there!")
		client.send(pkt_s)

	def handle_server(self, server:"SocketWrapper.Server"):
		pkt_s = SocketWrapper.Packet("Hello there!")
		server.send(pkt_s)

		out_pkt_r = SocketWrapper.OutputVar[SocketWrapper.Packet](None)
		server.recv(out_pkt_r)
		pkt_r = out_pkt_r.get()

		assert pkt_r.message == "Hello there!"

	def run_test(self, encoding:str):
		global CLIENT_WRAPPER
		global SERVER_WRAPPER

		client = SocketWrapper.Client("127.0.0.1", 1234, encoding)
		server = SocketWrapper.Server("127.0.0.1", 1234, encoding)

		CLIENT_WRAPPER(client, self.handle_client)
		SERVER_WRAPPER(server, self.handle_server)



class BufferSizeTest():
	def __init__(self):
		self.run_test()

	def run_test(self):
		pass



class AnySuffixTest():
	def __init__(self):
		self.run_test()

	def run_test(self):
		pass



class AnySplitCharTest():
	def __init__(self):
		self.run_test()

	def run_test(self):
		pass



class PacketClassWithHeadersTest():
	def __init__(self):
		self.run_test()

	def run_test(self):
		pass



class ArgsAndKwargsTest():
	def __init__(self):
		self.run_test()

	def run_test(self):
		pass



class CallbacksTest():
	def __init__(self):
		self.run_test()

	def run_test(self):
		pass



class BandwidthSavingTest():
	def __init__(self):
		self.run_test()

	def run_test(self):
		pass



def RunAllTests():
	HandshakeSystemTest()
	#EncodingTest()
	#ArgsAndKwargsTest()
	#BufferSizeTest()
	#AnySuffixTest()
	#CallbacksTest()
	#PacketClassWithHeadersTest()
	#AnySplitCharTest()
	#BandwidthSavingTest()




if __name__ == "__main__":
	RunAllTests()