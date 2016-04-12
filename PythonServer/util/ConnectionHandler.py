import json
import MySQLdb
import random
import bcrypt
import ast

from socket import *
from ssl import *

from scan import *
from ipRules import *
from log import *
from mail import send_email
from PasswordCrud import *


netscan = '142.232.169.0/24'


def tlsReceive(clientsock, bufferSize):
    chunk = ""
    data = ""
    
    while 1:
        
        chunk = clientsock.recv(bufferSize)
        data += chunk
        
        if not data or chunk[len(chunk) - 1] == "\n":
            return data.decode()

def sendFormattedJsonMessage(clientsock, action, status, message, additional = {}):
    
    json.dumps(additional)

    sendMessage = json.dumps({"action" : action, "status" : status, "message" : message, "additional" :  additional})
    sendMessage = sendMessage.encode()
    clientsock.sendall(sendMessage + "\n")

    return sendMessage

def handler(clientsock, addr, db, logger):

    cursor = db.cursor()

    loggedIn = False
    loggedInUser = ""
    # @param attemptedLogUser - the user who is attempting to log in, used for 2FA login
    attemptedLogUser = ""
    failedLoginCount = 0

    try:
        while 1:
            
            data = tlsReceive(clientsock, 4096)
            
            # if client disconnects
            if not data:
                print addr, "- Connection Closed"
                break

            
            commandData = json.loads(data.rstrip())
            print data
            # 
            # Register
            # 
            if commandData['action'] == "REGISTER":

                try: 
                    
                    plaintextPassword = commandData['password'].encode('utf-8')
                    hashedPassword = bcrypt.hashpw(plaintextPassword, bcrypt.gensalt())
                    # insert registered username and password
                    # cursor.execute("insert into users (username, password) values ('" + commandData['username'] + "', '" + hashedPassword + "')")
                    # db.commit()
                    UserCreate(db, commandData['username'], hashedPassword)
                    sendFormattedJsonMessage(clientsock, "REGISTER", 200, "Registration Successfull", {"username" : commandData['username'], "password" : hashedPassword})

                # catch exception for when username is already taken
                except MySQLdb.IntegrityError, e:
                    
                    # 1062 is the error number for inserting and already existing primary key value.
                    if not e[0] == 1062:
                        sendFormattedJsonMessage(clientsock, "REGISTER", 400, "Registration Unsuccessfull")
                        raise
                    else:
                        sendFormattedJsonMessage(clientsock, "REGISTER", 401, "Registration Unsuccessfull")
                        print "Username already taken"
                        db.rollback()
                continue

            # 
            # Register
            # 
            elif commandData['action'] == "LOGIN":

                # cursor.execute("select * from users where username = '" + commandData['username'] + "'" )
                # user = cursor.fetchall()
                # db.commit()

                attemptedUser = GetUser(db, commandData['username'])
                attemptedPassword = commandData['password'].encode('utf-8')
                
                                
                if len(attemptedUser) == 0:
                    logger.warn('Login attempt to user: %s from IP %s - Invalid Username', commandData['username'], clientsock.getsockname())
                    sendFormattedJsonMessage(clientsock, "LOGIN", 400, "LOGIN Unsuccessfull: USER NOT FOUND")
                    failedLoginCount += 1

                else:
                    # print "user found"
                    # print user
                    # for attemptedUser[0] in user:
                        # print attemptedUser[0][1]
                        # print len(attemptedUser[0][1])
                        
                    if attemptedUser[0][1] == bcrypt.hashpw(attemptedPassword, attemptedUser[0][1]):
                        
                        # CHECK FOR 2FA REQUIREMENT
                        if attemptedUser[0][2] == 0:
                            
                            loggedIn = True
                            loggedInUser = attemptedUser[0][0]
                            print "LOGGED SHIT"
                            logger.info('Login to user: %s from IP %s - Successfull Login', commandData['username'], clientsock.getsockname())
                            sendFormattedJsonMessage(clientsock, "LOGIN", 200, "LOGIN Successfull", {'tfa_enabled':False})
                            failedLoginCount = 0

                        else:
                            print "2FA Login Required"

                            attemptedLogUser = attemptedUser[0][0]
                            secret = random.randint(10000,99999)
                            send_email("devbcit@gmail.com","bastard11", "geoffdabu@gmail.com", "Khaled Keys: 2FA Login Key", secret)
                            
                            cursor.execute("update users set tfa_secret=" + `secret` + " where username='" + attemptedUser[0][0] + "'" )
                            db.commit()
                            
                            sendFormattedJsonMessage(clientsock, "LOGIN", 200, "LOGIN Unsuccessfull: 2FA REQUIRED", {'tfa_enabled':True})
                            # break

                    else:
                        print "Wrong Password"
                        print "LOGGED SHIT"
                        logger.warn('Login attempt to user: %s from IP %s - Wrong Password', commandData['username'], clientsock.getsockname())
                        sendFormattedJsonMessage(clientsock, "LOGIN", 402, "LOGIN Unsuccessfull: WRONG PASSWORD")
                        failedLoginCount += 1
                        # break

                
                # TODO : set failedLoginCount max in config file
                # set block duration in config file
                if failedLoginCount == 5:
                    logger.warn('Blocking IP: %s', clientsock.getsockname())
                    blockIp(addr[0], 5)

                continue

            # 
            # 2FA_LOGIN
            # 
            # USER should only be able to make a 2FA_LOGIN attempt if they have logged in with a correct user password combo 
            # 
            elif commandData['action'] == "2FA_LOGIN" and attemptedLogUser != "":

                # cursor.execute("select * from users where username = '" + attemptedLogUser + "'" )

                # user = cursor.fetchall()

                attemptedUser = GetUser(db, attemptedLogUser)

                try:
                    if attemptedUser[0][3] == int(commandData['secret']):
                        loggedIn = True
                        loggedInUser = attemptedUser[0][0]
                        logger.warn('Login to user: %s from IP %s - Successfull 2FA Login', loggedInUser, clientsock.getsockname())
                        sendFormattedJsonMessage(clientsock, "2FA_LOGIN", 200, "LOGIN Successfull", {'tfa_enabled':True})
                        
                    else:
                        logger.warn('Login attempt to user: %s from IP %s - Wrong 2FA key', attemptedLogUser, clientsock.getsockname())
                        sendFormattedJsonMessage(clientsock, "2FA_LOGIN", 404, "LOGIN Unsuccessfull: WRONG SECRET")
                        failedLoginCount += 1
                        
                except ValueError, e:
                    print e
                    sendFormattedJsonMessage(clientsock, "ERROR", 900, "LOGIN Unsuccessfull: NAN")


                continue

            # 
            # 2FA_ENABLE
            #
            elif commandData['action'] == "2FA_ENABLE" and loggedIn == True:
                # tfa_enabled = 0
                tfa_status = ""
                if commandData['enabled'] == True:
                    tfa_enabled = 1
                    tfa_status = "Enabled"
                else:
                    tfa_enabled = 0
                    tfa_status = "Disabled"

                try:

                    cursor.execute("update users set tfa_enabled=" + `tfa_enabled` + " where username='" +loggedInUser+ "'" )
                    db.commit()
                    sendFormattedJsonMessage(clientsock, "2FA_ENABLE", 200, "2Factor Auth " + tfa_status)
                        
                except MySQLdb.Error as e:
                    print e
                    db.rollback()
                    sendFormattedJsonMessage(clientsock, "2FA_ENABLE", 400, "2FA_ENABLE Unsuccessfull: Unable to Enable/Disable 2FA")
                    
                    
                    

                continue
            
            # 
            # Login
            # 
            elif commandData['action'] == "SYNC" and loggedIn == True:
                
                
                if commandData['subaction'] == "PUSH":
                    
                    PasswordDeleteAll(db, loggedInUser)
                    PasswordsCreate(db, loggedInUser, ast.literal_eval(commandData['passwords']))
                    sendFormattedJsonMessage(clientsock, "SYNC", 200, "PUSH Successfull", {'subaction' : commandData['subaction']})

                elif commandData['subaction'] == "PULL":
                    
                    passwordList = PasswordRead(db, loggedInUser)
                    sendFormattedJsonMessage(clientsock, commandData['action'], 200, "PULL EXECUTED", {'subaction' : commandData['subaction'], 'passwords' : passwordList})
                
                elif commandData['subaction'] == "DIFF":

                    passwordList = PasswordRead(db, loggedInUser)
                    sendFormattedJsonMessage(clientsock, commandData['action'], 200, "DIFF EXECUTED", {'subaction' : commandData['subaction'], 'passwords' : passwordList})

                else:

                    print "Not a Valid SYNC Command"
                    sendFormattedJsonMessage(clientsock, commandData['action'], 400, "COMMAND EXECUTED - INVALID", {'subaction' : commandData['subaction']})

                continue

            # 
            # CRUD
            # 
            elif commandData['action'] == "CRUD" and loggedIn == True:

                if commandData['subaction'] == "CREATE":
                    
                    PasswordCreate(db, loggedInUser, commandData['entry']['account'], commandData['entry']['accountPassword'])
                    sendFormattedJsonMessage(clientsock, commandData['action'], 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})

                elif commandData['subaction'] == "READ":
                    
                    passwordList = PasswordRead(db, loggedInUser)
                    sendFormattedJsonMessage(clientsock, commandData['action'], 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction'], 'passwords' : passwordList})

                elif commandData['subaction'] == "UPDATE":

                    try:
                        PasswordUpdate(db, loggedInUser, commandData['entry']['column'], commandData['entry']['newValue'], `int(commandData['entry']['id'])`)                    
                    except ValueError, e:
                        print e
                        sendFormattedJsonMessage(clientsock, commandData['action'], 400, "ERROR: INVALID ID", {'subaction' : commandData['subaction']}) 
                    else:
                        print e
                        sendFormattedJsonMessage(clientsock, commandData['action'], 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})
                
                elif commandData['subaction'] == "DELETE":

                    try:
                        PasswordDelete(db, loggedInUser, `int(commandData['entry']['id'])`)
                    except ValueError, e:
                        print e
                        sendFormattedJsonMessage(clientsock, commandData['action'], 400, "ERROR: INVALID ID", {'subaction' : commandData['subaction']})
                    else:
                        sendFormattedJsonMessage(clientsock, commandData['action'], 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})
                
                else:

                    print "Not a Valid Crud Command"
                    sendFormattedJsonMessage(clientsock, commandData['action'], 200, "COMMAND EXECUTED", {'subaction' : commandData['subaction']})

                continue
            
            # 
            # SCAN
            # 
            elif commandData['action'] == "SCAN" and loggedIn == True:

                hosts = getHosts(netscan)
                sendFormattedJsonMessage(clientsock, commandData['action'], 200, "SUCCESSFUL NETWORK SCAN", {'hosts' : hosts})
                
            # 
            # NOT LOGGED IN
            # 
            elif (commandData['action'] == "SYNC" or commandData['action'] == "CRUD") and loggedIn == False:
                print addr, "- Not Logged In"
                sendFormattedJsonMessage(clientsock, commandData['action'], 400, "COMMAND Unsuccessfull: You must be logged in")
                continue
            
            # 
            # Logout
            # 
            elif commandData['action'] == "LOGOUT":
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
        print e
        print "Socket error"

    finally: 
        clientsock.close()