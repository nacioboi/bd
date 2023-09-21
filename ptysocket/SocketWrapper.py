import socket
import json

class PacketHeader:
	def __init__(self, **kwargs):
		# convert the kwargs to a json string
		self._json = json.dumps(kwargs)
	
	def _shrink_json(self, json_str):
		# TODO: do some processing, probably some kind of compression
		return json_str

	def __str__(self):
		return self._shrink_json(self._json)

class Packet:
	"""
	Part of the `SocketWrapper` module.
	Represents a packet.
	"""

	def __init__(self, msg:str, header:'PacketHeader'=PacketHeader(), splitter:str='\u0000'):
		"""
		Args:
			msg (str): The message to send.
			header (PacketHeader, optional): Any other special information.
				The header will not be sent every time if the last packet sent had the same header,
				in other words, only the relevant changes will be sent.
				Defaults to PacketHeader().
			splitter (str, optional): The header and the message are split by this sequence.
				Defaults to '\u0000'.
		"""
		self.header = header
		self.msg = msg
		self._splitter = splitter

	def decode(self) -> str:
		"""
		Decodes the packet into its string representation.

		Returns:
			str: The string representation of the packet.
		"""
		return f"{self.header}{self._splitter}{self.msg}"
	
	@classmethod
	def encode(self, pkt_string:str, split_char:str='\u0000') -> 'Packet':
		"""
		Encodes a string representation of a packet into a `Packet` object.

		Args:
			pkt_string (str): The string representation of the packet.
			split_char (str, optional): The header and the message are split by this sequence.
				Defaults to '\u0000'.

		Returns:
			Packet: The `Packet` object.
		"""
		x = pkt_string.split(split_char)
		h, m = x[0], x[1]
		return Packet(m, header=h, splitter=split_char)

class Client:
	"""
	A client for the `SocketWrapper` module.

	Features:` \n
		- Set your own encoding.\n
		- Don't worry about buffer sizes anymore as the module, when receiving, will wait until receiving the suffix. Once the suffix is
			received, the module will stop receiving and return the message.\n
		- Set your own suffix.\n
		- Set your own split char. The split char is the character that splits the header and the message.\n
		- Packet class makes life easier by allowing you to send headers and messages in one packet.\n
		- Set *args and **kwargs for the socket object.\n
		- Set callbacks for receiving and sending.\n
			\t- The callback for sending will be called before sending the packet, allowing you to modify the packet before sending it.\n
			\t- The callback for receiving will be called after receiving the packet, allowing you to modify the packet after receiving it.\n
			\t- Each callback will be called every time a packet is sent/received.\n
		- Handshake system to make sure the server and the client are compatible.\n
		- Saves on bandwidth by only sending the header when it changes. This module does not however save on bandwidth on the message
			itself. This is because the message should be quick to access and modify, and since the message is usually larger than the
			header, it would take too much time to compress it.\n
	`
	"""

	def __init__(self, host, port, encoding='utf-8', buffer_size=512, suffix='\u0003', split_char='\u0000', *socket_args, **socket_kwargs):
		self._host = host
		self._port = port
		self._encoding = encoding
		self._buffer_size = buffer_size
		self._suffix = suffix
		self._split_char = split_char

		self._sock = socket.socket(*socket_args, **socket_kwargs)

		self._recv_callback = lambda msg: msg
		self._send_callback = lambda packet: packet

		self._decode_msg = lambda msg: msg.decode(self._encoding)
		self._encode_msg = lambda msg: msg.encode(self._encoding)

		self._recv = lambda: Packet.encode(self._decode_msg(self._sock.recv(self._buffer_size)), self._split_char)
		self._send = lambda packet: self._sock.sendall(self._encode_msg(packet.encode()))
	
	def _handle_handshake(self):
		# we need to send off:
		# 	- encoding,
		# 	- buffer_size,
		# 	- suffix,
		# 	- split_char
		# to the server in order to make sure they're compatible.
		# we need to do this without any suffix so we need a sufficiently large buffer size.
		# we also must use both on the server and the client, the same encoding.

		# the server always sends first, so we need to receive first.
		msg = self._decode_msg(self._sock.recv(1024))
		msg = Packet.encode(msg)

		# we will send off our header now.
		self._sock.sendall(self._encode_msg(
			Packet(
				msg="",
				header=PacketHeader(
					type='handshake',
					encoding=self._encoding,
					buffer_size=self._buffer_size,
					suffix=self._suffix,
					split_char=self._split_char,
				)
			).decode()
		))

		if msg.header.encoding != self._encoding:
			self._sock.close()
			raise ValueError(f"Encoding mismatch: expected {self._encoding}, got {msg.header.encoding}")
		if msg.header.buffer_size != self._buffer_size:
			self._sock.close()
			raise ValueError(f"Buffer size mismatch: expected {self._buffer_size}, got {msg.header.buffer_size}")
		if msg.header.suffix != self._suffix:
			self._sock.close()
			raise ValueError(f"Suffix mismatch: expected {self._suffix}, got {msg.header.suffix}")
		if msg.header.split_char != self._split_char:
			self._sock.close()
			raise ValueError(f"Split char mismatch: expected {self._split_char}, got {msg.header.split_char}")

	def connect(self):
		self._sock.connect((self._host, self._port))
		self._handle_handshake()
	
	def disconnect(self):
		self._sock.close()

	def define_recv_callback(self, callback):
		self._recv_callback = callback

	def define_send_callback(self, callback):
		self._send_callback = callback
	
	def recv(self):
		msg = self._recv()
		return self._recv_callback(msg)
	
	def send(self, packet):
		p = self._send_callback(packet)
		self._send(self._encode_msg(f"{p.msg}{self._suffix}"))

class Server:
	"""
	A server for the `SocketWrapper` module.

	Features:` \n
		- Set your own encoding.\n
		- Don't worry about buffer sizes anymore as the module, when receiving, will wait until receiving the suffix. Once the suffix is
			received, the module will stop receiving and return the message.\n
		- Set your own suffix.\n
		- Set your own split char. The split char is the character that splits the header and the message.\n
		- Packet class makes life easier by allowing you to send headers and messages in one packet.\n
		- Set *args and **kwargs for the socket object.\n
		- Set callbacks for receiving and sending.\n
			\t- The callback for sending will be called before sending the packet, allowing you to modify the packet before sending it.\n
			\t- The callback for receiving will be called after receiving the packet, allowing you to modify the packet after receiving it.\n
			\t- Each callback will be called every time a packet is sent/received.\n
		- Handshake system to make sure the server and the client are compatible.\n
		- Saves on bandwidth by only sending the header when it changes. This module does not however save on bandwidth on the message
			itself. This is because the message should be quick to access and modify, and since the message is usually larger than the
			header, it would take too much time to compress it.\n
	`
	"""

	def __init__(self, bind_address, port, encoding='utf-8', buffer_size=512, suffix='\u0003', split_char='\u0000', *socket_args, **socket_kwargs):
		self._bind_address = bind_address
		self._port = port
		self._encoding = encoding
		self._buffer_size = buffer_size
		self._suffix = suffix
		self._split_char = split_char

		self._sock = socket.socket(*socket_args, **socket_kwargs)

		self._recv_callback = lambda msg: msg
		self._send_callback = lambda packet: packet

		self._decode_msg = lambda msg: msg.decode(self._encoding)
		self._encode_msg = lambda msg: msg.encode(self._encoding)
		
		self._recv = lambda: Packet.encode(self._decode_msg(self._sock.recv(self._buffer_size)), self._split_char)
		self._send = lambda packet: self._sock.sendall(self._encode_msg(packet.encode()))

	def _handle_handshake(self):
		# we need to send off:
		# 	- encoding,
		# 	- buffer_size,
		# 	- suffix,
		# 	- split_char
		# to the server in order to make sure they're compatible.
		# we need to do this without any suffix so we need a sufficiently large buffer size.
		# we also must use both on the server and the client, the same encoding.

		# we will send off our header now.
		self._sock.sendall(self._encode_msg(
			Packet(
				msg="",
				header=PacketHeader(
					type='handshake',
					encoding=self._encoding,
					buffer_size=self._buffer_size,
					suffix=self._suffix,
					split_char=self._split_char,
				)
			).decode()
		))

		# the server always sends first, so we need to receive first.
		msg = self._decode_msg(self._sock.recv(1024))
		msg = Packet.encode(msg)

		if msg.header.encoding != self._encoding:
			self._sock.close()
			raise ValueError(f"Encoding mismatch: expected {self._encoding}, got {msg.header.encoding}")
		if msg.header.buffer_size != self._buffer_size:
			self._sock.close()
			raise ValueError(f"Buffer size mismatch: expected {self._buffer_size}, got {msg.header.buffer_size}")
		if msg.header.suffix != self._suffix:
			self._sock.close()
			raise ValueError(f"Suffix mismatch: expected {self._suffix}, got {msg.header.suffix}")
		if msg.header.split_char != self._split_char:
			self._sock.close()
			raise ValueError(f"Split char mismatch: expected {self._split_char}, got {msg.header.split_char}")
		
	def start(self):
		self._sock.bind((self._bind_address, self._port))
		self._sock.listen()
		self._sock, _ = self._sock.accept()
		self._handle_handshake()

	def stop(self):
		self._sock.close()

	def define_recv_callback(self, callback):
		self._recv_callback = callback

	def define_send_callback(self, callback):
		self._send_callback = callback

	def recv(self):
		msg = self._recv()
		return self._recv_callback(msg)
	
	def send(self, packet):
		p = self._send_callback(packet)
		self._send(self._encode_msg(f"{p.msg}{self._suffix}"))
