'''
Test scripts go here!
Making other test scripts is fine, but please call them from here so that this runs
all tests that can be run quickly.
'''

from message import Message, from_packet
from datetime import datetime
from server import Channel, ChatState, Server
from os import fork, waitpid, kill
from time import sleep
import signal
import sys

def format_test(name, assertion):
    try:
        assert(assertion)
    except AssertionError:
        print('FAILED: ' + name)
    else:
        print('passed: ' + name) 

msg = Message('anonymous', 'example', 2, False, 'some message here', 'localhost', 9999)
msg.time_stamp = datetime.now()

print('# Assembly to packet from Message object')
format_test('Message assembly', (msg.assemble() == b'anonymous\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00example\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02some message here'))
format_test('Message reassembly', (from_packet(msg.assemble()) == msg))

channel = Channel('idle', False)
channel.join(msg.source)
channel.add_message(msg)

print('# ChatState tests')
test_server = ChatState()
format_test('Join extant channel', (test_server.join_channel('test_user', 'idle') == True))
format_test('Prevent creating channels implicitly', (test_server.join_channel('test_user', 'rice') == False))
format_test('Create channel', (test_server.add_channel('test_channel', False) == True))
format_test('Join new channel', test_server.join_channel('anon', 'test_channel') == True)

print('# Live server and client tests')
try:
    port = int(sys.argv[1])
except IndexError:
    port = 9999

try:
    pid = fork()
except OSError as err:
    print('Fork failed: {}'.format(err))

if pid == 0:
    server = Server('localhost', port)
    sys.stdout = open('/dev/null', 'w')
    server.serve_forever()
else:
    default_msg = Message('anon', 'example', 2, False, 'Server default test message', 'localhost', port)
    sleep(0.1)
    try:
        response = int.from_bytes(default_msg.send(), byteorder='little')
        kill(pid, signal.SIGTERM)
        format_test('Server default message test', response == 4098)
    except ConnectionRefusedError:
        print('Failed: Server failed to start')
        sys.exit(2)
