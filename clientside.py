import requests
import json
import datetime
import traceback
import pymssql

import utils1.logging_api as logger # requires utils/loggin_api.py

url = "http://localhost:5000/users"
url2 = "http://localhost:5000/users/signin"
url3 = "http://localhost:5000/flights"
url4 = "http://localhost:5000/tickets"

def init_logger():
    with open(r'C:\Users\jeremy\Documents\LOGFILE\user_conf.json') as json_file:
        conf = json.load(json_file)
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
    #test the dba online and there is communication
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



def newClient(new_cust):

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    resp = requests.post(url, data=json.dumps(new_cust), headers=headers)# send to the rest server the new user
    res={}
    res = json.loads(resp.content)# receive from server result
    return res # return result

def showCustomer():
    cust_id = input("What's the cusgtomer id to get?")
    resp = requests.get(f'{url}/{cust_id}')# send to the server to print 1 user with id number
    if resp.status_code != 200:# if server return error
        print('Unexpected error')
        return
    customer1 = json.loads(resp.content)#receive from server the user
    if (customer1 == []):
        print('-- Not found --')#if result is empty,id user not in data base
    else:
        print(customer1)#print user

def showAllCustomers():
    resp = requests.get(url)#send to server to print all users
    if resp.status_code != 200:
        print('Unexpected error')
        return
    customers = json.loads(resp.content)#receive from server all users
    for c in customers:
        print(c)#print all users



def signIn(new_cust):
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    resp = requests.post(url2, data=json.dumps(new_cust), headers=headers)#send to server to chek if there is new_cust id in data base
    if resp.status_code != 200:
        return 2
    customer1 = json.loads(resp.content)

    if (customer1 == []):
        return 3#there is not user with this id number
    else:
        return customer1 #return the user who sign in

def showFlights():
    resp = requests.get(url3)# send to sever to print all flights the client can to buy
    if resp.status_code != 200:
        print('Unexpected error')
        return
    flight = json.loads(resp.content) #server return all flights
    for c in flight:
        print('PLEASE PRESS ',c['ID'],'FOR TICKET IN DATE:',c['DATE'],' FROM',c['ORIGINE ID'],' TO ',c['DESTINATION ID'],'WITH',c['REMAINING SEAT'],'PLACE REMAINDING')
        # print flight

def buyTicket(idClient):
    resp = requests.get(url4) #send to server to print flights
    if resp.status_code != 200:
        print('Unexpected error')
        return
    flight = json.loads(resp.content)

    showFlights() #print flights to buy
    print('PLEASE PRESS 0 FOR EXIT')
    idFlight = input("What's flight you want to buy ?") # user need to choice ticket to buy
    if int(idFlight)==0 :
        return 1 #if user choice 0 , back to menu
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    new_Ticket = {}

    new_Ticket['user_id'] = idClient
    new_Ticket['flight_id'] = idFlight
    resp = requests.post(url4, data=json.dumps(new_Ticket), headers=headers) #send to server to add ticket
    ticket1 = json.loads(resp.content)
    if ticket1==[]:
        return 2 # if user try to buy ticket not exist
    printFlight(ticket1['flight_id']) #print ticket that client buy

def printFlight(flightId):
    resp = requests.get(f'{url3}/{flightId}') # send to server to print flights
    flight = json.loads(resp.content) #server return flight
    print('YOU BUY', 'TICKET FROM', flight[0]['ORIGINE ID'], ' TO ', flight[0]['DESTINATION ID'], ' DATE:',flight[0]['DATE'])


def printTicket(cust_id):
        resp = requests.get(f'{url4}/{cust_id}') #send to server to print tiket with id user
        if resp.status_code != 200:
            print('Unexpected error')
            return
        ticket = json.loads(resp.content)
        if (ticket == []): #if return empty , client have not tickets
            return ticket
        else:
            for c in ticket:
                #for all ticket send to server which flight user buy and return it
                flightId=c['FLIGHT ID']
                ticketId=c['TICKET ID']
                resp = requests.get(f'{url3}/{flightId}')
                flight = json.loads(resp.content)
                print('YOU BUY TICKET ID:',c['TICKET ID'],'FROM', flight[0]['ORIGINE ID'], ' TO ', flight[0]['DESTINATION ID'],' DATE:', flight[0]['DATE'])


def removeTicket(ticket_id):
    resp = requests.delete(f'{url4}/{ticket_id}') #send to server to delete ticket with id
    if resp.status_code != 200:
        print('Unexpected error')
        return
    ticket = json.loads(resp.content)
    if ticket==[]: #if ticket empy,bad choice
        print("******** you have input an invalid ticket id ********")
    elif ticket[0]['status']=='delete':
        return True #if server return true ,ticket is delete
    else:
        return False



def removeClient(idClient):
    resp = requests.delete(f'{url}/{idClient}')
    return json.loads(resp.content)
    # send to server to remove user with id

def updateCustomer(idClient):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    names_par = ['full_name', 'password', 'real_id']
    updated_cust = {}
    for par in names_par:
        value = input(f'Please insert {par}: ')
        updated_cust[par] = value
    # input the new user to update and create dictionry
    if not updated_cust['real_id'].isdigit() or len(updated_cust['real_id']) != 9:
        print("id is be 9 numbers")
        #check if id with 9 numbers

#    print('updated_cust: ',json.dumps(updated_cust))
    resp = requests.put(f'{url}/{idClient}', data=json.dumps(updated_cust), headers=headers) #send to server to update user
    return json.loads(resp.content) # server back


def guiFlights(idClient):
    while True:
        print('select what you want')
        print('1. Show all flights ')
        print('2. buy flights  ')
        print('3. print tickets you bought')
        print('4. delete ticket')
        print('5. remove user ')
        print('6. Update user')
        print('0. sign out')
        choice = input("What's your choice? ")
        if not choice.isdigit() or int(choice)>6:
            print('******** bad choice !!!!!!!!- try again ********')
        if choice == "0":
            break; # client want to exit to flight gui
        if choice == "1":
            showFlights() # send to showflight func
        if choice == "2":
            res=buyTicket(idClient) #send to buyticket funct with id user
            if res==2:
                print('******** bad Ticket Id choice !!!!!!!!- try again ********')

        if choice == "3":
            res=printTicket(idClient) #send to printticket function with id user
            if res ==[]: #if res is empty , user not buy ticket
                print(' ')
                print('******** you have not buy any ticket ********')
                continue
        if choice == "4":
            res=printTicket(idClient) # print to the user all tickets and he is need to choice whitch to remove
            if res ==[]:
                print(' ')
                print('******** you have not ticket to remove ********')
                continue

            choiceTicketDelte=input("choice Ticket Id to remove: ")
            res=removeTicket(choiceTicketDelte) #send the removeticket function the ticket user want to remove
            if res==True:
                print('******** the ticket is delete ********')
        if choice == "5":
            res=removeClient(idClient) # send to remove client functiom
            print('delete is ',res['status'])
            break
        if choice == "6":
            res=updateCustomer(idClient) #send to updateCustomer function
            print('update is ',res['status'])
            break


def main():
    init_logger()
    logger.write_lo_log('**************** System started ...', 'INFO')

    test_db_connection()


    while True:
        print('1. Suscribe')#
        print('2. Sign in')
        print('0. Exit')
#        print('3. Show all customers')
#        print('4. Show customer by id')
        choice = input("What's your choice? ")
        if not choice.isdigit() or int(choice)>2:# check if user enter a true value
            print('bad choice !!!!!!!!- try again')
            continue
        if choice == "0":
            break;#user quit
        if choice == "3":
            showAllCustomers()# function that prints all user (only for administrator)
        if choice == "4":
            showCustomer()# function print only 1 user (only for administator)
        if choice == "1":

            names_par = ['full_name', 'password', 'real_id']
            new_cust = {}
            cust = {}

            for par in names_par:
                value = input(f'Please insert {par}: ')
                new_cust[par] = value
                # input from user name ,password and real id and create a dictionary
            if not new_cust['real_id'].isdigit() or len(new_cust['real_id']) != 9: #check the real id is only 9 numbers. if not it is back to the menu
                print("id is be 9 numbers")
            else:
                res=newClient(new_cust)# sendind to newclient function and receive to res

                if res['Error']=='duplicate':
                    print('******** this real id is already use ********')
                    print(' ')
                    continue
                    #if the id already use, the server return word "duplicate" and it is continue and back to menu
                else:
                    #after create account,automatic sign in the user

                    cust['password']=new_cust['password']
                    cust['real_id']=new_cust['real_id']
                    res=signIn(cust)
                    print('*************************')
                    print(f'** Welcome ',res["full_name"],' **')
                    print('*************************')
                    guiFlights(res["ID"])# send the user to the gui flight to buy tikcet

        if choice == "2":
            names_par = ['password', 'real_id']
            new_cust = {}

            for par in names_par:
                value = input(f'Please insert {par}: ')
                new_cust[par] = value
            #input from user password and id for signin

            if not new_cust['real_id'].isdigit() or len(new_cust['real_id']) != 9:# verif if 9 number
                print("id is be 9 numbers")
                continue
            else:
                res=signIn(new_cust)# send to signin function the dictionary and receive the result

            if res==3 :
                print("User not Found")# if signin fun rterurn 3: user enter id that not in database
            elif res==2 :
                print("Unexpected error")# if signin fun rterurn 2: there is an error
            else:
                print('*************************')
                print(f'** Welcome ',res["full_name"],' **')
                print('*************************')
                guiFlights(res["ID"])
                #print the use name and send to guiflight the id user


with open(r'C:\Users\jeremy\Documents\LOGFILE/user_conf.json') as json_file:
    conf = json.load(json_file)
    #open the configuration file
main()
