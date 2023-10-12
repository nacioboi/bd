from ptysocket import PTYSocketClient as Client
from ptysocket import PTYSocketServer as Server
from ptysocket.SocketWrapper import PacketHeader
from ptysocket.SocketWrapper import OutputVar
from ptysocket.SocketWrapper import Packet

import unittest

import threading
import random
import socket
import sys



class TestArgumentsFeatureForSocketWrapper(unittest.TestCase):
	
	def make_server(self, p):
		_server = Server(
			bind_address="127.0.0.1", port=p, *(), **{
				"family": socket.AF_INET,
				"type": socket.SOCK_STREAM,
				"proto": 0,
				"fileno": None
			}
		)
		_server.start()
		return _server
	
	def make_client(self, p):
		_client = Client(
			host="127.0.0.1", port=p, *(), **{
				"family": socket.AF_INET,
				"type": socket.SOCK_STREAM,
				"proto": 0,
				"fileno": None
			}
		)
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
			server = self.make_server(p)

			pkt1 = Packet("hello there!")
			server.send(pkt1)

			out_pkt2 = OutputVar[Packet]()
			server.recv(out_pkt2)
			pkt2 = out_pkt2()

			self.confirm_server(pkt1, pkt2)

			out_ret._set(True)
		except:
			out_ret._set(False)
		finally:
			server.stop()
	
	def client_tester(self, p:int, out_ret:"OutputVar[bool]"):
		try:
			client = self.make_client(p)

			out_pkt1 = OutputVar[Packet]()
			client.recv(out_pkt1)
			pkt1 = out_pkt1()

			pkt2 = Packet("hello there!")
			client.send(pkt2)

			self.confirm_client(pkt1, pkt2)

			out_ret._set(True)
		except:
			out_ret._set(False)
		finally:
			client.stop()

	def test_server_and_client(self):
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



class TestCallbackFeatureForSocketWrapper(unittest.TestCase):
	
	def add_one(self, out:"OutputVar[int]"):
		_a = out()
		_a = _a + 1
		out._set(_a)

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
			c._set(1)

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

			out_ret._set(True)
		except:
			out_ret._set(False)
		finally:
			server.stop()
		
	def client_tester(self, p:int, out_ret:"OutputVar[bool]"):
		try:
			c = OutputVar[int]()
			c._set(1)

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

			out_ret._set(True)
		except:
			out_ret._set(False)
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
	unittest.main()

