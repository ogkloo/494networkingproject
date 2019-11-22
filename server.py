import socketserver, time
from message import Message

def now():
    return time.asctime(time.localtime(time.time()))

class Channel():
    def add_message(self, msg):
        self.messages.append(msg)

    def __init__(self, name, ephemeral):
        # Channel identifier
        self.name = name
        # Nicks listening for updates on this channel
        self.nicks = {}
        self.messages = []
        self.ephemeral = ephemeral
    
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
            self.channels[channel].nicks[nick] = now()
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
            self.channels[channel].add_message(msg)
            return True

    def get_messages(self, msg, request):
        raise NotImplementedError('failed: get_message unimplemented') 

    # Fail if user does not exist (ie is not in known nicks)
    def send_message_to_user(self, target, msg):
        if target not in self.nicks:
            return False
        elif target not in self.user_messages:
            self.user_messages[target] = []
        msg.time_stamp = now()
        self.user_messages[target].append(msg)
        self.nicks[msg.source] = msg.time_stamp
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
                msg.time_stamp = now()
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
                print('{} created channel #{} at {}'.format(msg.source, msg.target, now()))
                return True
            else:
                request.sendall((3).to_bytes(4, 'little'))
                print('{} failed to create channel #{}: Channel already exists'.format(msg.source, msg.target))
                return False
        # Create ephemeral channel. Fails if the channel exists.
        elif msg.msg_type == 3:
            if self.add_channel(msg.target, True):
                request.sendall((4099).to_bytes(4, 'little'))
                print('{} created ephemeral channel #{} at {}'.format(msg.source, msg.target, now()))
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
                print('Message was sent at {}'.format(now()))
                return True
            else:
                request.sendall((5).to_bytes(4, 'little'))
                print('Message failed: Sent to non-existent user at {}'.format(now()))
                return False
        elif msg.msg_type == 5:
            self.get_messages(msg, self.request)
        else:
            err = (0).to_bytes(1, 'little')
            self.request.sendall(err)

# To eventually be replaced by a threading version
class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(4096)
        msg = Message.from_packet(self.data)
        print("{}:{} sent: {}".format(self.client_address[0], self.client_address[1], str(msg)))
        self.server.responder.respond(msg, self.request)

class Server():
    def __init__(self, host, port):
        self.responder = ChatState()
        self.socket_server = socketserver.TCPServer((host, port), RequestHandler)
        self.socket_server.responder = self.responder

    def serve_forever(self):
        self.socket_server.serve_forever()
