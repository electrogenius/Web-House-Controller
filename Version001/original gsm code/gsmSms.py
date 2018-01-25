import gsmGlobals as G
import gsmModem as modem

import serial

################################################################################
##
## Function: CheckForReceivedSMS (port)
##
## Parameters:  port - serial port object - the port to use.
##
## Returns: 
##
## Globals modified:
##
## Comments: The modem is configured to pass SMS messages directly to the serial port. So we will periodically call this
## function to check for SMS. SMS messages are identified by checking the start of the received data. This will start with
## +CMT:. We will then get the caller number, command and return it to the caller.
##
################################################################################
    
def  CheckForReceivedSMS (port) :
    
    # Check modem for any data. No need to wait so omit timeout parameter.
    rawModemData = modem.CheckForModemData (port)

    # Check if something received.
    if rawModemData != '' :
    
        print rawModemData
    
        # We make the text all uppercase for easy checking.
        rawModemData = rawModemData.upper ()
    
        # Parse to extract the received data. Each line is converted to a list entry.
        modemData = modem.ParseModemData (rawModemData)
        
        # A modem SMS message will be 2 or more lines and start with +CMT: 
        if len (modemData) >= 2 and modemData[0].startswith ('+CMT:') :
        
            # We have a message so extract the caller number and get the message.
            # The caller number is on the 1st line between the '+CMT: ' and the 1st comma. Note the number may start with a +.
            # The message is on the second line and there may be further lines if the message has newline characters in it.
            # Get the 1st line, which contains the caller number.
            callerNumberLine = modemData [0]
            
            # Find the 1st digit or '+', which will be the start of the number. Start at the space after the +CMT:.
            for firstDigitIndex in range (5, len (callerNumberLine)) :
                if callerNumberLine [firstDigitIndex].isdigit() or callerNumberLine [firstDigitIndex] == '+' :
                    break
                
            # Get here with firstDigitIndex pointing at the number. Extract the number. Number ends at 1st comma.
            callerNumber = callerNumberLine [firstDigitIndex : callerNumberLine.find (',')]
            
            # The 2nd line will have the command followed by, possibly, some further parameters. Split this line into a list so
            # that we can extract the command and parameters.
            commandData = modemData [1].split ()
            
            # The number is expected to be after the command so insert it into the list
            commandData.insert (1, callerNumber)
            
            # Pass command list to caller. 
            return  commandData
            
    # If we get here we have no message or a problem so return empty.
    return []

################################################################################
##
## Function: SendSms (port, number, message)
##
## Parameters:  port - serial port object - the port to use.
##                     number - string - the phone number.
##                     message - string - the message to send.
##
## Returns: int - if the message is sent we return the message number. If it fails we return -ve.
##
## Globals modified:
##
## Comments: Sends the supplied message to the supplied number. 
##
################################################################################

def SendSms (port, number, message) :

    #print 'sms send fake', number, message
    #return 1
    
    # The AT command to send an sms.
    smsAtCommand = 'AT+CMGS='
    
    # Flush out any data already in the serial input buffer.
    modem.CheckForModemData (port)
    
    # Send command with number to start message process. Number must be in double quotes. This command returns a '>' to
    # indicate ready for message text, so we cannot use our SendModemCommand function.
    port.write (smsAtCommand + '"' + number + '"' + '\r\n')
    
    # Now try and get the response.
    rawModemData = modem.CheckForModemData (port, 10)
    
    # Check if something received.
    if rawModemData != '' :
    
        # Parse response to the AT command. Converts each line to a list entry.
        modemData = modem.ParseModemData (rawModemData)
        
        # Response should be 2 lines. 1st line is command + number, 2nd line is the '>'. Note ParseModemData will have
        # removed the double quotes we added when sending the command.
        if len (modemData) == 2 and modemData [0] == smsAtCommand + number and  modemData [1] == '>' :
                
            print 'ready'
            
            # We got the correct response so send the text terminated with CTRL-Z (26)
            port.write (message + chr (26))
            
            # Now try and get the initial response. A second response will come when the text is completely sent.
            rawModemData = modem.CheckForModemData (port, 1)
            
            # Check if something received.
            if rawModemData != '' :
                        
                # Parse initial response. Converts each line to a list entry. Find out how many lines.
                modemData = modem.ParseModemData (rawModemData)
                modemDataLength = len (modemData)
                
                # Modem should initially simply echo back each line of the text sent. Note ParseModemData will have
                # removed the CTRL-Z we terminated the text with. If we send only a single line we can verify all
                # the message. For multiline messages we verify the final '>' prompt is present.
                if (modemDataLength == 1 and modemData [0] == message
                    or
                    modemDataLength > 1 and modemData [modemDataLength-1] == '>' ): 
        
                    print 'transmitting'

                    # Now try and get the second response. Data sheet specs this could be up to 60 seconds.
                    rawModemData = modem.CheckForModemData (port, 60)
                    
                    # Check if something received.
                    if rawModemData != '' :
        
                        # Parse second response. Converts each line to a list entry.
                        modemData = modem.ParseModemData (rawModemData)
    
                        # Response should be 2 lines. 1st line is +CMGS: XX. Where XX is a message number. 2nd line is OK
                        if len (modemData) == 2 and modemData [0].find ('+CMGS:') == 0 and  modemData [1] == 'OK' :
                            
                            print 'sent OK'
                            
                            # Sent OK so return message number to caller. This on the 1st line starting after the space and
                            # finishing at the end of line.
                            messageNumber = modemData [0]
                            messageNumber = messageNumber [messageNumber.find (' ') + 1 : len (messageNumber)]
                            return int (messageNumber)
    
    # If we get here we had an error. Send an ESC (27) to try and abort a failed send and then return -ve.
    port.write (chr (27))
    return -1

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
