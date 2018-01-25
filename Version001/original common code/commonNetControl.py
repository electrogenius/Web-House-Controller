import commonStrings as STR

import socket
import sys
import select
import multiprocessing
import time
from StringIO import StringIO

################################################################################
##
## Function: NetControlProcess (netSend, netReceive, ourId)
##
## Parameters: netSend - multiprocessing queue - 2 element tuple - data and destination socket.
##                   netReceive - multiprocessing queue - 2 element tuple - data and source socket.
##                   ourId - string - The id for this controller. e.g. GSM_ID, GATE_ID, LIGHTS_ID
##
## Returns: 
##
## Globals modified:
##
## Comments:
##
################################################################################

def NetControlProcess (netSend, netReceive, ourId) :

################################################################################

    def SendBroadcastProcess () :
        # Keep sending broadcast with system id and our id so other controllers know we are available.
        while 1 :
            broadcastSocket.sendto ((STR.SYSTEM_ID + ourId), ('<broadcast>', BROADCAST_PORT))
            #print "sent service announcement ", STR.SYSTEM_ID, ourId
            time.sleep (5)

################################################################################
    
    BROADCAST_PORT = 50000
    SERVER_PORT = 8089
    
    # Create a UDP broadcast socket.
    broadcastSocket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM) 
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
    broadcastSocket.bind (('', BROADCAST_PORT))
       
    # Start the broadcast process. This will keep sending a broadcast packet.
    multiprocessing.Process (target = SendBroadcastProcess).start ()

    # Now we will wait until we receive our own broadcast so that we can detect our physical ip address.
    while 1 :
        # Wait for received broadcast. We will get data (string) and the source address (ip address, port).
        broadcastData, ourBroadcastAddress = broadcastSocket.recvfrom (1024)
        
        # Is it our own broadcast?
        if broadcastData == (STR.SYSTEM_ID + ourId) :
            
            # Found our broadcast so get our ip address and create server address. Exit loop as we are done.
            serverAddress = (ourBroadcastAddress [0], SERVER_PORT)
            break
 
    # We have now got our server address so we can create the server tcp socket.
    try:
        serverSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind (serverAddress)
        serverSocket.listen (5)
    
    except socket.error, msg:
        print 'Socket failed with Error code : ' + str (msg[0]) + ' , Error message : ' + msg[1]
        sys.exit ()
                   
    # Start a dictionary of open sockets with the broadcast and server sockets. We will add or remove client 
    # sockets when connections are made and broken. We use the full socket address as the key. We will pass this
    # key back to the main code to identify the source of the data for any replies.
    openSocketDict = {ourBroadcastAddress : broadcastSocket, serverAddress : serverSocket}
    
    # Start a dictionary where we will keep the IP addresses for each of the system controllers. All controllers do a
    # regular broadcast and we will get the IP address from this. Each entry also has a timer that we restart on
    # receiving a broadcast. If the timer times out we flag the controller as lost. Format is as follows:
    # openControllerDict = {controller1 id : [address, timer], .......} 
    openControllerDict = {}
    
    # We may need to divert stdout so use StringIO to initialise a variable to use.
    catchStdout = StringIO ()
     
    # Main loop starts here.
    while 1:
        # We will sample everything at about 20mS intervals so timers need 50 units per second.
        time.sleep (0.02)
                
        # Scan through each of the open sockets in openSocketDict and check if we have received any data.
        for socketAddress, readSocket in openSocketDict.items () :
        
            # See if any received data on this socket, use zero timeout so we do not wait.
            if select.select ([readSocket], [], [], 0) == ([readSocket], [], []) :
        
                # Is it the broadcast socket that we originally created?
                if readSocket == broadcastSocket :
                
                    # Get the data and the address it was sent from. It could be ourselves.
                    # receivedData is a string, broadcastAddress is a tuple of (ip address, port).
                    receivedData, broadcastAddress = broadcastSocket.recvfrom (1024)

                    # Make sure it has our system ID on the front of the data and if it has get the controller ID.
                    receivedData = receivedData.upper ()
                    if receivedData.startswith (STR.SYSTEM_ID) :
                        controllerId = receivedData [len (STR.SYSTEM_ID) : ]
                        # Check it is a known controller.
                        if controllerId in STR.OURCONTROLLERS :  
                            # Is this is the 1st time we have seen or reseen this controller after it went offline? 
                            if not openControllerDict.has_key (controllerId) :
                                # Tell main code this controller is now online.
                                netReceive.put ((STR.ONLINE + STR.SPACE + controllerId, STR.BROADCAST))
                            # Save the IP address part in the system dictionary and set timer. We do this everytime
                            # we get a broadcast to keep setting the timer, which we are decrementing every 20mS
                            openControllerDict [controllerId] = [broadcastAddress [0], 500]
               
                # A server socket means we have a new client connection. Accept it and save client socket in our dictionary.
                elif readSocket == serverSocket :
                    clientSocket, clientAddress = serverSocket.accept ()
                    openSocketDict [clientAddress] = clientSocket
                    clientSocket.send ('Connection allowed\n')
                    print  'Client connection from : ', clientAddress
        
                # Not broadcast or server socket so must be a client socket. Get the data. If we have data return it
                # to the main program with the socket address. If no data we will shut connection down.
                else :
                    try :
                        receivedData = readSocket.recv (1024)
                        if receivedData:
                            netReceive.put ((receivedData, socketAddress))
                        else :
                            readSocket.close ()
                            del openSocketDict [socketAddress]
                            print 'Connection ended : ', socketAddress
                   
                    except socket.error , msg:
                        print 'Read failed. Error Code : ' + str (msg[0]) + ' Error message : ' + msg[1]
                        
                        readSocket.close ()
                        del openSocketDict [socketAddress]

        # Have we received anything from main process? If we have get the message and the command or address to send to.
        # If this is a system command sendAddress will hold 'SYSTEM' and the command will be in message.
        if not netSend.empty () :
            message, sendAddress = netSend.get ()
            # Is it a system command?
            if sendAddress == 'SYSTEM' :
                # Which command?
                if message == 'STDOUT DIVERT ON' :
                    # The system has requested that STDOUT is diverted. We will use stringio to catch STDOUT and then pass
                    # it back to the main code via our multiprocessing queue each time round the main loop.
                    sys.stdout = catchStdout = StringIO ()
                elif message == 'STDOUT DIVERT OFF' :
                     sys.stdout = sys.__stdout__

            # Not a command so must be something to send. Do not send anything that is broadcast or failed.
            elif sendAddress not in (STR.BROADCAST, STR.FAILED) :            
                # Is this a system controller message? Messages for system controllers will have the controller
                # ID name in the sendAddress field. 
                if sendAddress in STR.OURCONTROLLERS :
                    # Make sure the controller is online. It will have an entry in openControllerDict if it is. We will then
                    # use the ID name to lookup the ip address of the controller to send to.
                    if openControllerDict.has_key (sendAddress) :
                        ipAddress = openControllerDict [sendAddress][0]
                        # Scan through all our open clients to see if this ip address is open. Get related socket as well.
                        for openAddress, openSocket in openSocketDict.items () :
                            # Compare ip address part only. We do not know the port part of the address.
                            if ipAddress == openAddress [0] :
                                # Socket address is open so send the message using the related socket.
                                openSocket.sendall (message)
                                # Exit now we're done.
                                break
                        else :
                            # Controller address is not open so we will connect, send data and close a connection.
                            try :
                                sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sendSocket.connect ((ipAddress, SERVER_PORT))
                                sendSocket.sendall (message)
                                sendSocket.shutdown(socket.SHUT_RDWR)
                                sendSocket.close ()
                            except socket.error, msg :
                                netReceive.put ((STR.FAILED + STR.SPACE + 'NO CONTROLLER', STR.FAILED))
                    else :
                        # Controller is offline so return failed message.
                        netReceive.put ((STR.FAILED + STR.SPACE + sendAddress, STR.FAILED))
                            
                # Not a message for a system controller so must be for a client. Do we have to send to ALL clients?
                elif sendAddress == STR.ALL :
                    # Send to all open sockets, but exclude broadcast and server sockets.
                    for sendSocket in openSocketDict.values () :
                        if sendSocket not in (broadcastSocket, serverSocket) :
                            sendSocket.sendall (message)
                
                # A single send so make sure the client is online. It will have an entry in dictionary if it is.
                elif openSocketDict.has_key (sendAddress) :
                    sendSocket = openSocketDict [sendAddress]
                    sendSocket.sendall (message)
               
                # The socket is no longer active so return failed message.
                else :
                    netReceive.put ((STR.FAILED + STR.SPACE + 'NO SOCKET', STR.FAILED))
 
        # Decrement all the controller broadcast timers. If any timeout, flag that the associated controller is offline.
        for controllerId in openControllerDict :
            # Is the timer running? (not -ve).
            if openControllerDict [controllerId][1] >= 0 :
                # If it is running decrement it.
                openControllerDict [controllerId][1] -= 1
                # Has it timed out? (-ve).
                if openControllerDict [controllerId][1] < 0 :
                    # Flag controller offline by deleting it from the dictionary and tell main code it went offline.
                    del openControllerDict [controllerId]
                    netReceive.put ((STR.OFFLINE + STR.SPACE + controllerId, STR.BROADCAST))
                    # We MUST break as we have just deleted an item that is part of the for loop.
                    break
                
        monitorOutput = catchStdout.getvalue ()
        if monitorOutput :
            netReceive.put ((monitorOutput, 'SYSTEM'))
            sys.stdout = catchStdout = StringIO ()

################################################################################
##
## Function:
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: 
##
################################################################################

