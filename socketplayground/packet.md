# Packet specification
A packet will consist of the following elements:
## Section 1: The header
The packet header include meta information about a message.
The first 20 bytes are reserved for the sender's nick. The next 20 bytes are 
reserved for the name of the target (without # prefixed to it). The next byte
is a control byte.
## Section 2: Control byte values
0: The target in this packet is a channel.

1: The target in this packet is a nick.
