import socket

def utf8len(s):
    return len(s.encode('utf-8'))

class Message():
    def __init__(self, source='', target='', msg_type=1, ephemeral=1, text='', server='', port=0):
        self.source = source
        self.target = target
        self.msg_type = msg_type
        self.ephemeral = ephemeral
        self.text = text
        self.server = server
        self.port = port
        self.control_byte = (self.ephemeral << 4 | self.msg_type).to_bytes(1, 'little')

    def __eq__(self, msg):
        '''
        Important note: This does not compare target server and port, as those are not preserved in the packet.
        It would be pointless to keep track of for anything other than this, and so it was not included in this
        function. It might be worth changing this function? Not sure.
        '''
        metadata = self.source == msg.source and self.target == msg.target and self.msg_type == msg.msg_type and self.ephemeral == msg.ephemeral
        text = self.text == msg.text
        return metadata and text

    def from_packet(packet):
        '''
        Takes a packet, returns a message, without the server and port (those are not included in the packet
        header for our protocol). We *could* extract that information from the TCP header, but that doesn't
        seem particularly useful and I don't want to clutter the code with it.
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

    def __str__(self):
        return self.source + '>' + self.target + ':' + self.text + '/' + str(self.msg_type) + ',' + str(self.ephemeral) + '|' + str(self.control_byte) + '/' + self.server + ':' + str(self.port)

    def __repr__(self):
        return self.source + '->' + self.target + ':' + self.text + '\n' + str(self.msg_type) + ',' + str(self.ephemeral) + '->' + str(self.control_byte) + '\n' + self.server + ':' + str(self.port)

    def assemble(self):
        '''
        Assembles a packet from the Message object.
        '''
        if utf8len(self.source) < 21:
            byte_length = 21 - utf8len(self.source) 
            source = self.source.encode('utf-8')
            for b in range(0, byte_length):
                source += b'\0'
        else:
            raise RuntimeError('Nick too long')
        if utf8len(self.target) < 21:
            byte_length = 21 - utf8len(self.target) 
            target = self.target.encode('utf-8')
            for b in range(0, byte_length):
                target += b'\0'
        else:
            raise RuntimeError('Target nick or channel name too long')
        if utf8len(self.text) < 4000:
            return source + target + self.control_byte + self.text.encode('utf-8')
        else:
            raise RuntimeError('Message too long. Reduce to under 4000 characters.')


    def send(self):
        '''
        Client-side message sending. Handles all the socket heavy lifting. Intended to be a VERY simple API.
        This actually also enables bots to be built pretty easily I think, which is kinda cool.
        '''
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.server, self.port))
            client.sendall(self.assemble())
            response = client.recv(8)
            print(int.from_bytes(response, byteorder='little'))
        except ConnectionRefusedError as err:
            print('Error: Connection refused.')
        finally:
            client.close()
