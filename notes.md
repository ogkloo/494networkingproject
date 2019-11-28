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
