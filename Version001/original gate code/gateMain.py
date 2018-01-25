#!/usr/bin/python

import commonNetControl as netControl

import commonStrings as STR
import gateConstants as C
import gateGlobals as G
import gateCommands as commands
import gateGeneral as general
import gateStatus as status
import gateTimer

import fcntl
import argparse
import datetime
from astral import Astral
import sys
import select
import time
import RPi.GPIO as GPIO

################################################################################
##
## Function:  main ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: Main program starts here.
##
################################################################################

def main () :

    # Test to see if we are already running by trying to lock a file. If we can lock it then we are able to run.
    # If we can't then we must already be running so simply exit
    pid_file = '/home/pi/Testing/gateControl.pid'
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

    # Open and close the gate programmed times file for appending so we create one if it is missing.
    f = open ('/home/pi/Testing/gatetimes.txt', 'a')
    f.close ()
    
    # Flag to keep last daytime check in. We need this so that we only do day / night tasks when we actually go from
    # day to night and vice versa.
    isDaytime = None
    
    # 1 minute timer for interval we will check for sunrise, sunset or timed gate opening.
    oneMinuteTimeCheck = None
    
    # Setup rpi I/O lines.
    general.InitialiseGPIO ()
    
    # Start the process that controls the leds and lights.
    G.ledProcess.start ()
    
    # Start the process that controls the gates.
    G.gateProcess.start ()
    
    # Start the process that controls the network communication.
    G.netProcess.start ()
    
    # Initialise Astral so we can get sunrise and sunset times.
    cityName = 'Bristol'
    a = Astral ()
    a.solar_depression = 'civil'
    city = a [cityName]
    
    # Check the initial level of all the GPIO lines and run commands according to messages we received. 
    statusMessages =  status.CheckRpiLines (changed = False)
    for message in statusMessages :
        commands.ProcessCommand (message)
        
    # Send a gates stopped to the gate process. It will then report back if the gates are fully closed or open.
    commands.ProcessCommand (STR.GATES_ARE_STOPPED)
    
    # Turn the red and green leds in the gate push buttons on.
    G.ledCommandQueue.put ((STR.RED, STR.ON))
    G.ledCommandQueue.put ((STR.GREEN, STR.ON))
    
    while 1 :
        # We will sample everything at about 20mS intervals.
        time.sleep (0.02)
        
        # Toggle the heartbeat led.
        GPIO.output(C.STATUS_LED_2, GPIO.input(C.STATUS_LED_2)^1)
        
        # Check GPIO lines for any level changes.
        statusMessages =  status.CheckRpiLines ()       
        # If we have had any level changes run the commands for those.
        if statusMessages : 
            for message in statusMessages :
                commands.ProcessCommand (message)
        
        # Check if we have received any network data. We will get a tuple back consisting of (data, (address)).
        # Where address is also a tuple consisting of (ip address, port) except if the data was from a broadcast,
        # in this case the word broadcast will be here and we must not reply.
        if not G.netReceiveQueue.empty () :
            message, sourceAddress = G.netReceiveQueue.get ()
            # Only process data if there are more than 2 characters, anything else will be just a CRLF or nothing.
            # Pass the result back to the network process as a tuple (data, (address)). Don't send if the source
            # was a broadcast.
            if len (message) > 2 :
                message = commands.ProcessCommand (message)
                if sourceAddress != STR.BROADCAST :
                    G.netSendQueue.put ((message + STR.CRLF, sourceAddress))
                
        # Only check stdin if we are being run from a terminal window.
        if runFromTerminal :
            # Check to see if anything has been entered on stdin.
            if select.select ([sys.stdin], [], [], 0) == ([sys.stdin], [], []) :           
                # Get keyboard data.
                keyData = raw_input ()
                # Only process data if there are characters, anything else will be a blank line.
                # Let user know the result.
                if keyData :
                    print commands.ProcessCommand (keyData)
                
        # If the gate process reports any status save it and pass it on to the user.
        if not G.gateStatusQueue.empty () :
            message = G.gateStatusQueue.get ()
            commands.ProcessCommand (message)
            G.gateState = message
            print 'MESSAGE FROM GATE: ', message
            G.netSendQueue.put ((message + STR.CRLF, STR.ALL))
            
            # If the gates have closed turn the drive lights off. If they are not closed and it is night turn them on.
            if G.gateState == STR.GATES_CLOSED :
                G.ledCommandQueue.put ((STR.DRIVE, STR.OFF))
            elif G.dayNightMode == STR.NIGHT :
                G.ledCommandQueue.put ((STR.DRIVE, STR.ON))

        # Get the current time.
        timeNow = time.localtime(time.time())
        
        # Is it time for a sunrise, sunset or timed operation check? We will do this every minute.
        if oneMinuteTimeCheck != timeNow.tm_min :
            oneMinuteTimeCheck = timeNow.tm_min
            
            # Check for timed gate operation.
            action = gateTimer.CheckForTimedGateOperation (timeNow)
            
            # Is this a new timed action? (open to close or close to open) If it is save the action and run it.
            if action != 'NO ACTION' and action != G.lastTimedGateAction :
                G.lastTimedGateAction = action
                commands.ProcessCommand (action)
                print 'TIMED ', action           

            # Get the current date/time and sunrise and sunset times and check if it is daytime (turn lights off).
            sun = city.sun (date = datetime.date.today (), local = True)
            tzinfo = sun ['sunrise'].tzinfo
            timeNow = datetime.datetime.now (tzinfo)
            sunrise, sunset = city.daylight ()
            dayState = sunrise < timeNow < sunset
            
            # If we have moved from day to night or vice versa save new state and set dayNightMode. We only
            # set dayNightMode on a change so that we do not keep setting it as it may have been changed via
            # a user command.
            if isDaytime != dayState :
                isDaytime = dayState
                command = STR.SET_DAY_MODE if isDaytime else STR.SET_NIGHT_MODE
                print command 
                commands.ProcessCommand (command)
                
if __name__ == '__main__' :
    main ()
