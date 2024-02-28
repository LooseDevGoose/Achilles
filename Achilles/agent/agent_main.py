from agent import AgentInstance
import socket

docker_ip = socket.gethostbyname(socket.gethostname())
print(docker_ip)
agent = AgentInstance(LOCAL_IP=docker_ip)
agent.listen()