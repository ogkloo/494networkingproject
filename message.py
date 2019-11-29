import socket
from datetime import datetime

def utf8len(s):
    return len(s.encode('utf-8'))

def from_packet(packet):
    '''
    Takes a packet, returns a message, without the server and port (those are 
    not included in the packet header for our protocol).     
    '''
    msg = Message()
    msg.source = packet[0:21].decode('utf-8').strip('\0')
    msg.target = packet[21:41].decode('utf-8').strip('\0')
    msg.control_byte = packet[42]
    msg.msg_type = msg.control_byte & 0x0f
    msg.ephemeral = (msg.control_byte >> 4) & 0x01
    msg.control_byte = (msg.ephemeral << 4 | msg.msg_type).to_bytes(1, 'little')
    msg.text = packet[43:].decode('utf-8')
    msg.server = ''
    msg.port = 0
    return msg

class Message():
    def __init__(self, source='', target='', msg_type=1, ephemeral=False, text='', server='', port=0):
        self.source = source
        self.target = target
        self.msg_type = msg_type
        self.ephemeral = ephemeral
        self.text = text
        self.server = server
        self.port = port
        self.time_stamp = datetime.now()
        self.control_byte = (self.ephemeral << 4 | self.msg_type).to_bytes(1, 'little')

    def __eq__(self, msg):
        '''
        Important note: This does not compare target server and port, as those 
        are not preserved in the packet.
        '''
        routing = self.source == msg.source and self.target == msg.target
        control = self.msg_type == msg.msg_type and self.ephemeral == msg.ephemeral
        text = self.text == msg.text
        return routing and control and text


    def __str__(self):
        return self.source + '>' + self.target + ':' + self.text + '/' + str(self.msg_type) + ',' + str(self.ephemeral) + '|' + str(self.control_byte) + '/' + self.server + ':' + str(self.port)

    def __repr__(self):
        return self.source + '->' + self.target + ':' + self.text + '\n' + str(self.msg_type) + ',' + str(self.ephemeral) + '->' + str(self.control_byte) + '\n' + self.server + ':' + str(self.port)

    def assemble(self):
        '''
        Assembles a packet from the Message object. Enforces maximum sizes.
        '''
        if utf8len(self.source) < 21:
            byte_length = 21 - utf8len(self.source) 
            source = self.source.encode('utf-8')
            for _ in range(0, byte_length):
                source += b'\0'
        else:
            raise RuntimeError('Nick too long')
        if utf8len(self.target) < 21:
            byte_length = 21 - utf8len(self.target) 
            target = self.target.encode('utf-8')
            for _ in range(0, byte_length):
                target += b'\0'
        else:
            raise RuntimeError('Target nick or channel name too long')
        if utf8len(self.text) < 4000:
            return source + target + self.control_byte + self.text.encode('utf-8')
        else:
            raise RuntimeError('Message too long. Reduce to under 4000 characters.')

    def send(self):
        '''
        Client-side message sending. Handles all the socket heavy lifting.
        Blocks. Can potentially hang for some time if a large number of 
        messages are retrieved.
        Throws ConnectionRefusedError if server fails to connect. It is up to
        clients to handle this error, as many responses are possible.
        '''
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.server, self.port))
            client.sendall(self.assemble())
            # If request is for get_messages, handle in a special way
            # Warning: Can block for a potentially long time.
            if self.msg_type == 5:
                num_messages = int.from_bytes(client.recv(8), byteorder='little')
                response = []
                for _ in range(1, num_messages):
                    response.append(from_packet(client.recv(4096)))
            else:
                response = client.recv(8)
            return response
        finally:
            client.close()
