# Packet specification
A packet will consist of the following elements:
## Section 1: The header
The packet header include meta information about a message.
The first 20 bytes are reserved for the sender's nick. The next 20 bytes are 
reserved for the name of the target (without # prefixed to it). The next byte
is a control byte. Both the first 2 sections are encoded using utf-8.

## Section 2: Control byte values
0: The target in this packet is a channel.

1: The target in this packet is a nick.

## Section 3: The message
The message may be up to 4000 bytes. Messages are encoded and decoded using
utf-8.

## Note: Why are all these values so large?
These are specifically chosen to be large values to accomodate both long nicks, 
messages, channel names, etc, as well as provide easy support for utf-8. This is
important to supporting multilingual text.
