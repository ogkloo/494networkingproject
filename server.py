import socketserver
from clientlib import Message

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

class Server():
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

    def __init__(self):
        '''
        Nicks that are registered for the server. May or may not be online.
        Online nicks will be added when the notion of session is supported.
        '''
        self.nicks = set()
        self.channels = {}

class HandleTCPServer(socketserver.BaseRequestHandler):
    def respond_to_message(self, packet):
        # Parse packet
        msg = Message.from_packet(packet)

    def respond(self, *packet):
        print('responding to packet')
        packet = packet[0]
        # Send message to channel request
        if int(packet[0]) == 0: 
            print(packet[1] + '\n' + packet[2])
            if irc_state.send_message(packet[1], packet[2]) == 0:
                self.request.sendall('message sent to newly created channel {}'.format(packet[1]).encode('utf-8'))
            else:
                self.request.sendall('message sent to {}'.format(packet[1]).encode('utf-8'))
        # Get messages from a channel
        elif int(packet[0]) == 1:
            message = ''
            try:
                for m in irc_state.channels[packet[1]]:
                    message += m + '\n'
                self.request.sendall(message.encode('utf-8'))
            except KeyError as err:
                self.request.sendall('Channel {} not found'.format(packet[1]).encode('utf-8'))
        # Send list of all nicks
        elif int(packet[0]) == 2:
            nicks = ''
            for nick in global_users:
                nicks += nick
            self.request.sendall(nicks.encode('utf-8'))
        else:
            print('no known handler, sending default response...')
            self.request.sendall('no known handler for this request'.encode('utf-8'))
                
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} sent: ".format(self.client_address[0]))
        data_vector = self.data.decode('utf-8').split(':')
        self.respond(data_vector)

if __name__ == '__main__':
    irc_state = Server()
    HOST, PORT = 'localhost', 9999
    tcp_server = socketserver.TCPServer((HOST, PORT), HandleTCPServer)
    tcp_server.serve_forever()
