import socket

def utf8len(s):
    return len(s.encode('utf-8'))

class Message():
    def __init__(self, source, target, msg_type, ephemeral, text):
        self.source = nick
        self.target = channel
        self.msg_type = msg_type
        self.ephemeral = ephemeral
        self.text = text

    def assemble(self):
        control_byte = 0 | self.ephemeral << 4 | self.msg_type
        if utf8len(self.source) < 21 and utf8len(self.target) < 21 and utf8len(self.text) < 4000:
            return source.encode('utf-8') + target.encode('utf-8') + control_byte.to_bytes(1, byteorder='little') + self.text.encode('utf-8')

    def send_message(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.server, self.port))
            client.sendall(self.assemble())
            response = client.recv(8)
        except ConnectionRefusedError as err:
            print('Error: Connection refused. The server is not accepting requests at this time.')
        finally:
            client.close()
