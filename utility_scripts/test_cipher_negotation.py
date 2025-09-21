import ssl
import socket
import time

# Define missing variables
SSLCONTEXT = "ssl.TLSVersion.TLSv1_3"
#CIPHER = "ECDHE-RSA-AES128-GCM-SHA256"
IP = "127.0.0.1"
PORT = 12345
request_line = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(IP)

context = ssl.create_default_context()
# It's dirty with an eval, don't judge me
# if SSLCONTEXT == "ssl.TLSVersion.TLSv1_2":

context.maximum_version = eval(SSLCONTEXT)
#context.set_ciphers(CIPHER)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# else:
#     print("TLSv1.3 Ciphers cant be forced by the client yet. The cipher will be determined by the server")

# Calculate RTT time

sock = socket.create_connection((IP, int(PORT)))

ssock = context.wrap_socket(sock, server_hostname=IP, do_handshake_on_connect=False)
start_time = time.perf_counter_ns()
ssock.do_handshake()
end_time = time.perf_counter_ns()
ssock.sendall(request_line.encode())
print("Final Negotiation: ", ssock.version(), ssock.cipher())
ssock.recv(4096)

ssock.close()