import sys
import socket
import sys
import json
import bcrypt
import MySQLdb
import ast

# 
# Online Handler for all remote activity
# 
def onlineHandler(sock, db):

    commandData = ""
    loggedIn = False
    passwordList = []
    attemptedLogUser = ""
    loggedInUser = ""

    cursor = db.cursor()

    try:
        while 1:

            # send command
            command = raw_input('Enter Command: ')
            
            if command == "LOGIN":
                userName = raw_input('Enter User Name: ')
                userPassword = raw_input('Enter Password: ')
                attemptedLogUser = userName
                commandData = json.dumps({"action" : "LOGIN", "username":userName, "password":userPassword})
                sock.sendall(commandData)


            elif command == "REGISTER": 
                userName = raw_input('Enter User Name: ')
                userPassword = raw_input('Enter Password: ')
                commandData = json.dumps({"action" : "REGISTER", "username":userName, "password":userPassword})   
                sock.sendall(commandData)

            elif command == "2FA_ENABLE" and loggedIn == True:
                while True:
                    enabled = raw_input('Enable 2FA [True/FALSE/CANCEL]:')
                    if enabled == "True" or enabled == "FALSE":
                        commandData = json.dumps({"action" : "2FA_ENABLE", "enabled" : enabled})
                        sock.sendall(commandData)
                        break
                    elif enabled == "CANCEL":
                        break
                    else:
                        print "Invalid Option"

            elif command == "SYNC" and loggedIn == True:

                syncCommand = raw_input('Enter SYNC Command [PUSH/PULL/DIFF]: ')

                if syncCommand == "PUSH":
                    print loggedInUser
                    cursor.execute("select * from passwords where username = '" + loggedInUser + "'" )
                    passwords = cursor.fetchall()
                    print passwords
                    passwordList = []

                    for row in passwords:
                        passwordList.append({
                            "id" : row[0],
                            "username" :  row[1],
                            "account" :  row[2],
                            "password" :  row[3]
                        })

                    print "PASSWORD LIST:" + str(passwordList)
                    db.commit()
                    commandData = json.dumps({"action" : "SYNC", "subaction" : "PUSH", "passwords" : str(passwordList)})

                elif syncCommand == "PULL":
                    commandData = json.dumps({"action" : "SYNC", "subaction" : "PULL"})
                elif syncCommand == "DIFF":
                    commandData = json.dumps({"action" : "SYNC", "subaction" : "DIFF"})
                else:
                    print "Invalid Sync Command"
                    continue

                
                sock.sendall(commandData)


            elif command == "CRUD" and loggedIn == True:

                crudCommand = raw_input('Enter CRUD Command [CREATE/READ/UPDATE/DELETE]: ')

                if crudCommand == "CREATE":
                    account = raw_input('Enter Account Name: ')
                    accountPassword = raw_input('Enter Password: ')
                    commandData = json.dumps({"action" : "CRUD", "subaction" : "CREATE", "entry" : {"account" : account, "accountPassword" : accountPassword}})
                    print crudCommand

                elif crudCommand == "READ":
                    
                    commandData = json.dumps({"action" : "CRUD", "subaction" : "READ"})
                    print crudCommand

                elif crudCommand == "UPDATE":
                    
                    entryId = raw_input('Enter Entry ID Number: ')
                    column = raw_input('Which value would you like to change [account/password]: ')
                    newValue = raw_input('Enter new Value: ')

                    if column != "account" and column != "password":
                        print "You can only change account or password"
                        continue

                    commandData = json.dumps({"action" : "CRUD", "subaction" : "UPDATE", "entry" : {"id" : entryId, "column" : column, "newValue" : newValue}})
                    print crudCommand

                elif crudCommand == "DELETE":

                    entryId = raw_input('Enter Entry ID Number: ')
                    commandData = json.dumps({"action" : "CRUD", "subaction" : "DELETE", "entry" : {"id" : entryId}})
                    print crudCommand

                else:
                    print "Invalid CRUD command - ", crudCommand
                    continue

                sock.sendall(commandData)

            elif command == "LOGOUT":
                loggedIn = False
                passwordList = []
                commandData = json.dumps({"action" : "LOGOUT"});
                sock.sendall(commandData)
                
            else:
                print "Not A VALID Command"
                continue



            # recv response 
            while 1:
                
                # get data
                data = sock.recv(4096)

                if not data:
                    print 'Server Connection Terminated: Closing Socket'
                    sock.close()
                    return

                try:
                    respData = json.loads(data.rstrip());
                    response = respData['action']

                    if response == "LOGIN":
                        
                        # 200 STATUS CODE MEANS SUCCESSFULL LOGIN
                        if respData['status'] == 200:    

                            # CHECK FOR 2FA REQUIREMENT
                            if respData['additional']['tfa_enabled'] == "True":
                                print respData['message']

                                secret = raw_input('Enter 2FA Secret :')
                                commandData = json.dumps({"action" : "2FA_LOGIN", "secret" : secret})
                                sock.sendall(commandData)

                                # Since we just sent a message, continue to remain
                                # in listening loop
                                continue
                            
                            # IF 2FA IS NOT REQUIRED THEN YOUVE LOGGED IN SUCCESSFULLY
                            else:
                                # LOGGED IN SUCCESSFULLY
                                # TODO : upon successfull login make READ request
                                print respData['message']
                                loggedInUser = attemptedLogUser
                                loggedIn = True                
                        
                        else:
                            # unsuccessful login
                            print respData['message']
                        
                    elif response == "2FA_LOGIN":
                        if respData['status'] == 200:
                            # successfull login
                            print "SUCCESSFULLY LOGGED IN"
                            print respData["message"]
                            loggedInUser = attemptedLogUser
                            loggedIn = True

                            # TODO : upon successfull login make READ request

                        else:
                            print "UNSUCCESSFULL LOG IN"

                    elif response == "ERROR":
                        print respData["message"]

                    elif response == "REGISTER":
                        if respData['status'] == 200:
                            cursor.execute("insert into users (username, password) values ('" + respData['additional']['username'] + "', '" + respData['additional']['password'] + "')")
                            db.commit()

                            
                            
                        print respData['message']


                    elif response == "2FA_ENABLE":
                        print respData['message']

                    elif response == "SYNC":
                        if respData['additional']['subaction'] == "PUSH":
                            print respData['message']

                        elif respData['additional']['subaction'] == "PULL":
                            print respData['message']
                            respData['additional']['passwords']

                            cursor.execute("delete from passwords where username='" +loggedInUser+ "'" )
                            pushPasswordData = ast.literal_eval(respData['additional']['passwords'])
                            
                            for password in pushPasswordData:
                                cursor.execute("insert into passwords (username, account, password) values ('" + loggedInUser + "', '" + password['account'] + "', '" + password['password'] + "')" )

                            db.commit()

                        elif respData['additional']['subaction'] == "DIFF":
                            print respData['message']
                            cursor.execute("select * from passwords where username = '" + loggedInUser + "'" )
                            passwords = cursor.fetchall()
                            print passwords
                            passwordList = []

                            for row in passwords:
                                passwordList.append({
                                    "id" : row[0],
                                    "username" :  row[1],
                                    "account" :  row[2],
                                    "password" :  row[3]
                                })

                            print "LOCAL PASSWORD LIST:\n\n" + str(passwordList)
                            db.commit()

                            print "SERVER PASSWORD LIST\n\n" + respData['additional']['passwords']

                        else:
                            print "not a valid command"

                    # TODO : prevent user from performing crud if not logged in 
                    elif response == "CRUD":

                        if respData['additional']['subaction'] == "READ":

                            passwordList = ast.literal_eval(respData['additional']['passwords'])

                            for password in passwordList:
                                 print password

                        elif respData['additional']['subaction'] == "CREATE":
                            print respData
                            
                        elif respData['additional']['subaction'] == "DELETE":
                            print respData
                        elif respData['additional']['subaction'] == "UPDATE":
                            print respData
                        else:
                            print "not a valid command"

                    else:
                        print "Not A Valid Response"
                    # LEAVE LISTENING LOOP
                    break

                except ValueError, e:
                    print "Not returning JSON"
                    
    except socket.error, e:
        print "Raised Socket Exception: ", e

    finally:
        loggedIn = False
        sock.close()

# 
# Offline Handler for all local activity
# 
def offlineHandler(db):

    cursor = db.cursor()
    loggedIn = False
    loggedInUser = ""

    while 1:

        # send command
        command = raw_input('Enter Command: ')
        
        if command == "LOGIN":
            userName = raw_input('Enter User Name: ')
            userPassword = raw_input('Enter Password: ')

            cursor.execute("select * from users where username = '" + userName + "'")
            user = cursor.fetchall()

            if len(user) == 0:
                print "User not found"
            else:
                for row in user:
                    if row[1] == bcrypt.hashpw(userPassword, row[1]):
                        print "LOGGED IN SUCCESSFULLY"
                        loggedIn = True
                        loggedInUser = row[0]
                    else:
                        print "Wrong Password"
                    break
            continue

        elif command == "CRUD" and loggedIn == True:
            # TODO: CRUD
            # 
            # 
        
            crudCommand = raw_input('Enter CRUD Command [CREATE/READ/UPDATE/DELETE]: ')

            if crudCommand == "CREATE":
                account = raw_input('Enter Account Name: ')
                accountPassword = raw_input('Enter Password: ')
                
                cursor.execute("insert into passwords (username, account, password) values ('" + loggedInUser + "', '" + account + "', '" + accountPassword + "')" )
                db.commit()

                print crudCommand

            elif crudCommand == "READ":
                
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

                print crudCommand

            elif crudCommand == "UPDATE":
                
                entryId = raw_input('Enter Entry ID Number: ')
                column = raw_input('Which value would you like to change [account/password]: ')
                newValue = raw_input('Enter new Value: ')

                if column != "account" and column != "password":
                    print "You can only change account or password"
                    continue

                try:
                    int(entryId)
                    pass
                except ValueError, e:
                    sendFormattedJsonMessage(clientsock, command, 400, "ERROR: INVALID ID", {'subaction' : commandData['subaction']})
                    continue
                else:
                    pass
                finally:
                    pass

                
                print "update passwords set `" + column + "`=`" + newValue + "` where id = " + `entryId` + " and username = '" + loggedInUser + "'"
                cursor.execute("update passwords set " + column + "='" + newValue + "' where id = " + `entryId` + " and username = '" + loggedInUser + "'")
                db.commit()

                print crudCommand

            elif crudCommand == "DELETE":

                entryId = raw_input('Enter Entry ID Number: ')
                
                print crudCommand
                try:
                    int(entryId)
                    pass
                except ValueError, e:
                    sendFormattedJsonMessage(clientsock, command, 400, "ERROR: INVALID ID", {'subaction' : commandData['subaction']})
                    continue
                else:
                    pass
                finally:
                    pass

                cursor.execute("delete from passwords where id = " + `entryId` + " and username = '" + loggedInUser + "'")
                db.commit()

            else:
                print "Invalid CRUD command - ", crudCommand
                continue
            
            continue

        elif command == "LOGOUT" and loggedIn == True:
            loggedIn = False
            loggedInUser = ""

            print "Exiting Program. Bye!"
            sys.exit()

        else:
            print "not a command"
            continue

if __name__=='__main__':

    db = MySQLdb.connect(host="localhost", user="root", passwd="bastard11", db="pwd_manager")

    connection = raw_input("Make Connection [ONLINE/OFFLINE]:")

    try:

        if connection == "ONLINE":

            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('192.168.0.28', 8000)
            print 'connecting to %s port %s' % server_address
            clientSocket.connect(server_address)
            onlineHandler(clientSocket, db)

        elif connection == "OFFLINE":
            offlineHandler(db)

        else:
            sys.exit()

    except socket.error, e:
        print "Raised Socket Exception: ", e
        print "Could"
        offlineHandler(db)



