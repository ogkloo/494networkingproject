import socketserver, sys, time
from message import Message

class Channel():
    def add_message(self, msg):
        self.messages.append(msg)

    def __init__(self, name):
        # Channel identifier
        self.name = name
        # Nicks listening for updates on this channel
        self.nicks = set()
        self.messages = []
    
class Server():
    '''
    Overall state of the server at a given time.
    '''
    def join_nick_to_channel(self, nick, channel):
        if channel in self.channels:
            self.channels[channel].nicks.add(nick)
            return True
        else:
            return False

    def __init__(self):
        self.channels = {'idle': Channel('idle')}
        self.nicks = set()

    def add_channel(self, name):
        if name not in self.channels:
            self.channels[name] = Channel(name)
            return True
        else:
            return False

    def send_message(self, channel, msg):
        if channel not in self.channels:
            return False
        else:
            self.channels[channel].add_message(msg)
            return True

    def respond(self, msg, request):
        # Join nick to a certain channel
        if msg.msg_type == 0:
            if self.join_nick_to_channel(msg.source, msg.target):
                request.sendall(0x00010000.to_bytes(4, 'little'))
                print('{} joined #{}'.format(msg.source, msg.target))
                return True
            else:
                request.sendall(0x00000001.to_bytes(4, 'little'))
                print('{} failed to join #{}: Channel does not exist'.format(msg.source, msg.target))
                return False
        # Create channel -- "Fails" if the channel already exists
        elif msg.msg_type == 1:
            if self.add_channel(msg.target):
                request.sendall(0x00010001.to_bytes(4, 'little'))
                localtime = time.asctime(time.localtime(time.time()))
                print('{} created channel #{} at {}'.format(msg.source, msg.target, localtime))
                return True
            else:
                request.sendall(0x00000002.to_bytes(4, 'little'))
                print('{} failed to create channel #{}: Channel already exists'.format(msg.source, msg.target))
                return False
        elif msg.msgtype == 2:
            pass
        else:
            err = (0).to_bytes(0, 'little')
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
