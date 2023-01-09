# echo-client.py
import socket
import json

# #database prerequisites
# import sqlite3
# import os

HOSTS = ["192.168.176.108"]  # The agents's hostname or IP address
PORT = 8574  # The port used by the agents

#Generate payload data
data = {"TARGET": "192.168.176.105", "PORT": 443, "PROTOCOL": "TCP", "HITS": 100}
data = json.dumps(data)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    for HOST in HOSTS:
        s.connect((HOST, PORT))
        s.send(data.encode())
        data = s.recv(1024)
        

print(f"Received {data!r}")

