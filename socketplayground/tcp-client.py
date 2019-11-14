import sys, getopt, socket

# try:
#     opts, args = getopt.getopt(sys.argv[1:4], 's:p:', ['server=', 

host_ip, server_port = 'mechanicalgarden.online', 9001
data = sys.argv[1] + ':' + sys.argv[2] + ':' + sys.argv[3]

tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcp_client.connect((host_ip, server_port))
    tcp_client.sendall(data.encode())
    received = tcp_client.recv(1024)
finally:
    tcp_client.close()

print('bytes sent: {}'.format(data))
print('bytes received: {}'.format(received.decode()))
