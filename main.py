from command_center import CommandCenter
from gui import flask_main
from threading import Thread
import asyncio
import time

# Script to start the command center and GUI webserver on localhost:5000
# Instantiate CommandCenter singleton
cc = CommandCenter()
print("\u001b[32mInstantiating Command Center..")

async def start_command_center():
    # Start the command center with async function
    await cc.start_command_center()

print("Creating new Thread for Command Center..")

def start_async_command_center():
    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_command_center())

if __name__ == "__main__":
    print("Starting Command Center..")
 
    try:
        # Start new thread for TCP server (Command Center)
        command_center_thread = Thread(target=start_async_command_center)
        command_center_thread.start()
    except Exception as e:
        print("Could not start Command Center: ", e)

    try:
        print("Starting GUI..")
        flask_main.start_flask()
    except Exception as e:
        print("Could not start Flask Server (GUI): ", e)
 