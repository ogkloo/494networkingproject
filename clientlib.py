import socket

def utf8len(s):
    return len(s.encode('utf-8'))

class Message():
    def __init__(self, source, target, msg_type, ephemeral, text, server, port):
        self.source = source
        self.target = target
        self.msg_type = msg_type
        self.ephemeral = ephemeral
        self.text = text
        self.server = server
        self.port = port
        self.control_byte = (self.ephemeral << 4 | self.msg_type).to_bytes(1, 'little')

    def __str__(self):
        return self.source + '->' + self.target + ':' + self.text + '\n' + str(self.msg_type) + ',' + str(self.ephemeral) + '->' + str(self.control_byte) + '\n' + self.server + ':' + str(self.port)

    def assemble(self):
        if utf8len(self.source) < 21 and utf8len(self.target) < 21 and utf8len(self.text) < 4000:
            return self.source.encode('utf-8') + self.target.encode('utf-8') + self.control_byte + self.text.encode('utf-8')

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
