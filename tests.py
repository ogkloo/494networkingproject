from clientlib import Message

msg = Message('anonymous', 'example', 0, 0, 'some message here', 'localhost', 9999)
msg.assemble()
print(msg + '\n')

msg = Message('anonymous', 'example', 2, 1, 'some message here', 'localhost', 9999)
repr(msg.assemble())
print(msg)
