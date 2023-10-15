import multiprocessing
import socket
import json
import time
from typing import Any
from typing import TypeVar, Generic



def STOP_SOCK(s:socket.socket, out_success:"OutputVar[bool]"):
	s.close()
	out_success.set(True)



T = TypeVar("T")

class OutputVar(Generic[T]):
	def __init__(self, value:T) -> None:
		self._value = value

	def set(self, value:T) -> None:
		self._value = value

	def __call__(self, *args: Any, **kwds: Any) -> T:
		if len(args) != 0 or len(kwds) != 0:
			raise TypeError("OutputVar object is not callable with arguments")
		return self._value



class PacketHeader:
	def __init__(self, **kwargs):
		# convert the kwargs to a json string
		self._json = json.dumps(kwargs)

	def __call__(self, *args, **kwargs) -> str:
		return self._json



class Packet:
	"""
	Part of the `SocketWrapper` module.
	Represents a packet.
	"""

	def __init__(self, msg:str, header:'PacketHeader'=PacketHeader(), splitter:str='\U000f0000'):
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
		self.header = json.loads(header())
		self.msg = msg
		self._splitter = splitter

	def decode(self, do_repr_splitter=False) -> str:
		"""
		Decodes the packet into its string representation.

		Returns:
			str: The string representation of the packet.
		"""
		return f"{self.header}{repr(self._splitter) if do_repr_splitter else self._splitter}{self.msg}"
	
	@classmethod
	def encode(self, pkt_string:str, split_char:str='\U000f0000') -> 'Packet':
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
		if len(x) == 1:
			return Packet(x[0], header=PacketHeader(), splitter=split_char)
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

	def __init__(self, host:str, port:int, encoding:str='utf-8', buffer_size:int=512, suffix:chr='\U000f0000',
			split_char:chr='\u0000', *socket_args, **socket_kwargs) -> None:
		self._host = host
		self._port = port
		self._encoding = encoding
		self._buffer_size = buffer_size
		self._suffix = suffix
		self._split_char = split_char

		self._sock = socket.socket(*socket_args, **socket_kwargs)

		self._recv_callback = lambda packet: packet
		self._send_callback = lambda packet: packet

		self._decode_msg = lambda msg: msg.decode(self._encoding)
		self._encode_msg = lambda msg: msg.encode(self._encoding)

		self._recv = lambda: Packet.encode(self._decode_msg(self._sock.recv(self._buffer_size)), self._split_char)
		self._send = lambda packet: self._sock.sendall(self._encode_msg(packet.decode()))
	
	def _handle_handshake(self) -> None:
		sock = socket.socket()
		sock.connect((self._host, self._port))

		r_msg = sock.recv(1024).decode('utf-8')
		encoding, buffer_size, suffix, split_char = r_msg.split('\u0001')

		s_msg = ""
		s_msg += str(self._encoding)
		s_msg += "\u0001"
		s_msg += str(self._buffer_size)
		s_msg += "\u0001"
		s_msg += str(self._suffix)
		s_msg += "\u0001"
		s_msg += str(self._split_char)

		sock.sendall(s_msg.encode('utf-8'))

		sock.close()

		if str(encoding) != (self._encoding):
			raise ValueError(f"Encoding mismatch: expected [{repr(self._encoding)}], got [{repr(encoding)}]")
		if str(buffer_size) != str(self._buffer_size):
			raise ValueError(f"Buffer size mismatch: expected [{repr(self._buffer_size)}], got [{repr(buffer_size)}]")
		if str(suffix) != str(self._suffix):
			raise ValueError(f"Suffix mismatch: expected [{repr(self._suffix)}], got [{repr(suffix)}]")
		if str(split_char) != str(self._split_char):
			raise ValueError(f"Split char mismatch: expected [{repr(self._split_char)}], got [{repr(split_char)}]")

	def start(self) -> None:
		self._handle_handshake()
		time.sleep(0.25)
		self._sock.connect((self._host, self._port))
	
	def stop(self, non_blocking:bool=False) -> bool:
		global STOP_SOCK
		success = OutputVar[bool](False)
		if non_blocking:
			proc = multiprocessing.Process(target=STOP_SOCK, args=(self._sock, success))
			proc.start()
			time.sleep(5)
			proc.terminate()
			proc.join()
		else:
			self._sock.stop()
			success.set(True)
		return success()
			

	def define_recv_callback(self, callback) -> None:
		self._recv_callback = callback

	def define_send_callback(self, callback) -> None:
		self._send_callback = callback
	
	def recv(self, out_packet:OutputVar[Packet]) -> None:
		msgs = [self._recv()]
		while not msgs[len(msgs)-1].msg.endswith(self._suffix):
			msgs.append(self._recv())
		header = msgs[0].header
		msg = ""
		for m in msgs:
			msg += m.msg
		if repr(header) == "{}":
			pkt = Packet(msg.strip(self._suffix), header=PacketHeader(), splitter=self._split_char)
		else:
			pkt = Packet(msg.strip(self._suffix), header=PacketHeader(header), splitter=self._split_char)
		return out_packet.set(self._recv_callback(pkt))
	
	def send(self, packet:Packet) -> None:
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

	def __init__(self, bind_address:str, port:int, encoding:str='utf-8', buffer_size:int=512, suffix:chr='\U000f0000',
			split_char:chr='\u0000', *socket_args, **socket_kwargs) -> None:
		self._bind_address = bind_address
		self._port = port
		self._encoding = encoding
		self._buffer_size = buffer_size
		self._suffix = suffix
		self._split_char = split_char

		self._sock = socket.socket(*socket_args, **socket_kwargs)

		self._recv_callback = lambda packet: packet
		self._send_callback = lambda packet: packet

		self._decode_msg = lambda msg: msg.decode(self._encoding)
		self._encode_msg = lambda msg: msg.encode(self._encoding)
		
		self._recv = lambda: Packet.encode(self._decode_msg(self._sock.recv(self._buffer_size)), self._split_char)
		self._send = lambda packet: self._sock.sendall(self._encode_msg(packet.decode()))

	def _handle_handshake(self) -> None:
		s = socket.socket()
		s.bind((self._bind_address, self._port))
		s.listen()
		sock, _ = s.accept()

		s_msg = ""
		s_msg += str(self._encoding)
		s_msg += "\u0001"
		s_msg += str(self._buffer_size)
		s_msg += "\u0001"
		s_msg += str(self._suffix)
		s_msg += "\u0001"
		s_msg += str(self._split_char)

		sock.sendall(s_msg.encode('utf-8'))

		r_msg = sock.recv(1024).decode('utf-8')
		encoding, buffer_size, suffix, split_char = r_msg.split('\u0001')

		s.close()
		sock.close()

		if str(encoding) != str(self._encoding):
			raise ValueError(f"Encoding mismatch: expected [{repr(self._encoding)}], got [{repr(encoding)}]")
		if str(buffer_size) != str(self._buffer_size):
			raise ValueError(f"Buffer size mismatch: expected [{repr(self._buffer_size)}], got [{repr(buffer_size)}]")
		if str(suffix) != str(self._suffix):
			raise ValueError(f"Suffix mismatch: expected [{repr(self._suffix)}], got [{repr(suffix)}]")
		if str(split_char) != str(self._split_char):
			raise ValueError(f"Split char mismatch: expected [{repr(self._split_char)}], got [{repr(split_char)}]")

	def start(self) -> None:
		self._handle_handshake()
		time.sleep(0.25)
		self._sock.bind((self._bind_address, self._port))
		self._sock.listen()
		self._sock, _ = self._sock.accept()

	def stop(self, non_blocking:bool=False) -> bool:
		global STOP_SOCK
		success = OutputVar[bool](False)
		if non_blocking:
			proc = multiprocessing.Process(target=STOP_SOCK, args=(self._sock, success))
			proc.start()
			time.sleep(5)
			proc.terminate()
			proc.join()
		else:
			self._sock.stop()
			success.set(True)
		return success()

	def define_recv_callback(self, callback) -> None:
		self._recv_callback = callback

	def define_send_callback(self, callback) -> None:
		self._send_callback = callback

	def recv(self, out_packet:OutputVar[Packet]) -> None:
		msgs = [self._recv()]
		while not msgs[len(msgs)-1].msg.endswith(self._suffix):
			msgs.append(self._recv())
		header = msgs[0].header
		msg = ""
		for m in msgs:
			msg += m.msg
		if repr(header) == "{}":
			pkt = Packet(msg.strip(self._suffix), header=PacketHeader(), splitter=self._split_char)
		else:
			pkt = Packet(msg.strip(self._suffix), header=PacketHeader(header), splitter=self._split_char)
		return out_packet.set(self._recv_callback(pkt))
	
	def send(self, packet:Packet) -> None:
		p = self._send_callback(packet)
		self._send(self._encode_msg(f"{p.msg}{self._suffix}"))
