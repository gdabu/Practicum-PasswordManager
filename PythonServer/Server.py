from socket import *
import thread
import json
import MySQLdb
import random
import bcrypt
from util import *
import ast
import logging
import argparse

from scan import *

from mail import send_email
from ipRules import *

from sys import platform as _platform

def initLogger():

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # create a file handler

    handler = logging.FileHandler('./logs/login.log')
    handler.setLevel(logging.INFO)

    # create a logging format

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger

    logger.addHandler(handler)

    return logger



# TODO: SEND BACK JSON RESPONSES TO CLIENT

def handler(clientsock, addr, db, logger):

    cursor = db.cursor()

    loggedIn = False
    loggedInUser = ""
    # @param attemptedLogUser - the user who is attempting to log in, used for 2FA login
    attemptedLogUser = ""
    failedLoginCount = 0

    

    try:
        while 1:
            
            data = clientsock.recv(4096)
            print data
            # if client disconnects
            if not data:
                print addr, "- Connection Closed"
                break

            # print repr(addr) + " Command: " + data

            # 
            # Command Parser
            # 
            commandData = json.loads(data.rstrip())
            command = commandData['action']

            # 
            # Register
            # 
            if command == "REGISTER":

                try: 
                    
                    plaintextPassword = commandData['password'].encode('utf-8')
                    hashedPassword = bcrypt.hashpw(plaintextPassword, bcrypt.gensalt())
                    # insert registered username and password
                    cursor.execute("insert into users (username, password) values ('" + commandData['username'] + "', '" + hashedPassword + "')")
                    db.commit()
                    sendFormattedJsonMessage(clientsock, "REGISTER", 200, "Registration Successfull", {"username" : commandData['username'], "password" : hashedPassword})

                # catch exception for when username is already taken
                except MySQLdb.IntegrityError, e:
                    
                    # 1062 is the error number for inserting and already existing primary key value.
                    if not e[0] == 1062:
                        sendFormattedJsonMessage(clientsock, "REGISTER", 400, "Registration Unsuccessfull")
                        raise
                    else:
                        sendFormattedJsonMessage(clientsock, "REGISTER", 400, "Registration Unsuccessfull")
                        print "Username already taken"
                        db.rollback()
                
                continue

            # 
            # Register
            # 
            elif command == "LOGIN":

                cursor.execute("select * from users where username = '" + commandData['username'] + "'" )

                user = cursor.fetchall()
                attemptedPassword = commandData['password'].encode('utf-8')
                db.commit()



                
                if len(user) == 0:
                    print "User not found"
                    print "LOGGED SHIT"
                    logger.warn('Login attempt to user: %s from IP %s - Invalid Username', commandData['username'], clientsock.getsockname())
                    logger.warn('Login attempt to user: %s from IP %s - Invalid Username', commandData['username'], clientsock.getsockname())

                    sendFormattedJsonMessage(clientsock, "LOGIN", 400, "LOGIN Unsuccessfull: USER NOT FOUND")
                    failedLoginCount += 1
                else:
                    print "user found"
                    print user
                    for row in user:
                        # print row[1]
                        # print len(row[1])
                        
                        if row[1] == bcrypt.hashpw(attemptedPassword, row[1]):
                            
                            # CHECK FOR 2FA REQUIREMENT
                            if row[2] == 0:
                                
                                loggedIn = True
                                loggedInUser = row[0]
                                print "LOGGED SHIT"
                                logger.info('Login to user: %s from IP %s - Successfull Login', commandData['username'], clientsock.getsockname())
                                sendFormattedJsonMessage(clientsock, "LOGIN", 200, "LOGIN Successfull", {'tfa_enabled':False})
                                failedLoginCount = 0

                            else:
                                # TODO : SEND EMAIL WITH KEY
                                attemptedLogUser = row[0]
                                print "2FA Login Required"
                                secret = random.randint(10000,99999)
                                send_email("devbcit@gmail.com","bastard11", "geoffdabu@gmail.com", "Khaled Keys: 2FA Login Key", secret)
                                cursor.execute("update users set tfa_secret=" + `secret` + " where username='" + row[0] + "'" )
                                db.commit()
                                
                                sendFormattedJsonMessage(clientsock, "LOGIN", 200, "LOGIN Unsuccessfull: 2FA REQUIRED", {'tfa_enabled':True})
                                break

                        else:
                            print "Wrong Password"
                            print "LOGGED SHIT"
                            logger.warn('Login attempt to user: %s from IP %s - Wrong Password', commandData['username'], clientsock.getsockname())
                            sendFormattedJsonMessage(clientsock, "LOGIN", 402, "LOGIN Unsuccessfull: WRONG PASSWORD")
                            failedLoginCount += 1
                        break

                
                # TODO : set failedLoginCount max in config file
                # set block duration in config file
                if failedLoginCount == 5:
                    blockIp(addr[0], 5)

                continue

            # 
            # 2FA_LOGIN
            # 
            # USER should only be able to make a 2FA_LOGIN attempt if they have logged in with a correct user password combo 
            # 
            elif command == "2FA_LOGIN" and attemptedLogUser != "":

                cursor.execute("select * from users where username = '" + attemptedLogUser + "'" )

                user = cursor.fetchall()

                print commandData

                try:
                    for row in user:
                        if row[3] == int(commandData['secret']):
                            loggedIn = True
                            loggedInUser = row[0]
                            logger.warn('Login to user: %s from IP %s - Successfull 2FA Login', loggedInUser, clientsock.getsockname())
                            sendFormattedJsonMessage(clientsock, "2FA_LOGIN", 200, "LOGIN Successfull", {'tfa_enabled':True})
                            break
                        else:
                            logger.warn('Login attempt to user: %s from IP %s - Wrong 2FA key', attemptedLogUser, clientsock.getsockname())
                            sendFormattedJsonMessage(clientsock, "2FA_LOGIN", 404, "LOGIN Unsuccessfull: WRONG SECRET")
                            failedLoginCount += 1
                            break
                except ValueError, e:
                    sendFormattedJsonMessage(clientsock, "ERROR", 900, "LOGIN Unsuccessfull: NAN")


                continue

            # 
            # 2FA_ENABLE
            #
            elif command == "2FA_ENABLE" and loggedIn == True:
                tfa_enabled = 0
                
                if commandData['enabled'] == True:
                    tfa_enabled = 1

                try:

                    cursor.execute("update users set tfa_enabled=" + `tfa_enabled` + " where username='" +loggedInUser+ "'" )
                    db.commit()
                    print "tfa_enabled: " + `tfa_enabled`
                    if tfa_enabled == 1:
                        sendFormattedJsonMessage(clientsock, "2FA_ENABLE", 200, "2Factor Auth Enabled")
                    else:
                        sendFormattedJsonMessage(clientsock, "2FA_ENABLE", 200, "2Factor Auth Disabled")
                
                except error, e:
                    print e
                    db.rollback()
                    sendFormattedJsonMessage(clientsock, "2FA_ENABLE", 400, "2FA_ENABLE Unsuccessfull: Unable to Enable/Disable 2FA")

                continue
            
            # 
            # Login
            # 
            elif command == "SYNC" and loggedIn == True:
                print commandData

                if commandData['subaction'] == "PUSH":
                    cursor.execute("delete from passwords where username='" +loggedInUser+ "'" )
                    pushPasswordData = ast.literal_eval(commandData['passwords'])
                    
                    for password in pushPasswordData:
                        cursor.execute("insert into passwords (username, account, password) values ('" + loggedInUser + "', '" + password['account'] + "', '" + password['password'] + "')" )

                    db.commit()

                    sendFormattedJsonMessage(clientsock, "SYNC", 200, "PUSH Successfull", {'subaction' : commandData['subaction']})

                elif commandData['subaction'] == "PULL":
                    cursor.execute("select * from passwords where username = '" + loggedInUser + "'" )
                    passwords = cursor.fetchall()

                    passwordList = []

                    for row in passwords:
                        passwordList.append({ 
                            "id" : row[0],
                            "username" :  row[1],
                            "account" :  row[2],
                            "password" :  row[3]
                        })

                    print passwordList
                    db.commit()

                    sendFormattedJsonMessage(clientsock, command, 200, "PULL EXECUTED", {'subaction' : commandData['subaction'], 'passwords' : passwordList})
                
                elif commandData['subaction'] == "DIFF":

                    cursor.execute("select * from passwords where username = '" + loggedInUser + "'" )
                    passwords = cursor.fetchall()

                    passwordList = []

                    for row in passwords:
                        passwordList.append({ 
                            "id" : row[0],
                            "username" :  row[1],
                            "account" :  row[2],
                            "password" :  row[3]
                        })

                    print passwordList
                    db.commit()

                    sendFormattedJsonMessage(clientsock, command, 200, "DIFF EXECUTED", {'subaction' : commandData['subaction'], 'passwords' : passwordList})
                else:
                    print "Not a Valid SYNC Command"
                    sendFormattedJsonMessage(clientsock, command, 400, "COMMAND EXECUTED - INVALID", {'subaction' : commandData['subaction']})

                continue

            # 
            # CRUD
            # 
            elif command == "CRUD" and loggedIn == True:

                if commandData['subaction'] == "CREATE":
                    # TODO : DB ERROR HANDLING
                    cursor.execute("insert into passwords (username, account, password) values ('" + loggedInUser + "', '" + commandData['entry']['account'] + "', '" + commandData['entry']['accountPassword'] + "')" )
                    db.commit()

                    print commandData
                    sendFormattedJsonMessage(clientsock, command, 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})

                elif commandData['subaction'] == "READ":

                    cursor.execute("select * from passwords where username = '" + loggedInUser + "'" )
                    passwords = cursor.fetchall()

                    passwordList = []

                    for row in passwords:
                        passwordList.append({ 
                            "id" : row[0],
                            "username" :  row[1],
                            "account" :  row[2],
                            "password" :  row[3]
                        })

                    print passwordList
                    db.commit()

                    sendFormattedJsonMessage(clientsock, command, 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction'], 'passwords' : passwordList})
                    continue

                elif commandData['subaction'] == "UPDATE":
                    try:
                        int(commandData['entry']['id'])
                        pass
                    except ValueError, e:
                        sendFormattedJsonMessage(clientsock, command, 400, "ERROR: INVALID ID", {'subaction' : commandData['subaction']})
                        continue
                    else:
                        pass
                    finally:
                        pass

                    print commandData
                    
                    cursor.execute("update passwords set " + commandData['entry']['column'] + "='" + commandData['entry']['newValue'] + "' where id = " + `int(commandData['entry']['id'])` + " and username = '" + loggedInUser + "'")
                    db.commit()

                    print commandData
                    sendFormattedJsonMessage(clientsock, command, 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})
                
                elif commandData['subaction'] == "DELETE":
                    try:
                        int(commandData['entry']['id'])
                        pass
                    except ValueError, e:
                        sendFormattedJsonMessage(clientsock, command, 400, "ERROR: INVALID ID", {'subaction' : commandData['subaction']})
                        continue
                    else:
                        pass
                    finally:
                        pass

                    cursor.execute("delete from passwords where id = " + `int(commandData['entry']['id'])` + " and username = '" + loggedInUser + "'")
                    db.commit()

                    print commandData
                    sendFormattedJsonMessage(clientsock, command, 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})
                
                else:
                    print "Not a Valid Crud Command"
                    sendFormattedJsonMessage(clientsock, command, 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})

                
                continue

            elif command == "SCAN" and loggedIn == True:
                hosts = getHosts('192.168.0.0/24')
                sendFormattedJsonMessage(clientsock, command, 200, "SUCCESSFUL NETWORK SCAN", {'hosts' : hosts})
                # sendFormattedJsonMessage(clientsock, command, 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})                


            # 
            # NOT LOGGED IN
            # 
            elif (command == "SYNC" or command == "CRUD") and loggedIn == False:
                print addr, "- Not Logged In"
                sendFormattedJsonMessage(clientsock, command, 400, "COMMAND Unsuccessfull: You must be logged in")
                continue

            


            # 
            # Logout
            # 
            elif command == "LOGOUT":
                loggedIn = False
                loggedInUser = ""
                attemptedLogUser = ""
                print addr, " - Logged Out"
                break;

            # 
            # Invalid Command
            #
            else:
                sendFormattedJsonMessage(clientsock, "ERROR", 901, "Not A Valid Command")
                print "not a command"
                continue

        clientsock.close()

    except error, e:
        print "Socket error"
    finally: 
        clientsock.close()

if __name__=='__main__':

    cmdParser = argparse.ArgumentParser(description="8505A1-CovertChannel Client")
    cmdParser.add_argument('-i','--IP',dest='IP', help='HOST Ip', required=True)
    cmdParser.add_argument('-p','--PORT',dest='PORT', help='HOST Port', required=True)
    args = cmdParser.parse_args();


    ADDR = (args.IP, int(args.PORT))
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)

    if _platform == "darwin":
        dbpassword = ""
    else:
        dbpassword = "bastard11"


    db = MySQLdb.connect(host="localhost", user="root", passwd="", db="pwd_manager")
    logger = initLogger()

    while 1:
        print '>> Server Listening on Port: ', args.PORT
        clientsock, addr = serversock.accept()
        print '>> Connected to: ', addr
        thread.start_new_thread(handler, (clientsock, addr, db, logger))