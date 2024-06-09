from agent import AgentInstance
import socket

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
# retrieve the local IP
local_ip = get_ip_address()

try:
    agent = AgentInstance(LOCAL_IP=local_ip, COMMAND_CENTER="192.168.1.88")
    agent.listen()
except Exception as e:
    print(e)
    pass

