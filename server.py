import socketserver, time
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
    Overall state of the server at a given time.
    '''
    def __init__(self):
        # Channels on the server
        self.channels = {'idle': Channel('idle', False)}
        # Map of nicks to messages waiting for that user.
        self.user_messages = {}
        # Map of nicks to the last time they sent a get_messages request
        self.nicks = {}

    def dump_channels(self):
        for (_, info) in self.channels.items():
            print(info)

    def join_channel(self, nick, channel):
        '''
        We must add to the nicks list, but we don't want to send all messages
        yet. Or maybe we do? Joining a channel probably shouldn't pull down
        the entire message history, but instead allow the client the option
        of doing this by issuing a get messages request.
        '''
        if nick not in self.nicks:
            self.nicks[nick] = None
        if channel in self.channels:
            self.channels[channel].join(nick)
            return True
        else:
            return False

    def add_channel(self, name, ephemeral):
        if name not in self.channels:
            self.channels[name] = Channel(name, ephemeral)
            return True
        else:
            return False

    def send_message(self, channel, msg):
        if channel not in self.channels:
            return False
        else:
            msg.time_stamp = datetime.now()
            self.channels[channel].add_message(msg)
            return True

    # https://stackoverflow.com/questions/18807079/selecting-elements-of-a-python-dictionary-greater-than-a-certain-value
    # https://dateutil.readthedocs.io/en/stable/examples.html
    def get_messages(self, msg):
        # If the user has never logged in before, fail.
        if msg.source not in self.channels:
            return False
        # We do not need to send requests after this, as this message will send the request.
        else:
            self.nicks[msg.source] = datetime.now()
            # request_time = datetime.now()
            # old_messages = dict((k,v) for k,v in self.channels[msg.target].messages.items() if k > request_time)
            return True

    # Fail if user does not exist (ie is not in known nicks)
    def send_message_to_user(self, target, msg):
        if target not in self.nicks:
            return False
        elif target not in self.user_messages:
            self.user_messages[target] = []
        msg.time_stamp = datetime.now()
        self.user_messages[target].append(msg)
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
            if self.send_message(msg.target, msg):
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
                print('{} created channel #{} at {}'.format(msg.source, msg.target, datetime.now()))
                return True
            else:
                request.sendall((3).to_bytes(4, 'little'))
                print('{} failed to create channel #{}: Channel already exists'.format(msg.source, msg.target))
                return False
        # Create ephemeral channel. Fails if the channel exists.
        elif msg.msg_type == 3:
            if self.add_channel(msg.target, True):
                request.sendall((4099).to_bytes(4, 'little'))
                print('{} created ephemeral channel #{} at {}'.format(msg.source, msg.target, datetime.now()))
                return True
            else:
                request.sendall((4).to_bytes(4, 'little'))
                print('{} failed to create ephemeral channel #{}: Channel already exists'.format(msg.source, msg.target))
                return False
        # Send private messages among users
        elif msg.msg_type == 4:
            print(self.nicks)
            if self.send_message_to_user(msg.target, msg):
                request.sendall((4100).to_bytes(4, 'little'))
                print('Message was sent at {}'.format(datetime.now()))
                return True
            else:
                request.sendall((5).to_bytes(4, 'little'))
                print('Message failed: Sent to non-existent user at {}'.format(datetime.now()))
                return False
        elif msg.msg_type == 5:
            # self.get_messages(msg, self.request)
            pass
        else:
            err = (0).to_bytes(1, 'little')
            request.sendall(err)

# To eventually be replaced by a threading version
class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(4096)
        msg = from_packet(self.data)
        print("{}:{} sent: {}".format(self.client_address[0], self.client_address[1], str(msg)))
        self.server.responder.respond(msg, self.request)

class Server():
    def __init__(self, host, port):
        self.responder = ChatState()
        self.socket_server = socketserver.TCPServer((host, port), RequestHandler)
        self.socket_server.responder = self.responder

    def serve_forever(self):
        self.socket_server.serve_forever()
