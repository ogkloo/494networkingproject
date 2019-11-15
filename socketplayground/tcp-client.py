import sys, getopt, socket
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:p:n:c:m:t:', ['server=', 'port=', 'nick=', 'channel=', 'msg=', 'type='])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    server = 'localhost'
    port = 9999
    nick = 'anonymous'
    channel = 'idle'
    msg = 'test message'
    msg_type = 1

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

    data = str(msg_type) + ':' + channel + ':' + msg

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((server, port))
        client.sendall(data.encode('utf-8'))
        received = client.recv(1024)
    finally:
        client.close()

    print(format(received.decode('utf-8')))

if __name__ == '__main__':
    main()
