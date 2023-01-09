from command_center import CommandCenter
from threading import Thread

#Create CommandCenter singleton
cc = CommandCenter()

#Start listening on a new thread to keep other actions available
listen_thread = Thread(target=cc.listen)
listen_thread.start()


cc.register_agents()