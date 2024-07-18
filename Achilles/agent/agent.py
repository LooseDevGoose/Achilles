import socket
import json
import time
from threading import Thread
import asyncio
import ssl


class AgentInstance:

    def __init__(self, LOCAL_IP, PORT=8574, COMMAND_CENTER=None):
        # Default required Variables (CONSTANTS)
        self.HOST = socket.gethostname()
        self.PORT = PORT
        self.LOCAL_IP = LOCAL_IP
        self.UNREGISTERED = True
        print("Achilles Agent Version 0.9.1")

        # Variables
        self.COMMAND_CENTER = COMMAND_CENTER
        self.should_heartbeat = False

        # Thread(s)
        self.heartbeat_thread = Thread(target=self.send_heartbeat)

        # Register the agent
        self.register_agent()

        # Determine if the agent should be heartbeating
        if self.UNREGISTERED is False and self.should_heartbeat is False:
            # Start the heartbeat thread
            print("Starting Heartbeat thread to prove health status")
            self.should_heartbeat = True
            self.heartbeat_thread.start()
        elif self.UNREGISTERED is True and self.should_heartbeat is True:
            print("Stopping Heartbeat thread")
            self.should_heartbeat = False
            self.heartbeat_thread.stop()
    
    def register_agent(self):
            
         # Register the agent
            try:
                print(f"\033[1;33mRegistering at Command Center: \033[1;32m{self.COMMAND_CENTER}")
                DATA = json.dumps({"REGISTRATION": {"AGENT_IP": f"{self.LOCAL_IP}", "HOSTNAME": f"{self.HOST}"}})
                # Send the registration data to the command center
                socket.create_connection((self.COMMAND_CENTER, 9191)).sendall(DATA.encode())
                self.UNREGISTERED = False
                print("\033[1;32mRegistration completed. Happy testing!")
            except Exception as e:
                print("\033[1;31mERROR could contact Command Center: ", e)
                print("Retrying in 5 seconds..")
                time.sleep(5)
                self.register_agent()


    async def listen(self, reader, writer):
        try:
            data = await reader.read(1024)
            message = json.loads(data.decode())
            addr = writer.get_extra_info('peername')
            print(f'Received message from {addr}')

            writer.write(data)
            await writer.drain()
            writer.close()    
        
        except Exception as e:
            print(e)
        
       
        while message:
            # Attack the target if there is an attack instruction
            if "ATTACK" in message and self.COMMAND_CENTER:
                message = message["ATTACK"]
            
                try:
                    # Start the attack function with a valid IP / PORT / PROTOCOL / HIT amount and the connection instance to report back metrics to the master
                    rtt_data = self.attack(PROTOCOL=message['PROTOCOL'], IP=message['TARGET'], PORT=message['PORT'], HITS=message['HITS'], CIPHER=message['CIPHER'])
                except Exception as e:
                    print("\033[1;31mERROR: Could not start attack: ", e)
                    break
                # Send the RTT Data back to the command center for processing
                try:
                    if rtt_data:
                        print(f"Sending RTT data to Command Center: {rtt_data}")
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((self.COMMAND_CENTER, 9191))
                            rtt_data = json.dumps({"RTT": rtt_data})
                            #send the RTT data list to the command center so it can be stored in the database
                            s.sendall((rtt_data.encode()))
                except Exception as e:
                    print("ERROR could not send RTT data to command center: ", e)
                    break
            else:
                if not self.COMMAND_CENTER:
                    print(
                        "This is probably because you tried to initiate connections without registering the command center first")
                break

    def attack(self, IP, PORT, HITS, CIPHER, PROTOCOL, data=b"Handshake Message", SSLCONTEXT=ssl.TLSVersion.TLSv1_2):
        print("\033[1;95m---------------------------------")
        print("\033[1;33mInitiating attack function on:")
        print("\033[1;33mTarget:", f"\033[1;32m{str(IP)}")
        print("\033[1;33mPort:", f"\033[1;32m{str(PORT)}")
        print("\033[1;33mProtocol:", f"\033[1;32m{str(PROTOCOL)}")
        print("\033[1;33mCipher:", f"\033[1;32m{str(CIPHER)}")
        print("\033[1;33mTLS Version:", f"\033[1;32m{str(SSLCONTEXT)}")
        print("\033[1;33mHits:", f"\033[1;32m{str(HITS)}")
        print("\033[1;95m---------------------------------")

        # List for storing the roundtriptimes whom we send back to the command center
        _RTT = []
        # Append the RTT list with the Cipher suite used, we will use this later on for graphs
        _RTT.append(CIPHER)
        # Create the request line so we get an answer from the target
        request_line= "GET / HTTP/1.0\r\nHost: {IP}\r\n\r\n"
        # Check protocol and assign either to TCP or UDP
        for i in range(int(HITS)):
            try:
                if PROTOCOL == 'TCP':
                    
                    context = ssl.create_default_context()
                    context.maximum_version = ssl.TLSVersion.TLSv1_2
                    context.set_ciphers(CIPHER)

                     # Calculate RTT time
                    start_time = time.time()
                    
                    with socket.create_connection((IP, int(PORT))) as sock:
                        with context.wrap_socket(sock, server_hostname=IP) as ssock:
                            ssock.sendall(request_line.encode())
                            print(ssock.version(), ssock.cipher())
                            ssock.recv(4096)
                            ssock.close()
                    
                    end_time = time.time()
                    RTT = end_time - start_time
                    _RTT.append(RTT)
                    #_sockets.append(s)
    
                else:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    _sockets.append(s)
            except socket.error as e:
                if e.errno == 104:
                    print("\033[1;95mConnection reset by target, retrying to send data..")
                    # resending data to target
                    s.sendall(data)
                else:
                    print("\033[1;95mERROR: Could not send data to target: ", e)
                    _RTT = None
                    break
          
        # Return all the roundtrip time data to send to the command center
        return (_RTT)

    # Send HeartBeats to the command center to prove their Health Status | ALWAYS RUN ON A SEPERATE THREAD!
    def send_heartbeat(self):
        # Start the heartbeat
        while self.should_heartbeat:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # Send Heartbeat(HB) to Command Center
                    heartbeat_message = json.dumps({"HEARTBEAT": {"AGENT_IP": f"{self.LOCAL_IP}", "HOSTNAME": f"{self.HOST}"}})
                    # Connect to the command center and send the HB
                    s.connect((self.COMMAND_CENTER, 9191))
                    s.sendall(heartbeat_message.encode())
                    # close the connection
                    s.close()
                    # Print the heartbeat message with the current time
                    print(f"\033[1;32mHeartbeat sent to Command Center @ {time.ctime()}")
                    time.sleep(15)
            except Exception as e:
                print(f"\033[1;31mERROR: Failed to send Heartbeat to {self.COMMAND_CENTER}: ", e)
                try:
                    self.heartbeat_thread.join()
                except Exception as e:
                    print("\033[1;31mERROR: Could not stop heartbeat thread, it might be wise to reboot the agent: ", e)

        print("\033[1;95mWARNING: Heartbeat stopped!")

    async def start_agent(self, LOCAL_IP):
        # Define Server
        server = await asyncio.start_server(self.listen, LOCAL_IP, 8574)

        # Print Server Start
        print(f"Agent started and is listening on {server.sockets[0].getsockname()}")

        # Start server + all subtasks async
        await server.serve_forever()
        