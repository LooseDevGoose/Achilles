# echo-client.py
import socket
import json



 # The agent's hostname or IP address
agents = ["192.168.1.108"]
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
            s.send(data.encode())
            response = s.recv(1024).decode()
            response = json.loads(data)
            s.close()
            if response["REGISTRATION"] == "SUCCESS":
                print("Registration succeeded")
            else:
                print("Registration failed, check the agent for more detailed logging")
        except Exception as e:
            print("Failed to setup proper connection with agent: ", e)
        s.close()

print(f"Received {response!r}")

