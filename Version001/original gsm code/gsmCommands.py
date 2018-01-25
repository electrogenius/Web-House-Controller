import sys
import select
import tty
import termios
import time
import RPi.GPIO as GPIO
import threading
from copy import deepcopy
from StringIO import StringIO

import commonStrings as STR
import gsmGlobals as G
import gsmConstants as C
import gsmStatus as status
import gsmGeneral as general
import gsmModem as modem
import gsmSms as sms

################################################################################
##
## Function: SendStatusToCallerCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                  port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Send the caller the current status of the system. This is the RSSI value, the alarm, fire and mains status and
## the list of numbers to send any alarm status to.
##
################################################################################

def SendStatusToCallerCommand (commandList, port) :

    # We will need the rssi value to send.
    rssi = modem.GetModemRssi (port)
    
    # Create the string we are going to send if gsm modem does not respond.
    #statusReply = 'No modem response\r\n'
    
   # Make sure we got a valid response. -ve would be an error, zero is no signal.
    #if rssi >= 0 :
    
    # Start the string we are going to send. If rssi is -ve it is a modem error.
    statusReply = 'RSSI = ' + str(rssi) + '\r\n' if rssi >= 0 else 'No modem response\r\n'
        
    # Check the current state of the input lines. 
    listOfStatusMessages = status.CheckRpiLines (changed = False)

    # Add the status messages to our reply.
    statusReply = statusReply + STR.CRLF.join (listOfStatusMessages) + STR.CRLF 
        
    # Initial text for the numbers list.
    statusReply = statusReply + 'Called Numbers:\r\n'

    # Go through numbers list and add to the response message.
    for number in G.calledNumbers :
        statusReply = statusReply + number + '\r\n'
        
    # Initial text for the allowed numbers.
    statusReply = statusReply + 'Allowed Numbers:\r\n'

    # Go through numbers list and add to the response message.
    for number in G.allowedNumbers :
        statusReply = statusReply + number + '\r\n'
            
    # Send status to user.
    return ('REPLY', statusReply)
    
################################################################################
##
## Function: SendHelpCommand (commandList, port, source)
##
## Parameters: commandList - list of strings - the original command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified:
##
## Comments: Send the caller a list of all the commands available.
##
################################################################################

def SendHelpCommand (commandList, port) :

    # Initial text for the help command response.
    helpText = 'Commands:\r\n'
    
        
    # Send help to user.
    return ('REPLY', helpText)
    
################################################################################
##
## Function: StatusChangeCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified:
##
## Comments: This will be called whenever one of our status lines changes state. We will notify all users via sms, STDOUT
## and TCP.
##
################################################################################

def StatusChangeCommand (commandList, port) :

    # Remove the source from the message before sending.
    del commandList [1]
    
    # For the input from the doorbell we will only send a message when it is ringing so send message for anything
    # unless we detect silent in the correct location
    if commandList [2].upper () != 'SILENT' :
        # Turn commandList into a string for sending.
        message = ' '.join (commandList)
        # Send to all tcp clients that are active. Double bracket to force tuple.
        G.netSendQueue.put ((message + STR.CRLF, STR.ALL))
        # Send to all sms numbers. Create a SEND command with ALL as destination.
        ProcessCommand ('SEND ALL ' + message, port, 'STATUS', None)
        # Show on STDOUT
        print message
    
    # Nothing more to do.
    return  ('NO REPLY', None)

################################################################################
##
## Function: RebootRouterCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified:
##
## Comments: We use this command to do a power cycle of the router. When power is removed and reapplied the check
## status routine will send a message to the user as the I/O line will change state.
##
################################################################################

def RouterRebootFinished () :

    # Called when timer we set below expires. Take line back low to reconnect power to the router
    GPIO.output (C.TEXECOM_NET1_EXP3_ZONE_32, GPIO.LOW)

def RebootRouterCommand (commandList, port) :

    # Get the source and remove from commandList. This will leave the message in commandList [0] and [1]
    source = commandList [1]
    del commandList [1]
    
    # This command is only allowed if it is from TCP,STDIN or an allowed sms number.   
    if source not in ('TCP', 'STDIN') and source not in G.allowedNumbers :
        return ('REPLY', 'Error: not allowed')
    
    # Set output line high to activate relay that will disconnect power from the router. Setting this line high will set the zone
    # secure and we will use an inverted alarm output to mimic this. Mains power through the relay is on the NC contacts so
    # when the relay activates power is switched off.
    GPIO.output (C.TEXECOM_NET1_EXP3_ZONE_32, GPIO.HIGH)
    
    # Start timer. On timeout this will take the line back low to turn the router back on.
    threading.Timer (20, RouterRebootFinished).start ()
    
    # Nothing more to do.
    return ('NO REPLY', None)
          
################################################################################
##
## Function: TerminalCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified:
##
## Comments: Runs a simple terminal so that we can send commands and listen to the modem with stdin and stdout.
##
################################################################################

def TerminalCommand (commandList, port) :

    # Called when threading timer expires to give us 1 second ticks to time out inactive use.
    def OneSecondTimeout (status) :
        status.set ()

    ############################################################################
                
    # Tell user where we are.
    print 'Terminal mode: CTRL-C to exit'
    
    # Initialise flag and time for our 1 second timeout timer. Set flag so we start timer 1st time through.
    oneSecondTimerTick = threading.Event ()
    oneSecondTimerTick.set ()
    terminalTimeout = 60
    
    # Save the current tty settings so we can restore them later.
    old_in_settings = termios.tcgetattr (sys.stdin)

    # Set raw mode. Do it in a try so we always restore the old settings.
    try:
        tty.setraw(sys.stdin.fileno ())
        
        # Now just pass data to and from the modem.
        while 1:
        
            # Has 1 second elapsed?
            if oneSecondTimerTick.isSet () :
                # Reset the flag and decrement our timeout.
                oneSecondTimerTick.clear ()
                terminalTimeout -= 1
                # If we have timed out just exit.
                if terminalTimeout <=0 :
                    break
                # Not timed out so start another tick.
                threading.Timer (1, OneSecondTimeout, args = (oneSecondTimerTick,)).start ()

            # Move data from modem to screen.
            modemData = port.read (1)
            if modemData != '' :
                sys.stdout.write (modemData)
                sys.stdout.flush ()
            
            # Move data from keyboard to modem. Convert back key to backspace and exit on Ctrl-C.
            if select.select ([sys.stdin], [], [], 0) == ([sys.stdin], [], []) :
                keyboardData = sys.stdin.read (1)
                if keyboardData == chr (127) :
                    keyboardData = chr (8)
                if keyboardData == 'Z' :
                    keyboardData = chr (26)
                if keyboardData == chr (3) :
                    break
                port.write (keyboardData)
                # Got some input so restart timeout.
                terminalTimeout = 60
                
    # Restore tty settings to original values whatever happens.
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_in_settings)
        
        # Tell user we finished.
        print 'Exiting terminal mode'
        # Nothing more to do.
        return ('NO REPLY', None)

################################################################################
##
## Function: SendAnSmsCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command line. commandList [0] is the command.
##                   the number to send to will start in commandList [1] and the text to send will follow the number. The
##                   number could be in muliple locations if it had spaces in it. This will be delt with when we check it.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified:
##
## Comments: Sends text data to the number supplied. If the number is 'ALL' we use all the numbers in numberList.
##
################################################################################

def SendAnSmsCommand (commandList, port) :

    # Remove command from the list so source will be in commandList [0].
    del commandList [0]
    
    # Get source then remove source from the list so number will be in commandList [0].
    source = commandList [0]
    del commandList [0]

    # If the command did NOT come from tcp, stdin or status, reply that it is not allowed.
    if source not in ('TCP', 'STDIN', 'STATUS') :
        return ('REPLY', 'Error: not allowed')
        
    # Make sure number is valid. This will also tidy up a number broken with spaces. If the number is good or ALL it 
    # will be in commandList [0]. If the number is bad commandList will be empty.
    commandList = general.CheckForValidNumber (commandList)
    if not commandList :
        return ('REPLY', 'Error: Invalid number')
        
    # Do we have text to send? commandList will have more than 1 entry. The number [0] and the text [1+].
    if len (commandList) < 2 :
        return ('REPLY', 'Error: No text')
        
    # Get the number and text to send
    number = commandList [0]
    sendText = ' '.join (commandList [1 : ])
    
    # Are we using ALL the numbers in numberList?
    if number == 'ALL' :
        # Make sure we have numbers in the list.
        if G.calledNumbers :
            # Start the response message for a good send to all numbers.
            allSendResponseMessage =  'Message sent to: '
            # Use each number in turn and send message to that number.
            for number in G.calledNumbers :
                sms.SendSms (port, number, sendText)
                allSendResponseMessage = allSendResponseMessage + number + ' '

            # Get here when all sent so tell user.
            responseMessage = allSendResponseMessage           
        # No numbers in list.
        else :
            responseMessage = 'Error: no numbers'
    # Single number is supplied.
    else :
        sms.SendSms (port, number, sendText)
        responseMessage = 'Message sent to: ' + number

    return ('REPLY', responseMessage)
    
################################################################################
##
## Function: AddNumberCommand (commandList, port, mode = 'CALLED NUMBERS')
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##                   mode - string - specifies either called or allowed numbers to update - called by default.
##
## Returns:
##
## Globals modified: 
##
## Comments: Adds the supplied number to the supplied list. If the command is from sms we may have 2 numbers.
## The 1st number is the sms number and a possible 2nd number will be the number we want to add rather than the
## sms number. On sms just entering 'ADD' will add the sms number. Entering 'ADD number' will add 'number'.
##
################################################################################

def AddNumberCommand (commandList, port, mode = 'CALLED NUMBERS') :

    if mode == 'ALLOWED NUMBERS' :
        listName = G.allowedNumbers
        fileName = '/home/pi/Testing/allowedNumbers.txt'
    else :
        listName = G.calledNumbers
        fileName = '/home/pi/Testing/calledNumbers.txt'
    
    # Remove command from the list so source will be in commandList [0].
    del commandList [0]
    
    # Get source if it is tcp or stdin remove it so number is now in commandList [0]. For sms this will be the sms number
    source = commandList [0]
    if source in ('TCP', 'STDIN') :
        del commandList [0]
        
     # Make sure number is valid. This will also tidy up a number broken with spaces. If the number is good it will be in
    # commandList [0]. If the number is bad commandList will be empty.
    commandList = general.CheckForValidNumber (commandList)
    # Is there any more data other than the 1st number and did it come from sms (not tcp or stdin)?
    if len (commandList) > 1 and source not in ('TCP', 'STDIN') :
        # Remove the 1st number (the sms number) and see if the 2nd number is valid.
        del commandList [0]
        commandList = general.CheckForValidNumber (commandList)
         
    # Was 1st or 2nd number a good number? We should have just a single number or ALL in commandList. ALL is
    # is not allowed for this command.
    if len (commandList) == 1 and commandList [0] != 'ALL' :
        #  Get the number and make sure we do not already have this number in the list.
        number = commandList [0]
        if number in listName :       
            # Number is a duplicate so set exists response message.
            responseMessage = 'Error: number exists'               
        
        # If this is a called number make sure it is already an allowed number.
        elif mode == 'ALLOWED NUMBERS' or number in G.allowedNumbers :
            # New number so add it to our list and set added response message.
            listName.append (number)
            responseMessage = 'Added: ' + number 
            
            # Update file with new number.
            listFile = open (fileName, 'a')
            listFile.write (number + '\n')
            listFile.close ()
        
        else :
            # Number is not allowed
            responseMessage = 'Error: not allowed'

    else :
        # Bad number so return error message.
        responseMessage = 'Error: bad number'
    
    return ('REPLY', responseMessage)

################################################################################
##
## Function: AddAllowedNumberCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Updates the list of numbers that we allow calls from. For security we only allow this from TCP and STDIN.
## The number supplied will only be added to the allowed numbers list. If the number is to be called for an alarm condition
## it will also have to te added to the numbers list.
##
################################################################################

def AddAllowedNumberCommand (commandList, port) :

    # Remove the word 'allowed' from the command list so we can use the normal add command.
    del commandList [2]
    
    # Call AddNumberCommand with allowed number parameter.
    return AddNumberCommand (commandList, port, mode = 'ALLOWED NUMBERS')

################################################################################
##
## Function: RemoveNumberCommand (commandList, port, mode = 'CALLED NUMBERS')
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##                   mode - string - specifies either called or allowed numbers to update - called by default.
##
## Returns:
##
## Globals modified: 
##
## Comments: Removes the supplied number from a numbers list. If the command is from sms we may have 2 numbers.
## The 1st number is the sms number and a possible 2nd number will be the number we want to remove rather than the
## sms number. On sms just entering 'REMOVE' will remove the sms number. Entering 'REMOVE number' will remove number.
##
################################################################################

def RemoveNumberCommand (commandList, port, mode = 'CALLED NUMBERS') :

    if mode == 'CALLED NUMBERS' :
        listName = G.calledNumbers
        fileName = '/home/pi/Testing/calledNumbers.txt'
    else :
        listName = G.allowedNumbers
        fileName = '/home/pi/Testing/allowedNumbers.txt'
    
    # Remove command from the list so source will be in commandList [0].
    del commandList [0]
    
    # Get source if it is tcp or stdin remove it so number is now in commandList [0]. For sms this will be the sms number
    source = commandList [0]
    if source in ('TCP', 'STDIN') :
        del commandList [0]
        
    # Make sure number is valid. This will also tidy up a number broken with spaces. If the number is good it will be in
    # commandList [0]. If the number is bad commandList will be empty.
    commandList = general.CheckForValidNumber (commandList)
    # Is there any more data other than the 1st number and did it come from sms (not tcp or stdin)?
    if len (commandList) > 1 and source  not in ('TCP', 'STDIN') :
        # Remove the 1st number (the sms number) and see if the 2nd number is valid.
        del commandList [0]
        commandList = general.CheckForValidNumber (commandList)
         
    # Was 1st or 2nd number a good number? We should have just a single number or ALL in commandList. ALL is
    # is not allowed for this command.
    if len (commandList) == 1 and commandList [0] != 'ALL' :
        #  Get the number and make sure we  have this number in the list.
        number = commandList [0]
        if number in listName :       
            # Number is in the list so remove it and set removed response message.
            listName.remove (number)
            responseMessage = 'Removed: ' + number
            # Update file with all entries from list.
            listFile = open (fileName, 'w')
            for number in listName :
                listFile.write (number+'\n')
            listFile.close ()
        else:
            # Number not in list so return unknown message.
            responseMessage = 'Error: unknown number'               
    else :
        # Bad number so return error message.
        responseMessage = 'Error: bad number'
    
    return ('REPLY', responseMessage)

################################################################################
##
## Function: RemoveAllowedNumberCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Updates the list of numbers that we allow calls from. For security we only allow this from TCP and STDIN.
## The number supplied will be removed from both the allowed numbers list and the called numbers list
##
################################################################################

def RemoveAllowedNumberCommand (commandList, port) :

    # Remove the word 'allowed' from the command list so we can use the normal remove command.
    del commandList [2]
    
    # Need a real copy as we are going to delete from the list during the 1st call to remove.
    commandListCopy = deepcopy (commandList)
    
    # 1st try and remove number from called list. It may not be there, but we will ignore the reply.
    RemoveNumberCommand (commandListCopy, port)
    
    # Call RemoveNumberCommand with allowed number parameter.
    return RemoveNumberCommand (commandList, port, mode = 'ALLOWED NUMBERS')
    
################################################################################
##
## Function: TestPurposeCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments:
##
################################################################################

def TestPurposeCommand (commandList, port) :
    
    return ('REPLY TO PENDING', 'JUNK')

################################################################################
##
## Function: ControllerCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Called when we receive a control message from the network process. This could be the reception or loss
## of a broadcast from one of the system controllers. Detection of a network failure will also call this function.
##
################################################################################

def ControllerCommand (commandList, port) :

    # Just show the message for now.
    print ' '.join (commandList)
    
    # No reply allowed.
    return ('NO REPLY', None)

################################################################################
##
## Function: GateControllerButtonCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList [4] is the pressed / released word.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Called when we receive a message from the gate controller indicating a button operation. When a button
## is pressed we will set an alarm chime zone active so we know when someone has pressed a button at the gate.
## We will also send an sms if the sendAlertsToSms flag is set.
##
################################################################################

def GateControllerButtonCommand (commandList, port) :

    def ChimeFinished () :

        # Called when timer we set below expires. Take line back high to make zone secure.
        GPIO.output (C.TEXECOM_NET1_EXP3_ZONE_29, GPIO.HIGH)

    # Only operate chime on button press.
    if commandList [4] == 'PRESSED' :
    
        # Take line low this will cause the zone to go active and chime.
        GPIO.output (C.TEXECOM_NET1_EXP3_ZONE_29, GPIO.LOW)
        
        # Start timer. On timeout this will take the line back high to make zone secure again.
        threading.Timer (4, ChimeFinished).start ()
        
        if G.sendAlertsToSms :
            # Remove source from list before we send the message.
            del commandList [1]
            # Send to all sms numbers. Create a SEND command with ALL as destination.
            ProcessCommand ('SEND ALL ' + ' '.join (commandList [0:4]), port, 'STATUS', None)
            # Make sure we have numbers in the list.
 #           if G.calledNumbers :
                # Use each number in turn and send message to that number.
#                for number in G.calledNumbers :
#                    sms.SendSms (port, number, ' '.join (commandList [0:4]))
    
    # No reply required.
    return ('NO REPLY', None)
          
################################################################################
##
## Function: GatesOperateCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. 
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Called when we want to open or close the gates. We simply pass a message on to the gates controller.
##
################################################################################

def GatesOperateCommand (commandList, port) :

    # Get the source and remove from commandList. This will leave the message in commandList [0:2]
    source = commandList [1]
    del commandList [1]
    
    # This command must be from TCP,STDIN or an allowed sms number.   
    if source not in ('TCP', 'STDIN') and source not in G.allowedNumbers :
        return ('REPLY', 'Error: not allowed')
    
    # Just pass the message on. It has to be a string.
    if G.useBackupVersion :
        G.netSendQueue.put (( ' '.join (commandList [0:2]) + STR.CRLF, STR.BU_GATE_ID))  
    else :
        G.netSendQueue.put (( ' '.join (commandList [0:2]) + STR.CRLF, STR.GATE_ID))  
    
    # Say we are want to wait for reply.
    return ('SET REPLY PENDING', None)

################################################################################
##
## Function: GatesTimedCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. 
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Called when we want to start or stop timed operation. We simply pass a message on to the gates controller.
##
################################################################################

def GatesTimedCommand (commandList, port) :

    # Get the source and remove from commandList. This will leave the message in commandList [0:3]
    source = commandList [1]
    del commandList [1]
    
    # This command must be from TCP,STDIN or an allowed sms number.   
    if source not in ('TCP', 'STDIN') and source not in G.allowedNumbers :
        return ('REPLY', 'Error: not allowed')
    
    # Just pass the message on. It has to be a string.
    if G.useBackupVersion :
        G.netSendQueue.put (( ' '.join (commandList [0:3]) + STR.CRLF, STR.BU_GATE_ID))  
    else :
        G.netSendQueue.put (( ' '.join (commandList [0:3]) + STR.CRLF, STR.GATE_ID))  
    
    return ('REPLY', 'OK')

################################################################################
##
## Function: GatesStatusCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Called when the gate controller reports the gate status. We will pass the message on so that it can be sent
## to the user that requested the gate operation. 
##
################################################################################

def GatesStatusCommand (commandList, port) :

    # Remove the source from the commandList before turning to a string.
    del commandList [1]

    # Turn commandList into a string for sending.
    message = ' '.join (commandList)
    
    if G.sendAlertsToSms :
        # Send to all sms numbers. Create a SEND command with ALL as destination.
        ProcessCommand ('SEND ALL ' + message, port, 'STATUS', None)

        # This will be a reply to a pending gates open or close command. If we asked for no reply then it is just discarded.
    return ('REPLY TO PENDING', message)

################################################################################
##
## Function: CheckBalanceCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Called when we want to check the sim balance. We send BAL to 2732 for ASDA.
##
################################################################################

def CheckBalanceCommand (commandList, port) :

    # Send request to operator. The reply from the operator will be processed as a normal command.
    sms.SendSms (port, '2732', 'BAL')
    
    # Say we are want to wait for reply.
    return ('SET REPLY PENDING', None)

################################################################################
##
## Function: AsdaSystemCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList[0] is the command.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Called when we receive a message from 2732 on Asda. This is the management number and we are most
## likely receiving a balance request.
##
################################################################################

def AsdaSystemCommand (commandList, port) :

    # The number will be in location 1 so delete it.
    del commandList [1]
    # Now turn into a string and replace any 8 bit characters with 7 bit versions. This is because sms texts appear to use
    # 8 bit ASCII characters for symbols such as the pound sign
    reply = ' '.join (commandList)
    for letter in reply :
        value = ord (letter)
        if value > 127 :
            reply = reply.replace (chr (value), chr (value - 128))
            
    # This will be a reply to a balance command.
    return ('REPLY TO PENDING', reply)
    
################################################################################
##
## Function: MonitorCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList [2] is the on/off word.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Called when we want to send the output of print statements to a TCP connection rather than STDOUT so that
## we can monitor the operation of the controller. We will revert to STDOUT if we detect anything on STDIN or we get a
## monitor off command.
##
################################################################################

def MonitorCommand (commandList, port) :

    if commandList [2] == 'ON' :
        sys.stdout = G.catchStdout = StringIO ()
        G.netSendQueue.put (('STDOUT DIVERT ON', 'SYSTEM'))  
        print 'STDOUT diverted'
    else :
        sys.stdout = sys.__stdout__
        G.netSendQueue.put (('STDOUT DIVERT OFF', 'SYSTEM'))  
        G.netSendQueue.put (('STDOUT restored' + STR.CRLF, G.savedTcpForMonitor))
    return ('SAVE TCP', None)

################################################################################
##
## Function: SmsAlertsCommand (commandList, port)
##
## Parameters: commandList - list of strings - the original command. commandList [3] is the on/off word.
##                   port  - serial port object - the port to use to communicate with the GSM modem.
##
## Returns:
##
## Globals modified: 
##
## Comments: Enable or disable sending of general alerts, such as gate buttons pressed to the sms numbers.
##
################################################################################

def SmsAlertsCommand (commandList, port) :
  
    G.sendAlertsToSms = True if commandList [3] == 'ON' else False
  
    return ('REPLY', 'OK')

###############################################################################
##
## Function: ProcessCommand (inputData, modemPort, source, address)
##
## Parameters: inputData - string - the command string to process.
##                  port - serial port object - the port to use to communicate with the GSM modem.
##                  source - string - where the command came from - SMS, TCP, STDIN
##                  address - string/tuple - for sms the sms number or for tcp the ip address and port tuple.
##
## Returns:
##
## Globals modified:
##
## Comments: Splits the inputData into a list. The 1st word is treated as the command and the following words
## are the parameters.  Checks against a lookup of available commands and parameters and if we have a match
## runs the required command.
##
################################################################################

def ProcessCommand (inputData, port, source, address) :

    # Lookup table for all valid commands. We use this to verify the command is valid and then call the required command.
    # Each element holds a command and all the valid parameters and the function to call. There are 2 special values in the
    # lookup: A ? means match any word in this position and ?? means ignore this and any further words.
    # Note that commands received from sms always have the number as the 2nd word in the inpuData, hence for single word
    # sms commands we allow a 2nd word. For non sms commands we will detect too many words in the command function.
    commandLookup = (
        (('MONITOR',), ('TCP',), ('ON', 'OFF'), MonitorCommand),
        (('TEST',), ('?',), TestPurposeCommand),
        (('OPEN', 'CLOSE'), ('?',), ('GATES',), GatesOperateCommand),
        (('TIMED',), ('?',), ('GATES',), ('ON', 'OFF'), GatesTimedCommand),
        (('GATES',), ('?',), ('OPEN', 'CLOSED', 'HALTED', 'BUSY'), GatesStatusCommand),
        (('HELP',), ('?',), SendHelpCommand),
        (('ADD',), ('TCP', 'STDIN'), ('ALLOWED',), ('??',), AddAllowedNumberCommand),
        (('ADD',), ('??',), AddNumberCommand),
        (('REMOVE',), ('TCP', 'STDIN'), ('ALLOWED',), ('??',), RemoveAllowedNumberCommand),
        (('REMOVE',), ('??',), RemoveNumberCommand),
        (('SEND',), ('??',), SendAnSmsCommand),
        (('STATUS',), ('?',), SendStatusToCallerCommand),
        (('REBOOT',), ('?',), RebootRouterCommand),
        (('FGC',), ('??',), StatusChangeCommand),
        (('SMS',), ('?',), ('ALERTS',), ('ON', 'OFF'), SmsAlertsCommand),
        (('TERMINAL',), ('STDIN',), TerminalCommand),
        (('GATE',), ('?',), ('BUTTON',), ('OPEN', 'STOP', 'PED'), ('PRESSED', 'RELEASED'), GateControllerButtonCommand),
        ((STR.FAILED,), ('??',), ControllerCommand),
        ((STR.OFFLINE,), ('TCP',), STR.OURCONTROLLERS, ControllerCommand),
        ((STR.ONLINE,), ('TCP',), STR.OURCONTROLLERS, ControllerCommand),
        (('BAL',), ('?',), ('ASDA',), CheckBalanceCommand),
        (('?',), ('2732',), ('??',), AsdaSystemCommand)
   )
    
    # When we execute a command we will be passed back 2 strings. These are an action and a message. The action
    # tells us what to do. E.g. reply to the user. The message is what we use as the reply.
    action = ''
    replyMessage = ''

    # Convert the received string to uppercase and into list of parameters.
    inputDataList = inputData.upper ().split ()
    # If the command came from tcp, stdin or status we will insert this after the 1st command word. Commands from sms
    # will have the sms number here. This allows us to identify where the command came from when parsing it.
    if source in ('TCP', 'STDIN', 'STATUS') :
        inputDataList.insert (1, source)
    # Save the number of entries in the list.
    numberOfParametersInInput = len (inputDataList) 
    
    # Now we will try and match the supplied command with an entry in our table of commands.
    for testCommand in commandLookup :
            
        # Note that testCommand includes the function to call in it's length, hence the -1.
        # numberOfParametersInTestCommand will also be the index for the function to call.
        numberOfParametersInTestCommand = len (testCommand)  - 1

        # Verify that the command has the correct parameters by checking each word.
        # Miss the function to call at end of the line.
        for inputWord, testWords in zip (inputDataList, testCommand [0 : numberOfParametersInTestCommand]) :
            
            # A ?? means ignore this and all further parameters so run the command and exit.
            if '??'  in testWords :
                action, replyMessage =  testCommand [numberOfParametersInTestCommand] (inputDataList, port)
                break
        
            # Check a word is NOT one of the valid words for this position. A ? means match any word in that position.
            if inputWord not in testWords and '?' not in testWords :
                
                # Exit if word not valid. This is not fatal as there could be the same command with different parameters.
                # We exit back to get the next testCommand.
                break

        # If we get here all the words match in the shortest list.
        else :
            # Does the input line have the same number of parameters as this testCommand? We need to do this as
            # the lists in zip may be different lengths.
            if numberOfParametersInInput == numberOfParametersInTestCommand :
                # Parameters are all good and we have same number of them so execute command.
                action, replyMessage =  testCommand [numberOfParametersInTestCommand] (inputDataList, port)
    
        # If we now have an action we have run a command so exit the outer for loop.
        if action:
            break
    # If we get here we did not find the command or correct number of parameters so flag error to user.
    else :
        action, replyMessage = 'REPLY', 'Error: Command error'
    
    # Check through to see what action to take.
    if action == 'SAVE TCP' :
        G.savedTcpForMonitor = address
    
    elif action == 'SET REPLY PENDING' :
        G.pendingReplyDestination [0:2] = source, address
    
    elif action == 'REPLY TO PENDING' : 
        # Get the pending destination to overwrite the current source and address and then clear pending destination.
        source, address = G.pendingReplyDestination [0:2]
        G.pendingReplyDestination [0:2] = [None, None]
        # If we have a destination we will make the action a reply so it is processed below. If there was no pending
        # destination there will be no source so we will just fall through and do nothing as the action will still be set
        # to REPLY TO PENDING.
        if source :
            action = 'REPLY'
    
    if action == 'REPLY' :
        if source == 'TCP' :
            # Do not reply to broadcast or failure messages.
            if address not in (STR.BROADCAST, STR.FAILED) :
                G.netSendQueue.put ((replyMessage + STR.CRLF, address))
        elif source == 'SMS' :
            # Make sure it is a normal number and not an operator number.
            if address.startswith ('+44') :
                sms.SendSms (port, address, replyMessage)
        elif source == 'STDIN' :
            print replyMessage
    
    
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
  
    
    
