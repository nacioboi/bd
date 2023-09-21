import termios
import socket
import select
import pty
import os

class PTYSocketServer:
    def __init__(self, host='127.0.0.1', port=2222):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.client_socket, addr = self.server_socket.accept()
        self.run_pty(self.client_socket.recv(1024).decode('utf-8')) # get the program to run.

    def stop(self):
        self.client_socket.close()
        self.server_socket.close()

    def recv(self):
        return self.client_socket.recv(1024).decode('utf-8')

    def send(self, data):
        self.client_socket.sendall(data.encode('utf-8'))

    def run_pty(self, program):
        pid, fd = pty.fork()
        if pid == 0:  # Child
            os.execv(program, [program])
        else:  # Parent
            try:
                while True:
                    r, w, e = select.select([self.client_socket, fd], [], [])
                    if self.client_socket in r:
                        data = self.recv()
                        if not data:
                            break
                        os.write(fd, data.encode('utf-8'))
                    
                    if fd in r:
                        data = os.read(fd, 1024)
                        if not data:
                            break
                        self.send(data.decode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
            finally:
                self.stop()