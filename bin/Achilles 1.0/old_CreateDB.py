import sqlite3
import os
import time

#Get the current working directory of the script
path = os.path.dirname(os.path.realpath(__file__))

# connect (or create) to the database
conn = sqlite3.connect(f'{path}\CC_DATABASE.db')

# create a cursor object
cursor = conn.cursor()

# # create a table
# cursor.execute('''CREATE TABLE IF NOT EXISTS AGENT_MACHINES (id INTEGER PRIMARY KEY, hostname TEXT, ip TEXT UNIQUE, heartbeat INTEGER)''')

# # insert data into the database based on a unique IP
# cursor.execute('''INSERT OR IGNORE INTO AGENT_MACHINES (hostname, ip, heartbeat) VALUES (?, ?, ?)''', ('linuxvm1','192.168.176.1', '1'))


# # commit the changes
# conn.commit()

# execute a SELECT statement
cursor.execute('SELECT * FROM AGENT_MACHINES')

# retrieve the results
results = cursor.fetchall()

# print the results
for row in results:
    print(row)
# close the connection
conn.close()