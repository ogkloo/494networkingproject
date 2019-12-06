import sys, getopt
from message import Message

def main():
    '''
    Parse the command line arguments
    '''
    try:
        opts, _ = getopt.getopt(sys.argv[1:], 's:p:n:c:m:t:eh', ['server=', 'port=', 'nick=', 'channel=', 'msg=', 'type=', 'ephemeral', 'help'])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    '''The name of server or the IP number of the server'''
    server = 'localhost'
    '''Port number of server'''
    port = 9999
    '''User's nick name'''
    nick = 'anonymous'
    '''Name of channel'''
    channel = 'idle'
    '''Content of message'''
    msg = ''
    '''0 join channel, 1 send message to channel, 2 create channel, 3 private channel 4 private message 
    5 get information, 12 list channel, 13 get all users at that channel,  15 leave a channel
    '''
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
        elif o in ('-h', '--help'):
            print('Help: lhsmclient')
            print('-s | --server: Which server to send the message to. Defaults to localhost.')
            print('-p | --port: Port the server is running on. Defaults to 9999.')
            print('-n | --nick: Nick to send message from. Defaults to "anonymous".')
            print('-c | --channel: Specify a channel. Defaults to #idle.')
            print('-m | --message: Specify the content of the message. The default content is blank.')
            print('-t | --type: Specify the message type (See RFC).')
            print('-e | --ephemeral: Set ephemeral flag for servers that implement ephemeral messaging.')
            return 1
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

    if msg_type == 5 or msg_type == 12 or msg_type == 13:
        for message in response:
            print(message)
    else:
        print(int.from_bytes(response, byteorder='little'))

if __name__ == '__main__':
    main()
