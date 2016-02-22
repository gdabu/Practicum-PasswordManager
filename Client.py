import socket
import sys
import json


def clientHandler():

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
                commandData = json.dumps({"action" : "REGISTER", "username":userName, "password":userPassword});   
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

                print len(data)

                if not data:
                    print 'Server Connection Terminated: Closing Socket'
                    sock.close()
                    return

                if data.rstrip() == "END":
                    break

                if data: 
                    print 'Received Response: %s' % data
                    break


    except socket.error, e:
        print "Raised Socket Exception: ", e

    finally:
        sock.close()


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
try:
    server_address = ('localhost', 8000)
    print 'connecting to %s port %s' % server_address
    sock.connect(server_address)
    clientHandler()

except socket.error, e:
    print "Raised Socket Exception: ", e
    print "Connecting to local db"



