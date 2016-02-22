from socket import *
import thread
import json

HOST = 'localhost'# must be input parameter @TODO
PORT = 8000 # must be input parameter @TODO

testUser = "test"
testPassword = "test"

def handler(clientsock, addr):

    loggedIn = False
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
            
            if command == "REGISTER":
                clientsock.sendall(data)

            elif command == "LOGIN":
                
                if commandData['username'] == "test" and commandData['password'] == "test":
                    loggedIn = True
                    clientsock.sendall("LOGIN Successfull")
                else:
                    clientsock.sendall("LOGIN Unsuccessfull")
            
            elif data.rstrip() == "SYNC" and loggedIn == True:
                clientsock.sendall(data)

            elif data.rstrip() == "CRUD" and loggedIn == True:
                clientsock.sendall(data)

            elif (data.rstrip() == "SYNC" or data.rstrip() == "CRUD") and loggedIn == False:
                print addr, "- Not Logged In"
                clientsock.sendall(data)


            elif command == "LOGOUT" and loggedIn == True:
                loggedIn = False
                print addr, " - Logged Out"
                break;

            else:
                clientsock.sendall(data)
                print "not a command"

        clientsock.close()


    except socket.error:
        print "Socket error"
        clientsock.close()
    except KeyboardInterrupt:
        print "00000000"
    finally: 
        clientsock.close()

if __name__=='__main__':
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)


    while 1:
        print '>> Server Listening on Port: ', PORT
        clientsock, addr = serversock.accept()
        print '>> Connected to: ', addr
        thread.start_new_thread(handler, (clientsock, addr))