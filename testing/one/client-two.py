from ptysocket.SocketWrapper import PacketHeader as SocketWrapperPacketHeader
from ptysocket.SocketWrapper import Packet as SocketWrapperPacket
from ptysocket.SocketWrapper import Client as SocketWrapperClient
from ptysocket.SocketWrapper import OutputVar
import random

def generate_random_data(chunk_size=1024):
	return ''.join([chr(random.randint(32, 126)) for _ in range(chunk_size)])

client = SocketWrapperClient(
	host='127.0.0.1', port=2222,
	buffer_size=32,
)

client.start()

out_packet = OutputVar[SocketWrapperPacket]()
client.recv(out_packet)
packet = out_packet()
print(f"Received: {repr(packet.msg)}")

client.send(SocketWrapperPacket(generate_random_data()))






client.stop()
