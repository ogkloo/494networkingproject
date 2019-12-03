import sys, getopt
from message import Message

def main():
    try:
        opts, _ = getopt.getopt(sys.argv[1:], 's:p:n:c:m:t:e', ['server=', 'port=', 'nick=', 'channel=', 'msg=', 'type=', 'ephemeral'])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    server = 'localhost'
    port = 9999
    nick = 'anonymous'
    channel = 'idle'
    msg = ''
    msg_type = 1
    ephemeral = False

    for o, a in opts:
        if o in ('-s', '--server'):
            server = a
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-n', '--nick'):
            nick = a
        elif o in ('-c', '--channel'):
            channel = a
        elif o in ('-m', '--message'):
            msg = a
        elif o in ('-t', '--type'):
            msg_type = int(a)
        elif o in ('-e', '--ephemeral'):
            ephemeral = 1
        else:
            """ 
            Is it a better solution to throw an expection?
            """
            assert False, 'invalid option {}'.format(o)

    # Use message API to send, handle errors in the process
    data = Message(nick, channel, msg_type, ephemeral, msg, server, port)
    try:
        response = data.send()
    except ConnectionRefusedError:
        print('Connection failed: Connection refused.')
        sys.exit(2)

    if msg_type == 5:
        for message in response:
            print(message)
    else:
        print(int.from_bytes(response, byteorder='little'))

if __name__ == '__main__':
    main()
