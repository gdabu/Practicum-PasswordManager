from socket import *
import thread
import json
import MySQLdb

HOST = '192.168.0.28'# must be input parameter @TODO
PORT = 8000 # must be input parameter @TODO

testUser = "test"
testPassword = "test"

def handler(clientsock, addr, db):

    cursor = db.cursor()
    loggedIn = True

    loggedInUser = "test"

    try:
        while 1:

            data = clientsock.recv(4096)

            # if client disconnects
            if not data:
                print addr, "- Connection Closed"
                break

            print repr(addr) + " Command: " + data

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
                            print "Login Successfull"
                            loggedIn = True
                            loggedInUser = row[0]
                            clientsock.sendall("LOGIN Successfull")
                        else:
                            print "Wrong Password"
                            clientsock.sendall("LOGIN Unsuccessfull")
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
                    if tfa_enabled 
                    clientsock.sendall("2fa enabled/disabled")
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