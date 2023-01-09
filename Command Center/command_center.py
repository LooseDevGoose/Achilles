# echo-client.py
import socket
import json

# #database prerequisites
# import sqlite3
# import os

class CommandCenter:

    def __init__(self, PORT=9191):
        #Default required Variables (CONSTANTS)
        self.HOST = socket.gethostname()
        self.PORT = PORT
        self.LOCAL_IP = socket.gethostbyname(self.HOST)

    def listen(self, MAX_CONNECTIONS=5):
        #Bind the socket to port -> SOCK_STREAM = tcp traffic
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Bind the sockets to the machine ip and 8574 port
        sock.bind((self.HOST, self.PORT))
        #Start listening on host and port, accepting a maximal of 50 connections in queue. New requests get denied. 
        sock.listen(MAX_CONNECTIONS)

        while True:
            #Using ASCII colors here for readability  \033[#m] is the escape format, the number is the color Yellow = 33 Green=32
            print(f"Command Center started listening on: \n\033[1;33mIP: \033[1;32m {self.LOCAL_IP}  \n\033[1;33mHostname: \033[1;32m{self.HOST.upper()}  \n\033[1;33mPort: \033[1;32m{self.PORT}")
            connection, addr = sock.accept()

            #Decode command center's JSON data and assign to variable
            data = connection.recv(1024).decode()
            data = json.loads(data)              
            
            #Attack based on fed data, then break subloop upon completion
            try:
                while True:   
                    if data:
                        print(data)
                        try:
                        #Agent confirmation on registration success
                            if data["REGISTRATION"] == "SUCCESS":
                                print("Registration succeeded")
                                break
                            else:
                                print("Registration failed, check the agent for more detailed logging")
                                break
                        except Exception as e:
                            print("Failed to setup proper connection with agent1: ", e)
                            break
                    else:
                        print('Data transmission finished from', addr, " closing connection and start listening mode again")
                        break
            finally:
                connection.close()

    def register_agents(self, agents=["192.168.176.108"]):
         # The agent's hostname or IP address
        # The port used by the agent
        PORT = 8574

        #Generate payload data
        data = {"GOAL": "REGISTER", "COMMAND_CENTER_IP": "192.168.0.88"}
        data = json.dumps(data)


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            for agent in agents:
                try:
                    #Connect to the agent
                    s.connect((agent, PORT))
                    #Send the registration data
                    s.sendall(data.encode())
                except Exception as e:
                    print("Failed to setup proper connection with agent2: ", e)

                s.close()

      #  print(f"Received {response!r}")

