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

    def from_packet(packet):
        msg = Message()
        msg.source = packet[0:21].decode('utf-8').strip('\0')
        msg.target = packet[21:41].decode('utf-8').strip('\0')
        msg.control_byte = packet[42]
        msg.msg_type = msg.control_byte & 0x0f
        msg.ephemeral = (msg.control_byte >> 4) & 0x01
        # This is done mostly to make the output pretty but is really rather irrelevant
        # Python needs some pushing to do this nicely
        msg.control_byte = (msg.ephemeral << 4 | msg.msg_type).to_bytes(1, 'little')
        msg.text = packet[42:].decode('utf-8')
        # These are irrelevant to do bookkeeping for
        msg.server = ''
        msg.port = 0
        return msg

    def __str__(self):
        return self.source + '->' + self.target + ':' + self.text + '\n' + str(self.msg_type) + ',' + str(self.ephemeral) + '->' + str(self.control_byte) + '\n' + self.server + ':' + str(self.port)

    def __repr__(self):
        return self.source + '->' + self.target + ':' + self.text + '\n' + str(self.msg_type) + ',' + str(self.ephemeral) + '->' + str(self.control_byte) + '\n' + self.server + ':' + str(self.port)

    def assemble(self):
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
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.server, self.port))
            client.sendall(self.assemble())
            response = client.recv(8)
            print(response.decode('utf-8'))
        except ConnectionRefusedError as err:
            print('Error: Connection refused. The server is not accepting requests at this time.')
        finally:
            client.close()
