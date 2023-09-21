import ptysocket.SocketWrapper

server = ptysocket.SocketWrapper.Server(
	bind_address='0.0.0.0',
	port=2222,
	buffer_size=1,
)

server.start()

packet = server.recv()

print(f"Received: {packet.msg}")

server.stop()
