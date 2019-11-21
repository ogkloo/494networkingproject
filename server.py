import socketserver, sys, time
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
    
class Server():
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

    # Cannot fail
    def send_message_to_user(target, msg):
        if target not in self.user_messages:
            self.user_messages[target] = []
        msg.time_stamp = now()
        self.user_messages[target].append(msg)
        self.nicks[msg.source] = msg.time_stamp

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
            if self.add_channel(msg.target):
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
            if self.send_message_to_user(msg.target, msg):
                pass
        else:
            err = (0).to_bytes(1, 'little')
            self.request.sendall(err)

class RequestHandler(socketserver.BaseRequestHandler):
    '''
    Redirects a request to a specified server.
    '''
    def handle(self):
        self.data = self.request.recv(4096)
        msg = Message.from_packet(self.data)
        print("{}:{} sent: {}".format(self.client_address[0], self.client_address[1], str(msg)))
        server.respond(msg, self.request)

if __name__ == '__main__':
    server = Server()
    host, port = sys.argv[1], int(sys.argv[2])
    socket_server = socketserver.TCPServer((host, port), RequestHandler)
    socket_server.serve_forever()
