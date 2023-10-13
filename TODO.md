# TODO

## Must - sorted by priority.

* [ ] finish socket wrapper tests.
* [ ] finish socket wrapper and rerun the tests, make sure they all pass.
* [ ] integrate socket wrapper into pty socket
* [ ] rename notabackdoorbuilder into yinyang. this is because it will assemble server and clients that work in harmony.
* [ ] make yinyang backdoor agnostic. meaning it can assemble for any number of applications, not just backdoors.
* [ ] rewrite the backdoor to use yinyang.

## Nice to have.

right now the api is looking like its going to be hard to use.
it would be nice to have a way to make it easier to use.
like, instead of having to reference the dict `context` all the time, it would be nice to have a way to make it so that the user can just reference the variables directly.