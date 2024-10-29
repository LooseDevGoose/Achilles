from sqlalchemy import create_engine, Table, MetaData

engine = create_engine('sqlite:///CC_DATABASE.db')
connection = engine.connect()

metadata = MetaData()

mytable = Table('AGENT_MACHINES', metadata, autoload=True, autoload_with=engine)

# Retrieve all rows from the table
query = mytable.select()
result = connection.execute(query)
rows = result.fetchall()

# Print the rows
for row in rows:
    print(row[1])

# Close the connection
connection.close()