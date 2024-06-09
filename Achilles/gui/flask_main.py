from flask import Flask, render_template
import os
import sqlite3
from sqlalchemy import create_engine, Table, MetaData


#Path for database
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../database')

#Flask app
app = Flask(__name__)


@app.route("/")
   

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/get-agents", methods=['POST'])
def get_db_agents():

    ##Retrieve agents from database
    #Setup engine
    engine = create_engine(f'sqlite:///{path}/CC_DATABASE.db')
    connection = engine.connect()

    #Connect to Agent Machines Table
    metadata = MetaData()
    mytable = Table('AGENT_MACHINES', metadata, autoload_with=engine)

    # Retrieve all rows from the table
    query = mytable.select()
    result = connection.execute(query)
    agent_list = result.fetchall()


    # Close the connection
    connection.close()
    print(agent_list)
    return render_template("index.html", agents=agent_list)

@app.route("/purge-database", methods=['POST'])
def purge_database():

   # purge the database
    conn = sqlite3.connect(fr'{path}\CC_DATABASE.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM AGENT_MACHINES")
    conn.commit()
    conn.close()

    return render_template("index.html")

def start_flask():
    app.run()#debug=false)

#Dev command to apply tailwind changes
#npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css --watch