import socketserver

class HandleTCPServer(socketserver.BaseRequestHandler):
    def respond(self, *packet):
        print('responding to packet')
        packet = packet[0]
        # Send message to channel request
        if int(packet[0]) == 0: 
            if packet[1] in channels:
                channels[packet[1]].append(packet[2])
                self.request.sendall('message sent successfully to {}'.format(packet[1]).encode())
                print(channels)
                print('sent ack')
            else:
                channels[packet[1]] = [packet[2]]
                self.request.sendall('message sent successfully to newly created channel {}'.format(packet[1]).encode())
                print(channels)
                print('sent ack')
        # Get messages from a channel
        elif int(packet[0]) == 1:
            message = ''
            for m in channels[packet[1]]:
                message += m + '\n'
            self.request.sendall(message.encode())
        else:
            print('no known handler, sending default response...')
            self.request.sendall('no known handler for this request'.encode())
                
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} sent: ".format(self.client_address[0]))
        print(self.data.decode('UTF-8'))
        data_vector = self.data.decode('UTF-8').split(':')
        print(data_vector)
        self.respond(data_vector)

if __name__ == '__main__':
    channels = {}
    HOST, PORT = 'localhost', 9999
    tcp_server = socketserver.TCPServer((HOST, PORT), HandleTCPServer)
    tcp_server.serve_forever()
