from ptysocket.SocketWrapper import PacketHeader as SocketWrapperPacketHeader
from ptysocket.SocketWrapper import Packet as SocketWrapperPacket
from ptysocket.SocketWrapper import Server as SocketWrapperServer
from ptysocket.SocketWrapper import OutputVar
import random

def generate_random_data(chunk_size=1024):
	return ''.join([chr(random.randint(32, 126)) for _ in range(chunk_size)])

server = SocketWrapperServer(
	bind_address='0.0.0.0', port=2222,
	buffer_size=32,
)

server.start()

server.send(SocketWrapperPacket("hifdjgkdgklfgkljgkakgjdklagjfklghfjgdlhgkdjgkjdkagjkldagkdhasjfdsakfjdkajfkdahgkhdsajgdksagkdsalhgkldghkdhakgfjdklagkdhasklgdsaklg"))




out_packet = OutputVar[SocketWrapperPacket]()
server.recv(out_packet)
packet = out_packet()


print(f"Received: {repr(packet.msg)}")

server.stop()
