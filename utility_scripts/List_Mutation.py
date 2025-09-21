
import os
import ast
import statistics
import sqlite3
from sqlalchemy import create_engine, Table, MetaData



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

# Extract plain data as a list of dictionaries or tuples

# Option 2: As list of tuples (just values)
result_mutated_list = [list(row) for row in result_list]

#print(result_mutated_list)

# List cleanup
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






