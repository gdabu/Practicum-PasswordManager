import json
# 
# a helper function which sends formatted json through a socket.
# 
# @param clientsock - the client socket
# @param action - The action that was requested by the client
# @param status - An int which represents the pass/fail status of the server operation
# @param message - A String describing the status of the server operation 
# @param additional - JSON String of any additional fields that are to be sent
# 
# 
# 
def sendFormattedJsonMessage(clientsock, action, status, message, additional = {}):
    
    # used 
    json.dumps(additional)

    sendMessage = json.dumps({"action" : action, "status" : status, "message" : message, "additional" :  additional})
    clientsock.sendall(sendMessage)

