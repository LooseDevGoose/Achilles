from agent import AgentInstance
from threading import Thread
import socket
import asyncio
import os

command_center_ip = os.environ.get("COMMAND_CENTER_IP")

def get_ip_address():
    # Discover local IP address, this is needed for the command center to know where to send commands
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
# retrieve the local IP
local_ip = get_ip_address()


##Script to start the command centrum and GUI webserver (FLASK)
# Instantiate CommandCenter singleton
agent = AgentInstance(LOCAL_IP=local_ip, COMMAND_CENTER="192.168.1.88")


# Start the command center with async function
async def start_agent():
    await agent.start_agent(local_ip)

if __name__ == "__main__":
    print("Starting Agent..")
 
    try:
        # Start new thread for TCP server (Command Center)
        #loop = asyncio.new_event_loop()
        agent_thread = Thread(target=asyncio.run, args=(start_agent(),))
        agent_thread.start()
        #asyncio.run(cc.register_agents(["192.168.176.108"]))
    except Exception as e:
        print("Could not start agent: ", e)
