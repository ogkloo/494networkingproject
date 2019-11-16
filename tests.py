'''
Test scripts go here!
Making other test scripts is fine, but please call them from here so that this runs
all tests that can be run quickly.
'''

from clientlib import Message

msg = Message('anonymous', 'example', 0, 0, 'some message here', 'localhost', 9999)
print(msg.assemble())
print(msg)

msg1 = Message('anonymous', 'example', 2, 1, 'some message here', 'localhost', 9999)
print(msg1.assemble())
print(msg1)

print(Message.from_packet(msg.assemble()))
print(Message.from_packet(msg1.assemble()))
