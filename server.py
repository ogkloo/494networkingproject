import socketserver
from datetime import datetime

from message import Message, from_packet


class Channel():
    def __init__(self, name, ephemeral):
        # Channel identifier
        self.name = name
        # Nicks listening for updates on this channel
        self.nicks = {}
        self.messages = {}
        self.ephemeral = ephemeral

    def __str__(self):
        return self.name + ',' + str(self.ephemeral) + ',' + str(self.nicks) + ',' + str(self.messages)
    
    def add_message(self, msg):
        self.messages[msg.time_stamp] = msg

    # Have never checked for updates here before
    def join(self, nick):
        self.nicks[nick] = None

class ChatState():
    '''
    Overall state of the server at a given time. Includes a global store of
    nicks that have been used before, all channels on the server, and a store
    of private messsages between users.

    By default, this server creates a non-ephemeral channel called #idle for
    convenience.
    '''
    def __init__(self):
        # Channels on the server
        self.channels = {'idle': Channel('idle', False)}
        # Map of nicks to messages waiting for that user.
        self.user_messages = {}
        # Map of nicks to the last time they sent a get_messages request
        self.nicks = {}

    def dump_channels(self):
        '''
        Debug function that dumps the entire list of channels.
        '''
        for (_, info) in self.channels.items():
            print(info)
    
    def get_channels(self, msg, request):
        # Fail validity check if user has never logged in
        if msg.source not in self.nicks:
            request.sendall((6).to_bytes(4, 'little'))
            return False
        else:
            # Succeed otherwise
            request.sendall((4101).to_bytes(4, 'little'))

            # Send back number of channels to listen for
            num_channels = len(self.channels)
            request.sendall(num_channels.to_bytes(8, byteorder='little'))

            for name in sorted(self.channels.keys()):
                request.sendall(name.encode('utf-8'))
                if int.from_bytes(request.recv(1), byteorder='little') != 1:
                    break
            return True

    def get_nicks(self, msg, request):
        # Fail validity check if user has never logged in
        if msg.source not in self.nicks:
            request.sendall((7).to_bytes(4, 'little'))
            return False
        else:
            # Succeed otherwise
            request.sendall((4102).to_bytes(4, 'little'))

            # Send back number of channels to listen for
            num_nicks = len(self.nicks)
            request.sendall(num_nicks.to_bytes(8, byteorder='little'))

            for (name, _) in sorted(self.nicks.items()):
                request.sendall(name.encode('utf-8'))
                if int.from_bytes(request.recv(1), byteorder='little') != 1:
                    break
            return True

    def join_channel(self, nick, channel):
        '''
        Add user to global nicklist, as well as to the channel requested.
        If the channel is invalid, they are added to the global nicklist
        only.

        A nick cannot deregister from the global list of nicks- those are
        all nicks that have ever logged on.
        '''
        if nick not in self.nicks:
            self.nicks[nick] = None
        if channel in self.channels:
            self.channels[channel].join(nick)
            return True
        else:
            return False
    
    def leave_channel(self, msg):
        '''
        Leaves/"parts" a channel. If the channel was ephemeral and no longer 
        has anyone in it after the nick leaves, delete the channel. Otherwise,
        leave it up.
        '''
        if msg.source in self.channels[msg.target].nicks:
            channel = self.channels[msg.target]
            del channel.nicks[msg.source]
            if channel.ephemeral and len(channel.nicks) == 0:
                del self.channels[msg.target]
            return True
        else:
            return False

    def add_channel(self, name, ephemeral):
        '''
        Adds a channel to the list of channels. Does not join a user to it,
        the client should send a second message to accomplish that.
        '''
        if name not in self.channels:
            self.channels[name] = Channel(name, ephemeral)
            return True
        else:
            return False

    def send_message(self, msg):
        '''
        Send message to the requested channel. If nick is not in the channel,
        do not send the message.
        '''
        channel = self.channels[msg.target]
        if msg.target not in self.channels or msg.source not in channel.nicks:
            return False
        else:
            msg.time_stamp = datetime.utcnow()
            self.channels[msg.target].add_message(msg)
            return True

    def get_messages(self, msg, request):
        '''
        Get messages for a specific user, for a specific channel.
        Uses the msg object passed in to do this.

        Returns False if the user has never logged into that channel before.
        If channel is blank, should get private messages to that user.
        '''
        # If the user has never logged in before, fail.
        if msg.source not in self.nicks:
            return False
        # We do not need to send requests after this, as this message will send
        # the request.
        else:
            if self.nicks[msg.source] is None:
                request_time = datetime.min
            else:
                request_time = self.nicks[msg.source]
            self.nicks[msg.source] = datetime.utcnow()
            channel = msg.target
            try:
                if channel == '' and msg.text != 'ALL':
                    messages = dict((k,v) for k,v in self.user_messages[msg.source].items() if k >= request_time)
                elif channel == '' and msg.text == 'ALL':
                    messages = self.user_messages[msg.source]
                elif channel != '' and msg.text == 'ALL':
                    messages = self.channels[channel].messages
                else:
                    messages = dict((k,v) for k,v in self.channels[channel].messages.items() if k >= request_time)
                request.sendall((4099).to_bytes(4, 'little'))
            except KeyError:
                request.sendall((4).to_bytes(4, 'little'))
                return False
            # Need to standardize on a small set of error codes + success codes
            # Send back the number of messages
            request.sendall(len(messages).to_bytes(8, byteorder='little'))

            for (_, message) in sorted(messages.items()):
                request.sendall(message.assemble())
                # Wait for ACK from client, if it fails and/or we get something
                # unexpected back, we should stop sending messages immediately.
                if int.from_bytes(request.recv(1), byteorder='little') != 1:
                    break
            return True

    def send_message_to_user(self, msg):
        '''
        Sends a private message to a nick.
        
        Fails if the nick doesn't exist.
        '''
        if msg.target not in self.nicks:
            return False
        elif msg.target not in self.user_messages:
            self.user_messages[msg.target] = {}
        msg.time_stamp = datetime.utcnow()
        self.user_messages[msg.target][msg.time_stamp] = msg
        return True

    def respond(self, msg, request):
        # Join nick to a certain channel
        if msg.msg_type == 0:
            if self.join_channel(msg.source, msg.target):
                # Send response code 4096: Join channel successful 
                request.sendall((4096).to_bytes(4, 'little'))
                print('{} joined #{}'.format(msg.source, msg.target))
                return True
            else:
                request.sendall((1).to_bytes(4, 'little'))
                print('{} failed to join #{}: Channel does not exist'.format(msg.source, msg.target))
                return False
        # Send message to channel. Fails if channel does not exist.
        elif msg.msg_type == 1:
            if self.send_message(msg):
                # Send response code 4097: Message send successful 
                request.sendall((4097).to_bytes(4, 'little'))
                print('<{}> {} sent to #{}: {}'.format(msg.time_stamp, msg.source, msg.target, msg.text))
                return True
            else:
                request.sendall((2).to_bytes(4, 'little'))
                print('{} failed to create channel #{}: Channel already exists'.format(msg.source, msg.target))
                return False
        # Create channel. Fails if the channel already exists
        elif msg.msg_type == 2:
            if self.add_channel(msg.target, False):
                # Send response code 4098: Create channel successful 
                request.sendall((4098).to_bytes(4, 'little'))
                print('{} created channel #{} at {}'.format(msg.source, msg.target, datetime.utcnow()))
                return True
            else:
                request.sendall((3).to_bytes(4, 'little'))
                print('{} failed to create channel #{}: Channel already exists'.format(msg.source, msg.target))
                return False
        # Create ephemeral channel. Fails if the channel exists.
        elif msg.msg_type == 3:
            if self.add_channel(msg.target, True):
                request.sendall((4099).to_bytes(4, 'little'))
                print('{} created ephemeral channel #{} at {}'.format(msg.source, msg.target, datetime.utcnow()))
                return True
            else:
                request.sendall((4).to_bytes(4, 'little'))
                print('{} failed to create ephemeral channel #{}: Channel already exists'.format(msg.source, msg.target))
                return False
        # Send private messages among users
        elif msg.msg_type == 4:
            print(self.nicks)
            if self.send_message_to_user(msg):
                request.sendall((4100).to_bytes(4, 'little'))
                print('Message was sent at {}'.format(datetime.utcnow()))
                return True
            else:
                request.sendall((5).to_bytes(4, 'little'))
                print('Message failed: Sent to non-existent user at {}'.format(datetime.utcnow()))
                return False
        # Get messages from a specific channel
        elif msg.msg_type == 5:
            self.get_messages(msg, request)
            print('Sent back messages at {} '.format(datetime.utcnow()))
        # List channels
        elif msg.msg_type == 12:
            if self.get_channels(msg, request):
                print('User {} requested channel list at {}'.format(msg.source, datetime.utcnow()))
            else:
                print('Failed request for channel listing at {}'.format(datetime.utcnow()))
        elif msg.msg_type == 13:
            if self.get_nicks(msg, request):
                print('User {} requested nick list at {}'.format(msg.source, datetime.utcnow()))
            else:
                print('Failed request for nick listing at {}'.format(datetime.utcnow()))
        # Leave a channel
        elif msg.msg_type == 15:
            if self.leave_channel(msg):
                request.sendall((4100).to_bytes(4, 'little'))
                print('User {} left #{}'.format(msg.source, msg.target))
            else:
                request.sendall((6).to_bytes(4, 'little'))
                print('User {} tried to leave #{}'.format(msg.source, msg.target))
        else:
            err = (0).to_bytes(1, 'little')
            request.sendall(err)

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(4096)
        msg = from_packet(self.data)
        print("{}:{} sent: {}".format(self.client_address[0], self.client_address[1], str(msg)))
        self.server.responder.respond(msg, self.request)

class Server():
    '''
    A chat server. Takes requests on a certain port and then handles them one by one.
    '''
    def __init__(self, host, port):
        self.responder = ChatState()
        self.socket_server = socketserver.ThreadingTCPServer((host, port), RequestHandler)
        self.socket_server.responder = self.responder

    def serve_forever(self):
        try:
            self.socket_server.serve_forever()
        except KeyboardInterrupt:
            self.socket_server.shutdown()
            self.socket_server.server_close()
