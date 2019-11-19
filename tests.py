'''
Test scripts go here!
Making other test scripts is fine, but please call them from here so that this runs
all tests that can be run quickly.
'''

from message import Message

# Message tests
msg = Message('anonymous', 'example', 2, 1, 'some message here', 'localhost', 9999)

# Assembly to packet from Message object
try:
    assert(msg.assemble() == b'anonymous\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00example\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12some message here')
except AssertionError as err:
    print('Message assembly test... failed.')
else:
    print('Message assembly test... passed.')

# Reassembly to Message object from packet
try:
    assert(Message.from_packet(msg.assemble()) == msg)
except AssertionError as err:
    print('Message reassembly test... failed.')
else:
    print('Message reassembly test... passed.')
