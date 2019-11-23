from server import Server
import sys

if __name__ == '__main__':
    chat_server = Server(sys.argv[1], int(sys.argv[2]))
    chat_server.serve_forever()
