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

        # List to keep track of all active agents
        self.agent_list = {}

        # Path of database
        self.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../database')

    # Check if database exist, otherwise create one
    def create_database(self):
        # Get the current working directory of the database

        # Connect (or create) to the database
        conn = sqlite3.connect(fr'{self.path}\CC_DATABASE.db')
        # Create cursor for database operations
        cursor = conn.cursor()

        # Save and close
        conn.commit()
        cursor.close()

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
        print("added to DB")
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

                for agent in self.agent_list:
                    self.agent_list[f'{agent}']['LAST_SEEN'] += 15
                    print(self.agent_list)
                await asyncio.sleep(15)
            else:
                print("No agents to update heartbeat, skipping for 60 seconds")
                await asyncio.sleep(60)


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
            if "HELLO" in message:
                print("decoded :)")
                break
            # In case of Agent heartbeat message
            elif "HEARTBEAT" in message:

                _ip = message["HEARTBEAT"]["AGENT_IP"]
                print(message["HEARTBEAT"]["AGENT_IP"], " just sent a beat")

                # Calculate the times
                # Set the new_time to old_time
                # The times are  in unix time, so substract old from new and you have the passed time
                self.agent_list[f"{_ip}"]["LAST_SEEN"] = 0

                break
                # In case of Agent registration message
            elif "REGISTRATION" in message:

                _ip = message["REGISTRATION"]["AGENT_IP"]
                print("Registration succeeded for: ", message["REGISTRATION"]["AGENT_IP"])

                # Add the registration time for initial heartbeat calculation
                self.agent_list[f"{_ip}"] = {}

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