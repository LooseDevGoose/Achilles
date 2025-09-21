from flask import Flask, render_template, request
import os
import ast
import sqlite3
import statistics
from sqlalchemy import create_engine, Table, MetaData
from main import cc


#Path for database
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../command_center/database')

#Flask app
app = Flask(__name__)


@app.route("/")
   

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/reports")
def reports():
    ##Retrieve results from database
    #Setup engine
    engine = create_engine(f'sqlite:///{path}/CC_DATABASE.db')
    connection = engine.connect()

    try:
        #Connect to Agent Machines Table
        metadata = MetaData()
        mytable = Table('AGENT_RTT', metadata, autoload_with=engine)

        # Retrieve all rows from the table
        query = mytable.select()
        result = connection.execute(query)
        result_list = result.fetchall()
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
            average = sum(x[3]) // len(x[3])
            # add the total to the list
            x.append(average)
            x.append(statistics.stdev(x[3]))
            x[3] = len(x[3])

    except Exception as e:
        print("Could not retrieve results from database: ", e)
        connection.close()
        return render_template("reports.html", results=[])


    
    # Close the connection
    connection.close()
    return render_template("reports.html", results=result_mutated_list)

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

@app.route("/start-attack", methods=['POST'])
def start_attack():
    print("Starting attack..")
    # Get the form data
    protocol = request.form.get('protocol')
    target = request.form.get('target')
    port = request.form.get('port')
    hits = request.form.get('hits')
    cipher = request.form.get('cipher')
    sslcontext = request.form.get('tlsversion')
    attackduration = request.form.get('attackduration')
    print(sslcontext)

    #print(protocol, target, port, hits, cipher)
    # if attackduration is 0, run normal attack, else run sustained attack
    if attackduration != "0":
        print(f"Starting sustained attack for {attackduration} minutes")
        cc.send_data_to_agents(protocol, target, port, hits, cipher, sslcontext, int(attackduration))
    else:
        cc.send_data_to_agents(protocol, target, port, hits, cipher, sslcontext)
    return render_template("index.html")

@app.route("/purge-database", methods=['POST'])
def purge_database():

   # purge the database
    conn = sqlite3.connect(fr'{path}\CC_DATABASE.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM AGENT_MACHINES")
    conn.commit()
    conn.close()

    return render_template("index.html")

@app.route("/clear-rtt")
def clear_rtt():
    
        # purge the database
        conn = sqlite3.connect(fr'{path}\CC_DATABASE.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM AGENT_RTT")
        conn.commit()
        conn.close()
    
        return render_template("index.html")

def start_flask():
    app.run()#debug=false)

#Dev command to apply tailwind changes
#npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css --watch