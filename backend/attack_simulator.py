import socket

target = "127.0.0.1"
port = 80

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(5000):
    sock.sendto(b"attack", (target, port))