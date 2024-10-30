# Achilles

Built for the GO-EUC research on TLSV1.2 vs TLSV1.3 handshakes.
A key challenge in this research is simulating connections in a way that ensures each handshake is unique, preventing results from being skewed by optimization techniques. Scalability is also crucial, as testing under variable loads provides better insights into handshake efficiency under stress. To meet these needs, I developed custom software called Achilles. Achilles uses a coordinator/agent architecture, with a central command center that distributes data to its agents. This data includes the target and specified cipher suite/protocol, enabling the simulation of a large number of unique handshakes. 

The command center has a web interface to increase efficiency and make the testing more approachable.
 
 
 
 
A connection is made by a containerized agent via Podman, and the agent will simulate its handshake ‘x’ times. It will then send the results back to the command center for processing.  
From a research perspective, it is essential to make both the results and methodology accessible, so the code has been made publicly available. Please note that Achilles is intended solely for research purposes and is not a commercial product. 
