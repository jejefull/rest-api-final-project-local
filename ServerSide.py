import requests
import os
import utils1.logging_api as logger # requires utils/loggin_api.py
import datetime
import traceback
import pymssql
import json

from flask import Flask
from flask import render_template, request, redirect, url_for

app = Flask(__name__)

def init_logger():
    with open(r'C:\Users\jeremy\Documents\LOGFILE\user_conf.json') as json_file:
        conf = json.load(json_file)
        #log_file_location=D:\temp\logs\ebay.log'\n'
        #log_level=DEBUG
        logger.init(f'{conf["log_file_location"]}'+
                    f'{datetime.datetime.now().year}_'+
                    f'{datetime.datetime.now().month}_' +
                    f'{datetime.datetime.now().day}_' +
                    f'{datetime.datetime.now().hour}_' +
                    f'{datetime.datetime.now().minute}_' +
                    f'{datetime.datetime.now().second}' + '.log'
                    , conf["log_level"])
        #open log file and write

def test_db_connection():
    try:
        logger.write_lo_log(f'Testing connection to [{conf["server"]}] [{conf["database"]}]', 'INFO')
        conn = pymssql._mssql.connect(server=conf['server'], user='', password='',
                                    database=conf['database'])
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to connecto to db [{conf["server"]}] [{conf["database"]}]', 'ERROR')
        logger.write_lo_log(f'Failed to connecto to db {e}', 'ERROR')
        logger.write_lo_log(f'Failed to connecto to db {tr}', 'ERROR')
        print('Faild to connect to db ... exit')
        exit(-1)
    #test the dba online and there is communication

@app.route('/users', methods = ['GET','POST'])
def getpost_all_clients():
    try:
        if request.method=='GET':
            with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                        database=conf['database']) as conn:
                query='SELECT * FROM USERS' #ask from database all users
                conn.execute_query(query)
                result = []
                for row in conn:
                    print(f'{row["id_Al"]} ')
                    result.append({'ID': row["id_Al"], 'FULL NAME' : row["full_name"], 'PASSWORD' : row["password"], 'REAL ID' : row["real_id"]})
                    #insert all client on result
                    allclients=result
                print('=================== was pymssql._mssql connector')
                print('ALLCLIENT GET: ',result)
                return json.dumps(result)#return to the client result in json format with all users
            #GET ALL CLIENTS ON

        if request.method == 'POST':
            e=''
            logger.write_lo_log('/users POST', 'INFO')
            query = ''
            new_customer = request.get_json()
            print('new_customer: ', new_customer)
            #receive from clientside new client to add

            with pymssql._mssql.connect(server=conf['server'], user='', password='',database=conf['database']) as conn:
                print('real_id',new_customer['real_id'])
#                cursor = conn.cursor(as_dict=True)
#                cursor.callproc('FindId',"'",new_customer['real_id'],"'")
#                for row in cursor:
#                    print('callproc!!!!!!!!! '+f'{new_customer["real_id"]} {new_customer["full_name"]}')


                query = 'INSERT INTO dbo.USERS (full_name, password, real_id) ' + f"VALUES ('{new_customer['full_name']}', '{new_customer['password']}', '{new_customer['real_id']}');"
                print('query: ', query)

                #insert in dba the new user


                logger.write_lo_log(f'/customers POST new customer {new_customer}', 'INFO')
                logger.write_lo_log(f'/customers POST new customer query {query}', 'DEBUG')

                conn.execute_query(query)
                new_customer['Error'] = 'no'
                new_customer = new_customer, new_customer['error']
                #add to dictionary new_customer new_customer['Error'] = 'no'

                return json.dumps(new_customer)
                #send to the clients side the new user

    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        print('error: ',e)
        if (str(e).find('duplicate')>0) :
            print('duplicate')
            return json.dumps({'Error': 'duplicate'})
        # if exeption send error with word duplicate , server return dic {'Error': 'duplicate'}

        return json.dumps({'Error': 'err'})
            #if there is an other error sever send to clientside


@app.route('/users/<int:id>', methods=['GET'])
def get_by_id(id):
    query = ''
    try:
        with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                    database=conf['database']) as conn:
            query = f'SELECT * FROM USERS WHERE id_Al={id}'
            #ask from dba on ly 1 user with id
            conn.execute_query(query)
            result = []
            for row in conn:
                result.append({'ID': row["id_Al"], 'FULL NAME' : row["full_name"], 'PASSWORD' : row["password"], 'REAL ID' : row["real_id"]})

                print(f'{row["id_Al"]} {row["full_name"]} {row["password"]} {row["real_id"]}')
                # SALARY requires exytra parsing
                result = {'ID': row["id_Al"], 'NAME': row["full_name"], 'AGE': row["password"], 'REAL ID': row["real_id"]}
            print(result)
            return json.dumps(result)
        #return to client side the user
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error': e})

@app.route('/users/<int:id>', methods = ['DELETE'])
def del_by_id(id):
    query = ''
    try:
        with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                    database=conf['database']) as conn:
            query = f'DELETE FROM USERS WHERE id_Al={id}'
            #send to dba to remove user with id
            conn.execute_query(query)
            return json.dumps({'status': 'success'})
        #send to clientside sucess
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error' : e})

@app.route('/users/<int:id>', methods = ['PUT'])
def update_by_id(id):
    query = ''
    try:
        with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                    database=conf['database']) as conn:
            update_customer = request.get_json()
            print('update_customer: ',update_customer)
            logger.write_lo_log(f'/user PUT new user {update_customer}', 'INFO')

            query = f'UPDATE dbo.USERS '+f"SET full_name='{update_customer['full_name']}', password='{update_customer['password']}',real_id='{update_customer['real_id']}'"+f' WHERE id_Al={id}'
            print('query: ',query)
            #send to dba update the users details

            conn.execute_query(query)
            return json.dumps({'status': 'success'})
        #send to the client side success
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error' : e})

@app.route('/users/signin', methods = ['POST'])
def SignIn_clients():
    try:
            logger.write_lo_log('/SignIn_clients POST', 'INFO')
            query = ''
            check_customer = request.get_json()
            print('check_customer: ', check_customer)

            with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                            database=conf['database']) as conn:
                query = 'SELECT * FROM dbo.USERS WHERE ' + f"password='{check_customer['password']}' AND real_id='{check_customer['real_id']}';"
                print('qery: ',query)
                #send to dba if there is an user exit
                logger.write_lo_log(f'/customers POST new customer {check_customer}', 'INFO')
                logger.write_lo_log(f'/customers POST new customer query {query}', 'DEBUG')
                conn.execute_query(query)
                result = []

                for row in conn:
                    print(f'{row["id_Al"]} {row["full_name"]} {row["password"]} {row["real_id"]}')
                    result = {'ID': row["id_Al"], 'full_name': row["full_name"], 'password': row["password"], 'real_id ID': row["real_id"]}
            # if client exit , return the same client. if not exit send an result empty
            return json.dumps(result)
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error': e})



@app.route('/flights', methods = ['GET'])
def get_all_flight():
    try:
            with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                        database=conf['database']) as conn:
                query='SELECT * FROM FLIGHTS WHERE remaining_seats > 0'
                #ask to the dba if there is seat remaining
                conn.execute_query(query)
                result = []
                for row in conn:
                    originecountry = convertCountry(row["origin_country_id"])
                    #send to function that convert the id state to name state
                    print('originecountry: ',originecountry)
                    result.append({'ID': row["flight_id"], 'DATE' : row["timestamp"].strftime("%m/%d/%Y, %H:%M:%S"), 'REMAINING SEAT' : row["remaining_seats"], 'ORIGINE ID' : convertCountry(row["origin_country_id"]), 'DESTINATION ID' : convertCountry(row["dest_country_id"])})
                    # result receive flight
                print('ALLFLIGHTS RESULT GET: ',result)
                return json.dumps(result)
                # send to the client side the flight
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error': 'err'})

def convertCountry(numberId):
    try:
        with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                    database=conf['database']) as conn:

            query = f'SELECT * FROM dbo.COUNTRIES WHERE code_al={numberId}'
            #ask to dba what name of country with the id
            print('query: ',query)
            conn.execute_query(query)
            result = []
            for row in conn:
                result.append({'ID': row["code_al"],'NAME': row["name"]})
            dic= json.dumps(result)
            return result[0]["NAME"]
        #function return the state name
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error': 'err'})


@app.route('/tickets', methods = ['GET','POST'])
def post_all_tickets():
    try:
        if request.method=='GET':
            with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                        database=conf['database']) as conn:
                query='SELECT * FROM TICKETS'
                #ask to dba all tickets
                conn.execute_query(query)
                result = []
                for row in conn:
                    #result.append({ 'ID' : row["ID"], 'NAME' : row["NAME"], 'AGE' : row["AGE"], 'ADDRESS' : row["ADDRESS"], 'SALARY' : row["SALARY"]})
                    result.append({'ID': row["ticket_id"], 'USER ID' : row["user_id"], 'FLY ID' : row["flight_id"]})
                print('=================== was pymssql._mssql connector')
                print('ALLTICKETS GET: ',result)
                return json.dumps(result)
            #put all tickets on result and return to clientside
        if request.method == 'POST':
            logger.write_lo_log('/tickets POST', 'INFO')
            query = ''
            new_ticket = request.get_json()
            print('new_ticket: ', new_ticket)

            with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                            database=conf['database']) as conn:

                query='SELECT * FROM FLIGHTS'
                #ask to dba all flihts
                conn.execute_query(query)
                result = []
                res_ticket=0
                for row in conn:
                    print('new ticket: ',new_ticket["flight_id"]+'row: ',row["flight_id"])
                    if int(new_ticket["flight_id"])==int(row["flight_id"]):
                        res_ticket=1
                        print('res_ticket',res_ticket)
                print('res_ticket ',res_ticket)
                if res_ticket==0:
                    return json.dumps(result)
                #get all flights and verif if id flight on ticket it is the same id flight on flight table
                #if there is not, client try to buy flight  id not exit, return empty result




                flightid=new_ticket['flight_id']
                query = f'SELECT * FROM FLIGHTS WHERE flight_id={flightid}'
                conn.execute_query(query)
                #ask from dba flight table  user want to buy with flight id

                result = []
                for row in conn:
                    result.append({'REMAINING SEAT': row["remaining_seats"]})

                if int(result[0]['REMAINING SEAT'])>0:#only if there is remainig seat, write to dba the buying

                    query = 'INSERT INTO dbo.TICKETS (user_id, flight_id) ' + f"VALUES ('{new_ticket['user_id']}', '{new_ticket['flight_id']}');"
                    logger.write_lo_log(f'/customers POST new customer {new_ticket}', 'INFO')
                    #write to dba the buying ticket

                    logger.write_lo_log(f'/customers POST new TICKET query {query}', 'DEBUG')
                    conn.execute_query(query)

                    query = 'UPDATE FLIGHTS ' + f"SET remaining_seats = {str(int(result[0]['REMAINING SEAT']-1))}"+f" WHERE flight_id = {new_ticket['flight_id']}"
                    print(query)
                    # write to dba the remainin seat -1
                    logger.write_lo_log(f'/customers POST new customer {new_ticket}', 'INFO')

                    logger.write_lo_log(f'/customers POST new TICKET query {query}', 'DEBUG')
                    conn.execute_query(query)

                    return json.dumps(new_ticket)
                #return the ticket user buy
                else:
                    return json.dumps({'Error': 'last_Place'})


    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error': 'err'})


@app.route('/tickets/<int:id>', methods=['GET','DELETE'])
def get_delete_ticket_by_id(id):
    query = ''
    try:
        if request.method=='GET':
            with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                        database=conf['database']) as conn:
                query = f'SELECT * FROM TICKETS WHERE user_id={id}'
                #ask to dba ticket with id
                conn.execute_query(query)
                result = []
                for row in conn:
                    result.append({'FLIGHT ID': row["flight_id"],'TICKET ID':row["ticket_id"]})

                    # SALARY requires exytra parsing
                print(result)
                return json.dumps(result)
            #put on result ticket and return to clientside
        if request.method == 'DELETE':
            with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                        database=conf['database']) as conn:


                query='SELECT * FROM TICKETS'
                conn.execute_query(query)
                result = []
                res_check=0
                for row in conn:
                    result.append({'ID': row["ticket_id"], 'USER ID' : row["user_id"], 'FLY ID' : row["flight_id"]})
                    print("row['ticket_id']: ",row['ticket_id'],'id: ',id)
                    print()
                    if row['ticket_id']==id:
                        res_check=1
                print('res: ',result)
                if res_check==0:
                    return json.dumps([])
                #verif if client try dto delete an existing ticket


                result=[]
                query = f'SELECT * FROM dbo.TICKETS WHERE ticket_id={id}'
                #ask to dba ticket with id to check it on flight table
                print('query: ', query)
                conn.execute_query(query)
                result = []
                for row in conn:
                    result.append({'ID': row["ticket_id"], 'FLIGHT ID': row["flight_id"]})
                print('res: ',result)
                print(result[0]["FLIGHT ID"])
                query = f'SELECT * FROM dbo.FLIGHTS WHERE flight_id={result[0]["FLIGHT ID"]}'
                #check on the flight id with the same id from ticket
                conn.execute_query(query)
                result = []
                for row in conn:
                    result.append({'FLIGHT ID': row["flight_id"], 'REMAINING SEATS': row["remaining_seats"]})
                print(result)
                query = f'UPDATE dbo.FLIGHTS ' + f"SET remaining_seats={result[0]['REMAINING SEATS']+1}" + f' WHERE flight_id={result[0]["FLIGHT ID"]}'
                conn.execute_query(query)
                result = []
                query = f'DELETE FROM TICKETS WHERE ticket_id={id}'
                #write to the database remiang seat +1 after deleting
                conn.execute_query(query)
                result = [{'status': 'delete'}]
                return json.dumps(result)
            #return status to clientside
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error': e})


@app.route('/flights/<int:id>', methods=['GET'])
def get_flight_by_id(id):
    query = ''
    try:
        with pymssql._mssql.connect(server=conf['server'], user='', password='',
                                    database=conf['database']) as conn:
            query = f'SELECT * FROM FLIGHTS WHERE flight_id={id}'
            #ask to dba flights with id
            conn.execute_query(query)
            result = []
            for row in conn:
                result.append({'DATE': row["timestamp"].strftime("%m/%d/%Y, %H:%M:%S"),'ORIGINE ID': convertCountry(row["origin_country_id"]),
                               'DESTINATION ID': convertCountry(row["dest_country_id"]),'REMAINING SEAT':row["remaining_seats"]})

            print(result)
            return json.dumps(result)
        #return result
    except Exception as e:
        tr = traceback.format_exc()
        logger.write_lo_log(f'Failed to run [{query}] to db {tr}', 'ERROR')
        return json.dumps({'Error': e})




with open(r'C:\Users\jeremy\Documents\LOGFILE/user_conf.json') as json_file:
    conf = json.load(json_file)
    #open the configuration file


app.run()
