# echo-client.py
import socket
import json
import asyncio
# Database prerequisites
import sqlite3
import os
import time


class CommandCenter:

    def __init__(self, PORT=9191):
        # Default required Variables (CONSTANTS)
        self.HOST = socket.gethostname()
        self.PORT = PORT
        self.LOCAL_IP = socket.gethostbyname(self.HOST)
        self.running = False

        # Path of database
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../database')

        # List to keep track of all agents (including pre-registered ones in case of Command Center reboot)
        self.agent_list = {}
        # self.populate_agent_list()

    # Check if database exist, otherwise create one
    def create_database(self):
        # Get the current working directory of the database

        # Connect (or create) to the database
        conn = sqlite3.connect(fr'{self.path}\CC_DATABASE.db')
        # Create cursor for database operations
        cursor = conn.cursor()
        # Create table if not exists
        cursor.execute('''CREATE TABLE IF NOT EXISTS AGENT_MACHINES (
        id INTEGER PRIMARY KEY,
        hostname TEXT,
        ip TEXT UNIQUE,
        heartbeat INTEGER
        )''')
        # Save and close
        conn.commit()
        cursor.close()
    def populate_agent_list(self):
        # get all agents from database and add to list
        conn = sqlite3.connect(fr'{self.path}\CC_DATABASE.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AGENT_MACHINES")
        self.agent_list = cursor.fetchall()
        print(self.agent_list)
        conn.close() 
        

    async def register_agents(self, agents):
        # Generate payload data
        DATA = json.dumps({"GOAL": "REGISTER", "COMMAND_CENTER_IP": self.LOCAL_IP})

        if agents:

            for agent in agents:
                reader, writer = await asyncio.open_connection(agent, 8574)
                writer.write(DATA.encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
        else:
            print("No agents provided for registration, skipping")

    # Add agent to database upon registration
    def add_agent_to_database(self, agent_ip, hostname):
        # Get the current working directory of the database
        conn = sqlite3.connect(fr'{self.path}\CC_DATABASE.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS AGENT_MACHINES (
        id INTEGER PRIMARY KEY,
        hostname TEXT,
        ip TEXT UNIQUE,
        heartbeat INTEGER
        )''')

        # Insert data into the database based on a unique IP
        cursor.execute('''INSERT OR IGNORE INTO AGENT_MACHINES
        (hostname, ip, heartbeat) VALUES (?, ?, ?)''',
        (f'{hostname}', f'{agent_ip}', '0'))
        conn.commit()
        conn.close()

    # Set agent information in the database
    def update_agent_information(self, agent_ip):
        conn = sqlite3.connect(fr'{self.path}\CC_DATABASE.db')
        cursor = conn.cursor()

        update_agent_heartbeat = """Update AGENT_MACHINES set heartbeat = ? where ip = ?"""
        _hearbeat_time = time.time()
        data = (_hearbeat_time, agent_ip)
        cursor.execute(update_agent_heartbeat, data)
        conn.commit()
        conn.close()

    # Async function to update last seen time of agent every 10 seconds
    async def update_agent_last_seen(self):
        
        while True:
            if self.agent_list:

                for agent in self.agent_list.copy():
                    # only run code if agent is marked as active
                    if self.agent_list[f'{agent}']['STATUS'] == "ACTIVE":
                        _hb = int(self.agent_list[f'{agent}']['HEARTBEAT'])
                        # ping the agent and add 15 seconds to the heartbeat if no response
                        self.agent_list[f'{agent}']['HEARTBEAT'] = _hb
                        #print(self.agent_list)
                        # Update the agent information in the database
                        _hb += 15
                        self.agent_list[f'{agent}']['HEARTBEAT'] = _hb

                        # Update the agent information in the database
                        self.update_agent_information(agent)

                        # If the agent is gone for more than 60 seconds, set the status to inactive
                        if _hb > 120:
                            self.agent_list[f'{agent}']['STATUS'] = "INACTIVE"
                            print(f"Agent {agent} is inactive")
                            self.agent_list.pop(f'{agent}')
                            # update in database
                            conn = sqlite3.connect(fr'{self.path}\CC_DATABASE.db')
                            cursor = conn.cursor()
                            cursor.execute(f"DELETE FROM AGENT_MACHINES WHERE ip = '{agent}'")
                            conn.commit()
                
                await asyncio.sleep(15) #15
            else:
                print("No agents to update heartbeat, skipping for 15 seconds")
                await asyncio.sleep(15) #10


    async def listen(self, reader, writer):
        try:
            # Wait for message from client
            data = await reader.read(1024)
            message = json.loads(data.decode())
            addr = writer.get_extra_info('peername')
            print(f'Received message from {addr}: {message}')

            writer.write(data)
            await writer.drain()
            writer.close()

        except Exception as e:
            print(e)

        while message:
            # In case of Agent heartbeat message
            if "HEARTBEAT" in message:

                _ip = message["HEARTBEAT"]["AGENT_IP"]
                # Update the agent heartbeat time
                self.agent_list[f"{_ip}"] = {"HEARTBEAT": 0, "STATUS": "ACTIVE"}

                break
                # In case of Agent registration message
            elif "REGISTRATION" in message:

                _ip = message["REGISTRATION"]["AGENT_IP"]
                _hostname =message["REGISTRATION"]["HOSTNAME"]
                print("Registration succeeded for:", message["REGISTRATION"]["AGENT_IP"])

                # Add the agent to the agent list
                self.agent_list[f"{_ip}"] = {"HOSTNAME": f"{_hostname}", "HEARTBEAT": 0, "STATUS": "ACTIVE"}

                # Add the agent to the CC database
                self.add_agent_to_database(
                    agent_ip=message["REGISTRATION"]["AGENT_IP"],
                    hostname=message["REGISTRATION"]["HOSTNAME"])
                break

            else:
                print('Data transmission finished from', addr, " closing connection and start listening mode again")
                break

    async def start_command_center(self):
        # Define Server
        server = await asyncio.start_server(self.listen, "0.0.0.0", 9191)

        # Print Server Start
        print(f"Command Centrum started and is listening on {server.sockets[0].getsockname()}")

        # Start server + all subtasks async
        await asyncio.gather(
            server.serve_forever(),
            self.update_agent_last_seen()
            )