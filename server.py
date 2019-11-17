import socketserver, sys
from message import Message

# TODO: Redo this to work with the Message class instead of directly reading packets.
# Also, we should read packets correctly, as they're no longer formed randomly and
# badly.

class Channel():
    def add_message(self, msg):
        self.messages.append(msg)

    def __init__(self, name):
        # Channel identifier
        self.name = name
        # Nicks listening for updates on this channel
        self.nicks = set()
        self.messages = []

class Server(socketserver.BaseRequestHandler):
    def __init__(self, host, port):
        '''
        Nicks that are registered for the server. May or may not be online.
        Online nicks will be added when the notion of session is supported.
        '''
        self.nicks = set()
        self.channels = {}

    def add_channel(self, channel):
        if channel not in self.channels:
            self.channels[channel.name] = channel
            return 0
        else:
            return 1

    def send_message(self, channel, msg):
        if channel not in self.channels:
            self.add_channel(Channel(channel))
            self.channels[channel].add_message(msg)
            return 0
        else:
            self.channels[channel].add_message(msg)
            return 1

    def respond(self, msg):
        if msg.msg_type == 0:
            pass
        elif msg.msg_type == 1:
            pass
        elif msg.msgtype == 2:
            pass
        else:
            err = (0).to_bytes(1, 'little')
            self.request.sendall(err)

    def handle(self):
        self.data = self.request.recv(4096)
        print("{} sent: ".format(self.client_address[0]))
        msg = Message.from_packet(self.data.decode('utf-8'))

if __name__ == '__main__':
    host, port = sys.argv[1], int(sys.argv[2])
    server = socketserver.TCPServer((host, port), Server)
    server.serve_forever()
