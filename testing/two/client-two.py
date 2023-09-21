import ptysocket.SocketWrapper
import random

def generate_random_data(chunk_size=1024):
	return ''.join([chr(random.randint(0, 255)) for _ in range(chunk_size)])

client = ptysocket.SocketWrapper.Client(
	host='127.0.0.1', port=2222,
	buffer_size=1,
)

client.connect()

client.send(generate_random_data())

client.disconnect()