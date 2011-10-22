import socket
import sys
import os
import traceback




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 64000

server.bind(("", port))
server.listen(10)

conn = ""
try:
	while True:

			(conn, addy) = server.accept()
			print "found client at: " + str(addy)


			client = conn.makefile('r', 0)
			#line = conn.recv(100)
			print "made file"

			
			lines = client.readlines()

			print lines
			raw_input()

			print "End loop"
except Exception as e:
	print e
	traceback.print_exc(file = sys.stdout)
	raw_input("Fuck")
finally:
	if conn != "":
		conn.close()
	server.close()