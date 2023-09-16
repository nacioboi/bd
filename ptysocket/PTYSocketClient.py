import threading
import termios
import socket
import select
import queue
import sys
import tty

class PTYSocketClient:
    def __init__(self, host='127.0.0.1', port=2222):
        self.host = host
        self.port = port
        self.client_socket = socket.socket()
        self.key_queue = queue.Queue()

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        self.stdin_thread = threading.Thread(target=self.read_stdin, args=(self.key_queue,))
        self.stdin_thread.daemon = True
        self.stdin_thread.start()
        self.run()

    def disconnect(self):
        self.client_socket.close()

    def get_single_keypress(self):
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return ch

    def read_stdin(self, key_queue):
        while True:
            key = self.get_single_keypress()
            key_queue.put(key)

    def recv(self):
        return self.client_socket.recv(1024).decode('utf-8')

    def send(self, data):
        self.client_socket.sendall(data.encode('utf-8'))

    def run(self):
        try:
            while True:
                readable, _, _ = select.select([self.client_socket], [], [], 0.1)
                for s in readable:
                    if s is self.client_socket:
                        data = self.recv()
                        if not data:
                            return
                        print(data, end="", flush=True)
                
                try:
                    user_input = self.key_queue.get_nowait()
                    self.send(user_input)
                except queue.Empty:
                    pass
        finally:
            self.disconnect()
