import commonStrings as STR
import commonNetControl as netControl
import gsmGlobals as G
import gsmConstants as C
import gsmStatus as status
import gsmModem as modem
import gsmSms as sms
import gsmCommands as commands
import gsmGeneral as general

import time
import argparse
import sys
import select
import serial
import RPi.GPIO as GPIO
import fcntl
from StringIO import StringIO
    
# Main program starts here.
def main () :

    # Test to see if we are already running by trying to lock a file. If we can lock it then we are able to run.
    # If we can't then we must already be running so simply exit
    pid_file = '/home/pi/Testing/program.pid'
    fp = open (pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # another instance is running
        sys.exit (0)

    # We use a command line argument to indicate if we are being run via systemd or from a terminal window.
    # We only use input from STDIN when we run from a terminal window.
    parser = argparse.ArgumentParser ()
    parser.add_argument ("-s", "--systemd", help = "run from systemd", action = "store_true")
    args = parser.parse_args ()
    runFromTerminal = not args.systemd
    
    # Start the process that controls the TCP network communication.
    G.netProcess.start ()
    
    # Get GPIO into correct state.
    general.InitialiseGPIO ()
    
    # Use serial port for GSM modem communication. Initialise and get serial object
    modemPort = modem.InitialiseModem ()

    # If called numbers file does not exist create an empty one. An existing one will simply be opened for append.
    # Move file pointer to start of file as we are going to read it. Get the contents of the file into the called numbers list.
    listFile = open ('/home/pi/Testing/calledNumbers.txt', 'a+')
    listFile.seek (0, 0)
    G.calledNumbers = listFile.read ().splitlines ()
    listFile.close ()
    
    # If allowed numbers file does not exist create an empty one. An existing one will simply be opened for append.
    # Move file pointer to start of file as we are going to read it. Get the contents of the file into the allowed numbers list.
    listFile = open ('/home/pi/Testing/allowedNumbers.txt', 'a+')
    listFile.seek (0, 0)
    G.allowedNumbers = listFile.read ().splitlines ()
    listFile.close ()

    # Run the STATUS command so we can see what state we are in. Only visible on STDOUT.
    commands.ProcessCommand ('STATUS', modemPort, 'STDIN', None)

    # This is our main loop. We will check for commands received from gpio, sms, stdin or a tcp connection.
    while 1 :
    
        # We will sample everything at about 20mS second intervals. Timers will be 50 units per second.
        time.sleep (.02)
        
        # Toggle the heartbeat led.
        GPIO.output(C.STATUS_LED_1, GPIO.input(C.STATUS_LED_1)^1)
        
        # Check GPIO lines for any level changes.
        statusMessages =  status.CheckRpiLines ()       
        # If we have had any GPIO level changes run the commands for those.
        if statusMessages : 
            for message in statusMessages :
                commands.ProcessCommand (message, modemPort, 'STATUS', None)

        # Check if we have received any network data. We will get a tuple back consisting of (data, (address)).
        # Where address is also a tuple consisting of (ip address, port) except if the data was from a broadcast,
        # failure or a system message in this case the word BROADCAST, FAILED or SYSTEM will be here and
        # we must not reply.
        if not G.netReceiveQueue.empty () :
            netData, sourceAddress = G.netReceiveQueue.get ()
            # If it is a system message simply display it.
            if sourceAddress == 'SYSTEM' :
                print 'From NetControl: ',netData
            # Only process data if there are more than 2 characters, anything else will be just a CRLF or nothing.
            elif len (netData) > 2 :
                commands.ProcessCommand (netData, modemPort, 'TCP', sourceAddress)

        # Test for sms data. If there is nothing we will get an empty list. A received sms will return a
        # list of the format: [command, sms number, possible 2nd number or data, more data, ...]
        smsData = sms.CheckForReceivedSMS (modemPort)
        # If we have received something process it.
        if smsData :
            # We need to pass the data to ProcessCommand as a string.
            commands.ProcessCommand (  ' '.join (smsData), modemPort, 'SMS', smsData [1])
            
        # Check to see if anything has been entered on stdin, but only if we are running from terminal.
        if runFromTerminal and select.select ([sys.stdin], [], [], 0) == ([sys.stdin], [], []) :           
            # Get keyboard data.
            keyData = raw_input ()
            # Only process data if there are characters, anything else will be a blank line.
            if keyData :
                # Reconnect STDOUT if we have redirected it with the monitor command.
                if sys.stdout != sys.__stdout__ :
                    sys.stdout = sys.__stdout__
                    G.netSendQueue.put (('STDOUT DIVERT OFF', 'SYSTEM'))  
                    
                # Run the command received from STDIN.
                commands.ProcessCommand (keyData, modemPort, 'STDIN', None)
        
        # If STDOUT divert is on we will get data in catchStdout so check if anything there. If there is send it to
        # the TCP connection that started the monitor command. Reset variable now we have read it.
        if sys.stdout != sys.__stdout__ :
            monitorOutput = G.catchStdout.getvalue ()
            if monitorOutput :
                G.netSendQueue.put ((monitorOutput, G.savedTcpForMonitor))
                sys.stdout = G.catchStdout = StringIO ()
            
if __name__ == '__main__' :
    main ()
 
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
