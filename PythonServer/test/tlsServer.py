#server side
# echo client
from socket import *
from ssl import *

#create socket
server_socket=socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

#Bind to an unused port on the local machine
server_socket.bind(('192.168.0.6',8000))

#listen for connection
server_socket.listen (1)
tls_server = wrap_socket(server_socket, ssl_version=PROTOCOL_TLSv1, cert_reqs=CERT_NONE, server_side=True, keyfile='./key.pem', certfile='./cert.pem')

print('server started')

#accept connection
connection, client_address= tls_server.accept()
print ('connection from', client_address)

#server is not finnished
finnished =False

#while not finnished
while not finnished:


    #send and receive data from the client socket
    data_in=connection.recv(1024)
    message=data_in.decode()
    print('client send',message)

    if message=='quit':
        finnished= True
    else:

        data_out=message.encode()
        connection.send(data_out)

#close the connection
connection.shutdown(SHUT_RDWR)
connection.close()

#close the server socket
server_socket.shutdown(SHUT_RDWR)
server_socket.close()