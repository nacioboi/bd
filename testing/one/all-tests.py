from ptysocket.SocketWrapper import Server
from ptysocket.SocketWrapper import Client
from ptysocket.SocketWrapper import PacketHeader
from ptysocket.SocketWrapper import OutputVar
from ptysocket.SocketWrapper import Packet

import woody

import threading
import random
import socket
import time
import os



woody.Woody(f"{os.getcwd()}/logs")

DEBUG_CONTEXT = woody.DebugContext(
	"debug", 
	do_save_logs=True,
	do_use_time=True,
	colors=woody.ColorConfiguration._default(),
	time_format=""
)
DEBUG_CONTEXT.simple_log_line(f"[{DEBUG_CONTEXT.get_time()}]~>>>{DEBUG_CONTEXT.get_reset_poison()}Started a new!")



RETRY_NOW = False
RETRY_COUNT = 3



class TestArgumentsFeatureForSocketWrapper:

	def confirm(self, pkt1, pkt2):
		DEBUG_CONTEXT.log_line("Confirming server...")

		assert isinstance(pkt1, Packet)
		assert isinstance(pkt2, Packet)

		assert pkt1.msg == "hello there!"
		assert pkt2.msg == "hello there!"

		assert isinstance(pkt1.header, PacketHeader)
		assert isinstance(pkt2.header, PacketHeader)

		assert pkt1.header == PacketHeader()
		assert pkt2.header == PacketHeader()

	def server_tester(self, p:int, out_server:"OutputVar[Server]", out_ret:"OutputVar[bool]", out_done:"OutputVar[bool]"):
		try:
			DEBUG_CONTEXT.log_line("Creating server...")
			out_server.set(Server(
				bind_address="127.0.0.1", port=p, *(), **{
					"family": socket.AF_INET,
					"type": socket.SOCK_STREAM,
					"proto": 0,
					"fileno": None
				}
			))
			DEBUG_CONTEXT.log_line("Starting server...")
			out_server().start()

			DEBUG_CONTEXT.log_line("Sending packet...")
			pkt1 = Packet("hello there!")
			out_server().send(pkt1)

			DEBUG_CONTEXT.log_line("Receiving packet...")
			out_pkt2 = OutputVar[Packet](None)
			out_server().recv(out_pkt2)
			pkt2 = out_pkt2()

			self.confirm(pkt1, pkt2)

			out_ret.set(True)
			out_done.set(True)
		except Exception as e:
			out_ret.set(False)
			out_done.set(True)
			print(e, flush=True)
		finally:
			DEBUG_CONTEXT.log_line("Ending... Attempting to stop server...")
			if not out_server().stop(True):
				DEBUG_CONTEXT.log_line("ERROR: Failed to stop server.")
	
	def client_tester(self, p:int, out_client:"OutputVar[Client]", out_ret:"OutputVar[bool]", out_done:"OutputVar[bool]"):
		try:
			DEBUG_CONTEXT.log_line("Creating client...")
			out_client.set(Client(
				host="127.0.0.1", port=p, *(), **{
					"family": socket.AF_INET,
					"type": socket.SOCK_STREAM,
					"proto": 0,
					"fileno": None
				}
			))
			DEBUG_CONTEXT.log_line("Starting client...")
			out_client().start()

			DEBUG_CONTEXT.log_line("Receiving packet...")
			out_pkt1 = OutputVar[Packet](None)
			out_client().recv(out_pkt1)
			pkt1 = out_pkt1()
			
			DEBUG_CONTEXT.log_line("Sending packet...")
			pkt2 = Packet("hello there!")
			out_client().send(pkt2)

			self.confirm(pkt1, pkt2)

			out_ret.set(True)
			out_done.set(True)
		except Exception as e:
			out_ret.set(False)
			out_done.set(True)
			print(e, flush=True)
		finally:
			DEBUG_CONTEXT.log_line("Ending... Attempting to stop client...")
			if not out_client().stop(True):
				DEBUG_CONTEXT.log_line("ERROR: Failed to stop client.")

	def watcher(self, out_server:"OutputVar[Server]", out_client:"OutputVar[Client]", out_do_retry:"OutputVar[bool]"):
		global RETRY_COUNT
		global RETRY_NOW
		while True:
			if RETRY_NOW:
				RETRY_NOW = False
				RETRY_COUNT = RETRY_COUNT - 1
				if RETRY_COUNT >= 0:
					DEBUG_CONTEXT.log_line("Retrying...")
					out_server().stop(True)
					out_client().stop(True)
					time.sleep(1)
					out_do_retry.set(True)
					break
			time.sleep(0.1)


	def test_server_and_client(self):
		port = random.randint(1000, 65535)
		DEBUG_CONTEXT.log_line(f"Generated random port: [{port}].")

		server_out_ret = OutputVar[bool](False)
		client_out_ret = OutputVar[bool](False)

		server_out_done = OutputVar[bool](False)
		client_out_done = OutputVar[bool](False)

		server_out_server = OutputVar[Server](None)
		client_out_client = OutputVar[Client](None)

		watcher_out_do_retry = OutputVar[bool](False)

		server_thread = threading.Thread(target=self.server_tester, args=(port, server_out_server, server_out_ret, server_out_done))
		client_thread = threading.Thread(target=self.client_tester, args=(port, client_out_client, client_out_ret, client_out_done))
		watcher_thread = threading.Thread(target=self.watcher, args=(server_out_server, client_out_client, watcher_out_do_retry))

		server_thread.start()
		time.sleep(1)
		client_thread.start()
		time.sleep(1)
		watcher_thread.start()

		DEBUG_CONTEXT.log_line("Started all threads...")

		DEBUG_CONTEXT.log_line("Waiting for server and client threads to finish...")
		while not (server_out_done() and client_out_done()):
			pass
		
		DEBUG_CONTEXT.log_line("Server and client threads finished.")

		if watcher_out_do_retry:
			DEBUG_CONTEXT.log_line("Watcher thread requested a retry.")
			server_thread.join()
			client_thread.join()
			watcher_thread.join()
			self.test_server_and_client()
		else:
			DEBUG_CONTEXT.log_line("Watcher thread did not request a retry.")
			server_thread.join()
			client_thread.join()
			watcher_thread.join()

		assert server_out_ret() == True
		assert client_out_ret() == True



class TestCallbackFeatureForSocketWrapper:#(unittest.TestCase):
	
	def add_one(self, out:"OutputVar[int]"):
		_a = out()
		_a = _a + 1
		out.set(_a)

	def make_server(self, p:int, on_receive, on_send):
		_server = Server(bind_address="0.0.0.0", port=p)
		_server.define_recv_callback(on_receive)
		_server.define_send_callback(on_send)
		_server.start()
		return _server
	
	def make_client(self, p, on_receive, on_send):
		_client = Client(host="127.0.0.1", port=p)
		_client.define_recv_callback(on_receive)
		_client.define_send_callback(on_send)
		_client.start()
		return _client

	def confirm_server(self, pkt1, pkt2):
		self.assertEqual(pkt1.msg, "hello there!")
		self.assertEqual(pkt2.msg, "hello there!")

		self.assertEqual(pkt1.header, PacketHeader())
		self.assertEqual(pkt2.header, PacketHeader())

	def confirm_client(self, pkt1, pkt2):
		self.assertEqual(pkt1.msg, "hello there!")
		self.assertEqual(pkt2.msg, "hello there!")

		self.assertEqual(pkt1.header, PacketHeader())
		self.assertEqual(pkt2.header, PacketHeader())
	
	def server_tester(self, p:int, out_ret:"OutputVar[bool]"):
		try:
			c = OutputVar[int]()
			c.set(1)

			def on_receive(packet:Packet):
				self.add_one(c)
				return packet
			
			def on_send(packet:Packet):
				self.add_one(c)
				return packet
			
			server = self.make_server(p, on_receive, on_send)

			pkt1 = Packet("hello there!")
			server.send(pkt1)
			self.assertEqual(c(), 2)

			out_pkt2 = OutputVar[Packet]()
			server.recv(out_pkt2)
			pkt2 = out_pkt2()
			self.assertEqual(c(), 3)

			self.confirm_server(pkt1, pkt2)

			out_ret.set(True)
		except:
			out_ret.set(False)
		finally:
			server.stop()
		
	def client_tester(self, p:int, out_ret:"OutputVar[bool]"):
		try:
			c = OutputVar[int]()
			c.set(1)

			def on_receive(packet:Packet):
				self.add_one(c)
				return packet
			
			def on_send(packet:Packet):
				self.add_one(c)
				return packet
			
			client = self.make_client(p, on_receive, on_send)

			out_pkt1 = OutputVar[Packet]()
			client.recv(out_pkt1)
			pkt1 = out_pkt1()
			self.assertEqual(c(), 2)

			pkt2 = Packet("hello there!")
			client.send(pkt2)
			self.assertEqual(c(), 3)

			self.confirm_client(pkt1, pkt2)

			out_ret.set(True)
		except:
			out_ret.set(False)
		finally:
			client.stop()

	def test_both_server_and_client(self):
		port = random.randint(1000, 65535)

		server_out_ret = OutputVar[bool]()
		client_out_ret = OutputVar[bool]()

		server_thread = threading.Thread(target=self.server_tester, args=(port, server_out_ret))
		client_thread = threading.Thread(target=self.client_tester, args=(port, client_out_ret))

		server_thread.start()
		client_thread.start()

		server_thread.join()
		client_thread.join()

		self.assertTrue(server_out_ret())
		self.assertTrue(client_out_ret())



class TestPacketHeaderFeatureForSocketWrapper:#(unittest.TestCase):
	
	def make_server(self, p:int):
		_server = Server(bind_address="127.0.0.1", port=p)
		_server.start()
		return _server
	
	def make_client(self, p:int):
		_client = Client(host="127.0.0.1", port=p)
		_client.start()
		return _client
	
	def confirm_server(self, pkt1, pkt2):
		self.assertEqual(pkt1.msg, "hello there!")
		self.assertEqual(pkt2.msg, "hello there!")

		self.assertEqual(pkt1.header["header_1"], 2)
		self.assertEqual(pkt1.header["header_2"], "test")
		self.assertEqual(pkt1.header["header_3"], True)

	def confirm_client(self, pkt1, pkt2):
		self.assertEqual(pkt1.msg, "hello there!")
		self.assertEqual(pkt2.msg, "hello there!")

		self.assertEqual(pkt1.header["header_1"], 2)
		self.assertEqual(pkt1.header["header_2"], "test")
		self.assertEqual(pkt1.header["header_3"], True)

	def server_tester(self, p:int, out_ret:"OutputVar[bool]"):
		try:
			server = self.make_server(p)

			pkt1 = Packet("hello there!", PacketHeader(
				header_1=2,
				header_2="test",
				header_3=True
			))
			server.send(pkt1)

			out_pkt2 = OutputVar[Packet]()
			server.recv(out_pkt2)
			pkt2 = out_pkt2()

			self.confirm_server(pkt1, pkt2)

			out_ret.set(True)
		except:
			out_ret.set(False)
		finally:
			server.stop()
	
	def client_tester(self, p:int, out_ret:"OutputVar[bool]"):
		try:
			client = self.make_client(p)

			out_pkt1 = OutputVar[Packet]()
			client.recv(out_pkt1)
			pkt1 = out_pkt1()

			pkt2 = Packet("hello there!", PacketHeader(
				header_1=2,
				header_2="test",
				header_3=True
			))
			client.send(pkt2)

			self.confirm_client(pkt1, pkt2)

			out_ret.set(True)
		except:
			out_ret.set(False)
		finally:
			client.stop()
		
	def test_both_server_and_client(self):
		port = random.randint(1000, 65535)

		server_out_ret = OutputVar[bool]()
		client_out_ret = OutputVar[bool]()

		server_thread = threading.Thread(target=self.server_tester, args=(port, server_out_ret))
		client_thread = threading.Thread(target=self.client_tester, args=(port, client_out_ret))

		server_thread.start()
		client_thread.start()

		server_thread.join()
		client_thread.join()

		self.assertTrue(server_out_ret())
		self.assertTrue(client_out_ret())

if __name__ == "__main__":
	DEBUG_CONTEXT.set_class_name("TestArgumentsFeatureForSocketWrapper")
	TestArgumentsFeatureForSocketWrapper().test_server_and_client()

