import socket
import json
import time
import asyncio

from agent_instance import AgentInstance

agent = AgentInstance()
agent.listen()