import gsmGlobals as G

import serial
from string import maketrans
    
################################################################################
##
## Function: CheckForModemData (port, initialTimeout = 0)
##
## Parameters: port - serial port object - the port to use.
##                    initialTimeout - integer - time to wait for data to start.
##
## Returns: string containing data from modem. Null if no data.
##
## Globals modified:
##
## Comments: Try and read a single byte from the modem. If a byte is found read data from modem until no more
## received during our timeout period. Pass all the received data back to the caller as a string.
##
################################################################################

def CheckForModemData (port, initialTimeout = 0) :

    # Set timeout for initial test.
    port.timeout = initialTimeout
    
    # Check if any data available by reading a single byte.
    rawModemData = port.read (1)
    
    # Have we got data?
    if rawModemData != '' :
    
        # Set timeout so we wait until all data received. Timeout based on 9600 baud.
        port.timeout = 0.1
        
        # Read the rest of the data until we timeout.
        rawModemData = rawModemData + port.read (500)
    
    # Put timeout back to zero.
    port.timeout = 0
    
    # Pass data back. Will be null if no data
    return rawModemData
    
################################################################################
##
## Function: ParseModemData (rawModemData)
##
## Parameters: rawModemData - string - the data from the modem to parse.
##
## Returns: list of lines of modem data.
##
## Globals modified:
##
## Comments: Converts string of modem data to list of lines of the data with leading whitespace, double quotes and blank
## lines removed.
##
################################################################################
    
def ParseModemData (rawModemData) :

    # Remove all double quote marks. Note '"' is double quote between two single quotes.
    rawModemData = rawModemData.replace ('"','')
    
    # Remove any leading and trailing whitespace. This is normally a leading CRLF that the modem outputs before a message.
    # and a trailing space after the > prompt when sending a message. Then get each line into a list.
    rawModemData = rawModemData.strip ()
    modemData = rawModemData.splitlines ()
       
    # Remove any blank lines.    
    while '' in modemData :
        modemData.remove ('')
        
    # Pass data back as list of lines.    
    return modemData
    
################################################################################
##
## Function: SendModemCommand (port, command, resultLength)
##
## Parameters:  port - serial port object - the port to use.
##                     command - string - the command excluding the leading AT.
##                     resultLength - integer - the number of lines of the response expected.
##
## Returns: A list of the lines of the response. The list will be set empty if we have an error.
##
## Globals modified:
##
## Comments: Sends a command to the modem and verifies correct response. Each line of the response is placed in a list
## and returned to the caller.
##
################################################################################

def SendModemCommand (port, command, resultLength) :

    # Flush out any data already in the buffer.
    CheckForModemData (port)
    
    # Put AT on the front of the command.
    command = 'AT' + command
    
    # Send the command, terminate with a CRLF.
    port.write (command+'\r\n')
    
    # Get modem response. Set timeout so modem has time to respond.
    rawModemData = CheckForModemData (port, 1)

    # Check that something came back.
    if rawModemData != '' :
    
        # Parse to extract the returned data. Each line to a list entry.
        modemData = ParseModemData (rawModemData)
        
        # Commands echo back the original AT command followed by results followed by OK. So we check that we have the correct
        # number lines, have received the original command back and have the final OK. Commands that only set a mode will not
        # return any results.
        if len (modemData) == resultLength and modemData [0] == command and modemData [resultLength-1] == 'OK' :
            return modemData
        
    # If we get here we have a problem so return an empty list.
    return []

################################################################################
##
## Function: GetModemRssi (port)
##
## Parameters:  port - serial port object - the port to use.
##
## Returns: int - the rssi signal quality value. -ve if error detected.
##
## Globals modified:
##
## Comments: Extracts the signal quality value from the response to a AT+CSQ command.
##
################################################################################

def GetModemRssi (port) :

    # Try and get signal quality response from modem.
    modemData = SendModemCommand (port, '+CSQ', 3)
    
    # Did we get a valid response?
    if modemData != [] :
    
        #The signal quality text is in the second element. This has the format +CSQ: X,Y. Where X=rssi and Y=ber.
        # So we will extract the text between the space after :' and ',' and pass it back to the caller as an int.
        rssi = modemData [1]
        rssi = rssi [rssi.find (' ') : rssi.find (',')]
        return int (rssi)
    
    # If we get here we have a problem so return -ve
    return -1
 
################################################################################
##
## Function: InitialiseModem ()
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

def InitialiseModem () :

    # Use serial port for GSM modem communication. Initialise and get serial object. Use new alias: serial0.
    #modemPort = serial.Serial ("/dev/ttyAMA0", baudrate=9600, bytesize=8,parity='N',stopbits=1)
    modemPort = serial.Serial ("/dev/serial0", baudrate=9600, bytesize=8,parity='N',stopbits=1)
    modemPort.timeout = 0

    # Send AT to autobaud modem.
    print SendModemCommand (modemPort, '', 2)
    # Set SMS to text mode.
    print SendModemCommand (modemPort, '+CMGF=1', 2)
    # Set received SMS to serial port.
    print SendModemCommand (modemPort, '+CNMI=1,2,0,0,0', 2)
    
    return modemPort
    


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
