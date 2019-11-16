import sys, getopt
from clientlib import Message

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:p:n:c:m:t:e', ['server=', 'port=', 'nick=', 'channel=', 'msg=', 'type=', 'ephemeral'])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    server = 'localhost'
    port = 9999
    nick = 'anonymous'
    channel = 'idle'
    msg = 'test message'
    msg_type = 1
    ephemeral = 0

    for o, a in opts:
        if o in ('-s', '--server'):
            server = a
        elif o in ('-p', '--port'):
            port = p
        elif o in ('-n', '--nick'):
            nick = a
        elif o in ('-c', '--channel'):
            channel = a
        elif o in ('-m', '--message'):
            msg = a
            msg_type = 0
        elif o in ('-t', '--type'):
            msg_type = a
        elif o in ('-e', '--ephemeral'):
            ephemeral = 1
        else:
            assert False, 'invalid option {}'.format(o)

    data = Message(nick, channel, msg_type, ephemeral, msg, server, port)
    data.send()

if __name__ == '__main__':
    main()
