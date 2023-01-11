from command_center import CommandCenter
from threading import Thread
import asyncio
import time

# Create CommandCenter singleton
cc = CommandCenter()

async def start_command_center():
    await cc.start_command_center()

def start_command_center_thread():
    asyncio.run(start_command_center())

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    command_center_thread = Thread(target=loop.run_until_complete, args=(start_command_center(),))
    command_center_thread.start()

print("text")
asyncio.run(cc.register_agents(["192.168.176.108"]))

while True:
    print(cc.agent_list)
    time.sleep(1)