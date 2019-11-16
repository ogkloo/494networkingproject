# Packet specification
A packet will consist of the following elements:

## Section 1: The header
The packet header include meta information about a message.
The first 20 bytes are reserved for the sender's nick. The next 20 bytes are 
reserved for the name of the target (without # prefixed to it). The next byte
is a control byte. Both the first 2 sections are encoded using utf-8.

## Section 2: Control byte values
```
1 2 3 4      | 5           | 6            | 7 8
Message type   Target type   Ephemerality   Reserved
```
### Bits 1 through 4: Message type
Describes the message type. This will be used directly by the server.

### Bit 5: Target type
Describes the target type. If 0, the target is a channel. If 1, the target
is a nick, and this is a private message.

### Bit 6: Ephemerality
A toggle for ephemerality. If this bit is set, the server should omit this
message from logs. When two users open an ephermal chat, this bit should be
set on all messages between them.

## Section 3: The message
The message may be up to 4000 bytes. Messages are encoded and decoded using
utf-8.

## Note: Why are all these values so large?
These are specifically chosen to be large values to accomodate both long nicks, 
messages, channel names, etc, as well as provide easy support for utf-8. This is
important to supporting multilingual text.

# Responses
Reponses should be kept small. The client will accept 8 bytes of response. It
will be the response of the client to figure out what the response means based
on further specification in this document.
