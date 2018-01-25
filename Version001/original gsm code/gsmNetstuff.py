import socket
import sys
import select
 
################################################################################
##
## Function: InitialiseTCPSocket (host, port)
##
## Parameters: host - string - ip address in dot notation.
##                    port - integer - the port to listen on.
##
## Returns: TCP socket - the server tcp socket.
##
## Globals modified:
##
## Comments: Initialise a TCP socket that we will use to get monitor commands and send status to.
##
################################################################################
 
def InitialiseTcpSocket (host, port) :

    try:
        #Create an AF_INET, STREAM socket.
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error, msg:
        print 'Create failed. Error code : ' + str(msg[0]) + ' , Error message : ' + msg[1]
        sys.exit ()
     
    print 'Socket Create'
    
    try:
        tcpSocket.bind ((host, port))
    except socket.error , msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message : ' + msg[1]
        sys.exit ()
         
    print 'Socket Bind'
      
    # Only allow 1 connection.
    tcpSocket.listen(1)
    
    # Pass socket back to caller.
    return tcpSocket
    
################################################################################
##
## Function: CheckForTcpConnection (serverTcpSocket)
##
## Parameters: serverTcpSocket - TCP socket - the server tcp socket.
##
## Returns: TCP socket - null if no connection, the client tcp socket if a connection.
##
## Globals modified:
##
## Comments: 
##
################################################################################

def CheckForTcpConnection (serverTcpSocket) :

    clientTcpSocket = None
    if select.select ([serverTcpSocket], [], [], 0) == ([serverTcpSocket], [], []) :
        clientTcpSocket, addr = serverTcpSocket.accept ()
        clientTcpSocket.send ('Connection allowed\n\r')
        print  'Connection from : ', addr

    return clientTcpSocket
    
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
