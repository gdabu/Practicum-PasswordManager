import socket
import sys
import json


def onlineHandler(sock):

    commandData = ""

    try:
        while 1:

            # send command
            command = raw_input('Enter Command: ')
            
            if command == "LOGIN":
                userName = raw_input('Enter User Name: ')
                userPassword = raw_input('Enter Password: ')
                commandData = json.dumps({"action" : "LOGIN", "username":userName, "password":userPassword})
                sock.sendall(commandData)

            elif command == "REGISTER": 
                userName = raw_input('Enter User Name: ')
                userPassword = raw_input('Enter Password: ')
                commandData = json.dumps({"action" : "REGISTER", "username":userName, "password":userPassword})   
                sock.sendall(commandData)

            elif command == "2FA_ENABLE":
                while True:
                    enabled = raw_input('Enable 2FA [TRUE/FALSE/CANCEL]:')
                    if enabled == "TRUE" or enabled == "FALSE":
                        commandData = json.dumps({"action" : "2FA_ENABLE", "enabled" : enabled})
                        sock.sendall(commandData)
                        break
                    elif enabled == "CANCEL":
                        break
                    else:
                        print "Invalid Option"

            elif command == "SYNC":
                commandData = json.dumps({"action" : "SYNC"})
                sock.sendall(commandData)

            elif command == "CRUD":
                commandData = json.dumps({"action" : "CRUD"})
                sock.sendall(commandData)

            elif command == "LOGOUT":
                commandData = json.dumps({"action" : "LOGOUT"});
                sock.sendall(commandData)
                
            else:
                print "Not A Command"
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
                        
                        if respData['status'] == 200:    

                            if respData['additional']['tfa_enabled'] == "TRUE":
                                print respData['message']

                                secret = raw_input('Enter 2FA Secret :')
                                commandData = json.dumps({"action" : "2FA_LOGIN", "secret" : secret})
                                sock.sendall(commandData)

                                # Since we just sent a message, continue to remain
                                # in listening loop
                                continue
                            
                            else:
                                print respData['message']                
                        
                        else:
                            print respData['message']
                        
                    elif response == "2FA_LOGIN":
                        print respData["message"]

                    elif response == "ERROR":
                        print respData["message"]

                    elif response == "REGISTER":
                        print respData['message']

                    elif response == "2FA_ENABLE":
                        print respData['message']

                    elif response == "SYNC":
                        print respData['message']

                    elif response == "CRUD":
                        print respData['message']

                    # LEAVE LISTENING LOOP
                    break

                except ValueError, e:
                    print "Not returning JSON"
                    



    except socket.error, e:
        print "Raised Socket Exception: ", e

    finally:
        sock.close()

def offlineHandler():
    print "Connecting to local db"


# Create a TCP/IP socket


# Connect the socket to the port where the server is listening
try:
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('142.232.169.29', 8000)
    print 'connecting to %s port %s' % server_address
    clientSocket.connect(server_address)
    onlineHandler(clientSocket)

except socket.error, e:
    print "Raised Socket Exception: ", e
    offlineHandler()



