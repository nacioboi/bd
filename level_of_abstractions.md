# Level of abstractions

We do not want the notabackdoorbuilder to be just for backdoors.

Somehow we need a way to export the functionality of building compatible server and client scripts to other projects.

This means the schema for the protocol needs to be defined in a way that is not specific to the notabackdoorbuilder.

## Protocol as of current

The protocol is defined in the [making_a_protocol.md](making_a_protocol.md) file.

## Protocol as of future

There will still be three sub-protocols:
- handshake;
- fallback; and,
- normal.

### Normal sub-protocol Design for the Future

#### `function-configurations`:

- `after-receive`
- `before-send`