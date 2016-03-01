from socket import *
import thread
import json
import MySQLdb
import random
from util import *

HOST = '192.168.0.28'# must be input parameter @TODO
PORT = 8000 # must be input parameter @TODO


# TODO: SEND BACK JSON RESPONSES TO CLIENT

def handler(clientsock, addr, db):

    cursor = db.cursor()
    loggedIn = False

    loggedInUser = ""
    attemptedLogUser = ""

    try:
        while 1:

            data = clientsock.recv(4096)

            # if client disconnects
            if not data:
                print addr, "- Connection Closed"
                break

            # print repr(addr) + " Command: " + data

            # 
            # Command Parser
            # 
            commandData = json.loads(data.rstrip());
            command = commandData['action']

            # 
            # Register
            # 
            if command == "REGISTER":


                try: 
                    
                    # insert registered username and password
                    cursor.execute("insert into users (username, password) values ('" + commandData['username'] + "', '" + commandData['password'] + "')")
                    db.commit()
                    clientsock.sendall("Registration Successfull")

                # catch exception for when username is already taken
                except MySQLdb.IntegrityError, e:
                    
                    # 1062 is the error number for inserting and already existing primary key value.
                    if not e[0] == 1062:
                        clientsock.sendall("Registration Unsuccessfull")
                        raise
                    else:
                        clientsock.sendall("Registration Unsuccessfull: Username already taken")
                        print "Username already taken"
                        db.rollback()
                continue

            # 
            # Register
            # 
            elif command == "LOGIN":

                cursor.execute("select * from users where username = '" + commandData['username'] + "'" )

                user = cursor.fetchall()

                if len(user) == 0:
                    print "User not found"
                    clientsock.sendall("LOGIN Unsuccessfull")
                else:
                    print "user found"
                    for row in user:
                        if row[1] == commandData['password']:
                            if row[2] == 0:
                                
                                loggedIn = True
                                loggedInUser = row[0]
                                sendFormattedJsonMessage(clientsock, "LOGIN", 200, "LOGIN Successfull", {'tfa_enabled':'FALSE'})
                            else:
                                
                                attemptedLogUser = row[0]
                                print "2FA Login Required"
                                secret = random.randint(10000,99999)
                                cursor.execute("update users set tfa_secret=" + `secret` + " where username='" + row[0] + "'" )
                                db.commit()
                                

                                # TODO: SEND CLIENT 2FA PROMPT
                                sendFormattedJsonMessage(clientsock, "LOGIN", 401, "LOGIN Unsuccessfull: 2FA REQUIRED", {'tfa_enabled':'TRUE'})
                            

                        else:
                            print "Wrong Password"
                            sendFormattedJsonMessage(clientsock, "LOGIN", 402, "LOGIN Unsuccessfull: WRONG PASSWORD")
                        break
                continue

            # 
            # 2FA_LOGIN
            # 
            elif command == "2FA_LOGIN":
                cursor.execute("select * from users where username = '" + attemptedLogUser + "'" )

                user = cursor.fetchall()

                for row in user:
                    print row[3]
                    print commandData['secret']
                    if row[3] == commandData['secret']:
                        loggedIn = True
                        loggedInUser = row[0]
                        sendFormattedJsonMessage(clientsock, "2FA_LOGIN", 200, "LOGIN Successfull", {'tfa_enabled':'TRUE'})
                        break
                    else:
                        sendFormattedJsonMessage(clientsock, "2FA_LOGIN", 404, "LOGIN Unsuccessfull: WRONG SECRET")
                        break
                continue



            # 
            # 2FA_ENABLE
            #
            elif command == "2FA_ENABLE" and loggedIn == True:
                tfa_enabled = 0
                
                if commandData['enabled'] == "TRUE":
                    tfa_enabled = 1

                try:
                    cursor.execute("update users set tfa_enabled=" + `tfa_enabled` + " where username='" +loggedInUser+ "'" )
                    db.commit()
                    if tfa_enabled == 0:
                        clientsock.sendall("2fa disabled")
                    else:
                        clientsock.sendall("2fa enabled")
                except error, e:
                    print e
                    db.rollback()
                    clientsock.sendall("2fa was not enabled/disabled")

                continue

            
            # 
            # Login
            # 
            elif data.rstrip() == "SYNC" and loggedIn == True:
                clientsock.sendall(data)
                continue

            # 
            # CRUD
            # 
            elif data.rstrip() == "CRUD" and loggedIn == True:
                clientsock.sendall(data)
                continue

            # 
            # NOT LOGGED IN
            # 
            elif (data.rstrip() == "SYNC" or data.rstrip() == "CRUD") and loggedIn == False:
                print addr, "- Not Logged In"
                clientsock.sendall(data)
                continue

            # 
            # Logout
            # 
            elif command == "LOGOUT" and loggedIn == True:
                loggedIn = False
                print addr, " - Logged Out"
                break;

            # 
            # Invalid Command
            # 
            else:
                clientsock.sendall(data)
                print "not a command"
                continue

        clientsock.close()

    except error, e:
        print "Socket error"
    finally: 
        clientsock.close()

if __name__=='__main__':
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)

    db = MySQLdb.connect(host="localhost", user="root", passwd="bastard11", db="pwd_manager")

    while 1:
        print '>> Server Listening on Port: ', PORT
        clientsock, addr = serversock.accept()
        print '>> Connected to: ', addr
        thread.start_new_thread(handler, (clientsock, addr, db))