# How to configure protocol.json.

## The concept.

This project uses a neat idea of having all the communication that could take place,
or in other words, the protocol, all defined in one place.
This is of course configured in the `protocol.json` file.

As stated in the `READ_ME.md`, you must build the backdoor, and this is because
the `protocol.json` file is baked into a copy of the source code of the backdoor.
This is done to make sure that the client and server code are in sync and always agree
upon the protocol they should use.

Another benefit is that you can see clear as day everything that can take place in
communication between the client and server all in one place, no hidden code.

## Top level variables.

You must have the following defined in the root of the json object:

### `buffer-size`:
- The size of the buffer to use when sending and receiving data.
- type: number.
- note: size in bytes.

### `attacker-ip`:
- The ip address of the attackers machine.
- type: string.

### `fallback-ip`:
- The ip address of the fallback server.
- type: string.
- note: this server should always be running so that the client can connect to it even if the attackers machine is not online.

### `acceptable-ports`:
- the acceptable ports that the protocol will run on.
- type: array that can have numbers or strings as children.
- note: this can have just one port in it, but it is recommended to have more than one.
	we recommend this incase of the victims machine having a port being used or blocked.
	you may also specify ranges of ports using a string in the format of `start:end`.

### `message-suffix`:
- The suffix that defines the end of every message.
- type: string.
- note: we need this because sometimes the buffer_size is still too small. 
	so we can keep reading from the socket, buffer-size bytes at a time, until we find this suffix.

## Sub protocols.

A sub protocol is a protocol that is used for a specific purpose.
NOTE: **the server always sends the first message.**

Here are the possible options:
1. `handshake-sub-protocol`:
	- this is the protocol that is used at the very start of the communication.
2. `fallback-communications-sub-protocol`:
	- this is the protocol that is used when the attackers machine is not online and fallback communications are to take place.
3. `normal-sub-protocol`:
	- this is the protocol that is used when the attackers machine is online and normal communications are to take place.

So use the above as a root element of the json object that can accept the following properties.

### child properties.

- `messages`:
	-this is an array of messages that can be sent and received, the same properties of this applies to both the client and server.
	- type: array of objects.
- `server`:
	- this is required if the above, `messages`, is not defined. the server specific messages.
	- type: array of objects.
- `client`:
	- this is required if the above, `messages`, is not defined. the client specific messages.
	- type: array of objects.


### message properties.

The following properties are available for all three child properties of all three sub protocols (stated above).

- `unconditional-sequence`:
	- this is an array of messages that must be sent or received in order.
		remember, as stated in a note above, the server always sends the first message.
	- type: array of string.
	- note: the string is in a special format that is explained below.
	- acceptable children:
		- `unconditional-sequence`:
			- see below
- `function-configurations`:
	- this is an array of objects that define the functions that are to be called when a specific message is sent or received.
	- type: array of objects.
	- acceptable children:
		- `function-to-call-on-success`:
			- the function to call when the message is sent or received successfully.
			- type: string.
			- is-required: true.
		- `data-must-equal`:
			- the data that must be received or sent in order for the success function to be called.
			- type: string.
		- `data-must-be-prefixed`:
			- the data must be prefixed with a string in order for the success function to be called.
			- type: string.
		- `data-can-be-anything`:
			- if this is true, then the success function will be called no matter what data is received or sent so long as all other conditions have not been met yet.
			- type: boolean.

## Special format for unconditional-sequence.

The string that is used in the `unconditional-sequence` property can include features that allow for more checking conditions and referencing abstract variables that the compiler for our backdoor knows how to get.

for example: `$(if ${use-shell-prompt} then use ${shell-prompt} otherwise use ${fallback-prompt})`
- opens with `$(`, this is to indicate we want to run a check.
	- this must be at the very start of the string and the closing parenthesis must be at the very end of the string.
- `if` is the keyword that indicates we want to run a check.
- `${use-shell-prompt}` is the variable that we want to check if is true.
	- this variable is defined in the `protocol.json` file.
- `then` is the keyword that indicates we want to do something if the check is confirmed to be true.
- `send` is the keyword that indicates we want to use a variable as this unconditional-sequence message.
- `${shell-prompt}` is the variable that we want to use as the message.
	- this variable is defined in the `protocol.json` file.
- `otherwise` is the keyword that indicates we want to do something if the check is confirmed to be false.
- `send` here is the use keyword again.
- `${fallback-prompt}` is the variable that we want to use as the message.
	- this variable is defined in the `protocol.json` file.

so the possible tokens are:
- `$(`
- `)`
- `if`
- `then`
- `otherwise`
- `send`
- `${`
- `}`
- `send`
- `end comms`:
	- if this token is used, then the sequence will end and the connection will continue according to `function-configurations`, if defined.
	- **ONLY AVAILABLE ON SERVER SIDE**.
- or:
- any variable to check or use, or;
- inside a check and using a string, this must be inside quotes, or;
- any string that is not a token.
