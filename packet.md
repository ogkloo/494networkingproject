# Packet specification

A packet will consist of the following elements:

## Section 1: The header

The packet header include meta information about a message.
The first 20 bytes are reserved for the sender's nick. The next 20 bytes are
reserved for the name of the target (without # prefixed to it). The next byte
is a control byte. Both the first 2 sections are encoded using utf-8.

## Section 2: Control byte values

```none
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

## Message types

### 0 / Join channel

Adds nick to the list of listening nicks for a certain channel. This means the
client is "logged in".

### 1 / Send message to channel

Sends a message to a certain channel. These messages ignore ephemeral settings,
although the server will inform the client in the response code if the channel
is considered ephemeral.

### 2 / Create channel

Creates a public, non-ephemeral channel.

### 3 / Create ephemeral channel

Creates a "private" chat. Technically, anyone can join, but it will not be
included in list requests (see type 12) and the channel will be deleted when
all users in the channel sign off.

### 4 / Send message to user

Specifies that the target field of the message is a user and not a channel.
The server should deliver the message to only the specified user. This message
type respects the ephemeral field.

### 5 / Get messages

Get all messages from the last time the user checked. If the text field includes
a string of the form "Tue May 08 15:14:45 +0800 2012", it should be interpreted
as the time to get messages from. This allows a user to request the history of
a channel, even if they just joined, which facilitates usage across multiple
devices.

## 12 / List channels

Lists all public channels on the server. Should not list ephemeral channels
(see message type 3). This response may be very large.

## 13 / List users

Lists all users who are currently joined to at least one channel.

## 15 / Part

The target field of a message should be interpreted as the channel to remove
the source user from.

## Responses

Reponses should be kept small. The client will accept 8 bytes of response. It
will be the response of the client to figure out what the response means based
on further specification in this document.

### Introduction

Responses are 32 bits in length, with a few exceptions. For the most part,
responses communicate simple success or failure for some specific action.
All responses are sent little endian.

#### `0x00000000` - `0x0000ffff`: Errors

* 0: Unidentified failure
* 1: Failure to join channel, channel does not exist.
* 2: Failed to send message, channel does not exist.
* 3: Failed to create channel, channel already exists.
* 4: Failed to send messages back, channel does not exist.
* 5: Failed to part channel

#### `0x00010000` - `0xffffffff`: Successes and other responses

* 4096: Join channel successful
* 4097: Send message successful
* 4098: Create channel successful
* 4099: Messages to follow
* 4100: Channel successfully parted

#### Messages

Getting messages follows a format:
The first thing that happens is a check for validity. This ensures that a
request is not made to a channel that does not exist. If this happens, the
server will return 4 to the client as in accordance with the error codes. If
the channel is valid, the server will return 4099 Messages to Follow.

If the channel is blank, this is to be interpreted as getting the user's
private messages.

After the server is sure that the channel requested exists, the next thing is
returning to the client how many messages to wait for.

Only new messages are sent. New messages are defined in 2 cases:

1. If the user has never sent a get messages request to the requested channel
before, "new" shall be interpreted as all messages to that channel since the
beginning of time.

2. If the user has sent a message to the requested channel before, new shall be
interpreted as all messages since the last get messages request.

They are sent in chronological order, and after each message the server shall
wait for an ACK. The ACK is the number 1. This is to ensure that neither gets
out of sync and runs into each other.
