
import os
import ast
import statistics
import sqlite3
from sqlalchemy import create_engine, Table, MetaData

##Script to convert the data from the database to a list of lists.
##This allows data processing and manipulation to be done on the data.
##This data is then used to consolidate results into an average and standard deviation per test cluster. 

# Path for database
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../database')

# Setup engine
engine = create_engine(f'sqlite:///{path}/CC_DATABASE.db')
connection = engine.connect()

# Connect to Agent Machines Table
metadata = MetaData()
mytable = Table('AGENT_RTT', metadata, autoload_with=engine)

# Retrieve all rows from the table
query = mytable.select()
result = connection.execute(query)
result_list = result.fetchall()

# Extract plain data as a list
result_mutated_list = [list(row) for row in result_list]



#----------------- List cleanup -----------------
for x in result_mutated_list:
    # add a new item that will become the list location
    x.append(ast.literal_eval(x[2]))
    # convert the string to a list
    x[2] = ast.literal_eval(x[2])
    # set the cipher suit from the string to a different list location
    x[2] = x[2][0]
    # remove the cipher suit from the list with numbers
    x[3].pop(0)
    # create a totol of all numbers in the list
    average = sum(x[3]) / len(x[3])
    # add the total to the list
    x.append(average)
    #print(x[3])
    x.append(statistics.stdev(x[3]))



#  ----------------- Consolidation -----------------
# Filter on the attack
Attack_Count = 10
# Filter on the cipher suite
final_result = [0, '0.0.0.0', 'TLS_CHACHA20_POLY1305_SHA256', []]

# Group the data by the cipher suite
for y in result_mutated_list:
    if y[2] == final_result[2]:
        if len(y[3]) == Attack_Count:
            for x in y[3]:
                final_result[3].append(x)
       
#print(final_result)
# print(final_result)
print("average: ", sum(final_result[3]) // len(final_result[3]))
print("deviation: ", statistics.stdev(final_result[3]))
# print(len(final_result[3]))
