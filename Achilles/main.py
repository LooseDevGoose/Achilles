from command_center import CommandCenter
from gui import flask_main
from threading import Thread
import asyncio
import time


##Script to start the command centrum and GUI webserver (FLASK)
# Instantiate CommandCenter singleton
cc = CommandCenter()
print("\u001b[32mInstantiating Command Center..")

# Start the command center with async function
async def start_command_center():
    await cc.start_command_center()


print("Creating new Thread for Command Center..")



if __name__ == "__main__":
    print("Starting Command Centrum..")
 
   
     # Start new thread for TCP server (Command Center)
    #loop = asyncio.new_event_loop()
    command_center_thread = Thread(target=asyncio.run, args=(start_command_center(),))
    command_center_thread.start()
    #asyncio.run(cc.register_agents(["192.168.176.108"]))

    print("Starting GUI..")
    print("Starting Flask Server..")
    flask_main.start_flask()

   
    
