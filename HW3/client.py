import socket
import sys
import os


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 64000

server.connect((host, port))
serverFile = server.makefile("w", 0)

serverFile.writelines(["hello", "world", "hello"])

raw_input("press a key")
server.shutdown(socket.SHUT_WR)
server.close()


raw_input("press a key")

server2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 64000

server2.connect((host, port))

raw_input("Reconnected socket")

serverFile2 = server2.makefile("w", 0)
serverFile2.writelines(["hello", "world", "hello"])
server2.close()
