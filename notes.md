# === NOTES ===
## 19.11.21
Refactored code in server.py to be a bit nicer as an API. Will continue to
pursue this concept, but may have to do it twice because I forgot to push
things like an idiot. So I guess I'll have to do that tomorrow. Don't forget
to stash + backup so you can look at things separately.

#TODO:
* Keep refactored server design to only expose necessary API and move as much
of the backend as possible to the ChatState class.
* Stabilize both Server and Client APIs, then freeze them. Make backend changes
after that, but do not break the API.
* Potentially change message to use JSON.
* Switch server to ThreadedTCP server.
* Build in SSL support.

## 19.11.28
More progress! Setup VSCode. Very pleasurable editing experience actually.
Actual code changes are mostly getting pylint shut up.
Next thing should be to get the server to be able to send messages back to
the client.
Should follow:
- Figure out which channel the client wants (if blank, all)
- Figure out how many messages there are in that channel
- Send back the number of messages
- Send messages back 1 at a time
Remember to handle errors correctly!