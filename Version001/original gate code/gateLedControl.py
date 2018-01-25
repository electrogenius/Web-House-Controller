import commonStrings as STR
import gateConstants as C

import time
import RPi.GPIO as GPIO

################################################################################
##
## Function: LedControl (command)
##
## Parameters: command - multiprocessing queue. - tuple - 1st element is the led and 2nd element is command required.
##
## Returns:
##
## Globals modified:
##
## Comments: We call this function as a process to control the red, green,front, drive and sign leds. We pass it commands
## through a multiprocessing queue. There are 5 leds (red, green,front, drive and sign) and 5 commands (on, off, flash1,
## flash2 and last). Flash1 and flash2 set the led to flash, but on alternate periods of the flash so that you can set 2 leds
## to flash in anti-phase. Last will terminate a flash and/or restore the previous led state. We run this as a process as it
## enables us to use a simple infinite loop with a delay to generate a flash without any overhead in the main code.
##
################################################################################

def LedControl (command) :

    # Timer for period a flash will last. 20mS units.
    flashDelay = 0
    # Flag that inverts every flash delay period. We use this to flash 2 leds alternately.
    flashCycle = 0
    
    # Create a dictionary that holds a lookup for the states to output to the leds for each of the commands. The
    # supplied command will lookup a 2 element tuple. The 1st element is the led flash 1 state and the 2nd element
    # is the led flash 2 state. We then keep these states in the STATE element. We also keep the state of an on or off 
    # in the LAST element so that we restore that state if we stop a flash command with a last. 
    stateLookup = {
        'RED' : {'ON': (1, 1), 'OFF': (0, 0), 'FLASH1' : (1, 0), 'FLASH2' : (0, 1), 'LAST' : [0, 0], 'STATE' : [0, 0]},
        'GREEN' : {'ON': (1, 1), 'OFF': (0, 0), 'FLASH1' : (1, 0), 'FLASH2' : (0, 1), 'LAST' : [0, 0], 'STATE' : [0, 0]},
        'FRONT' : {'ON': (1, 1), 'OFF': (0, 0), 'FLASH1' : (1, 0), 'FLASH2' : (0, 1), 'LAST' : [0, 0], 'STATE' : [0, 0]},
        'DRIVE' : {'ON': (1, 1), 'OFF': (0, 0), 'FLASH1' : (1, 0), 'FLASH2' : (0, 1), 'LAST' : [0, 0], 'STATE' : [0, 0]},
        'SIGN' : {'ON': (1, 1), 'OFF': (0, 0), 'FLASH1' : (1, 0), 'FLASH2' : (0, 1), 'LAST' : [0, 0], 'STATE' : [0, 0]}
    }
    while 1 :
        while 1 :
            # Have we got a command?
            if not command.empty () : 
            # Get the 2 parameters
                commandData = command.get ()              
                # Hang on to current state while we load new state. We cannot put it into LAST now as we maybe
                # reading LAST for the current command and we must not change it until after it is read.
                previousState = stateLookup [commandData [0]]['STATE']               
               # Load new state required for the specified led colour and command.
                stateLookup [commandData [0]]['STATE'] = stateLookup [commandData [0]][commandData [1]]                
                # Save the previous state so it can be restored with a last.
                stateLookup [commandData [0]]['LAST'] = previousState              
                # Now go and set led to new state.
                break
            
            # No command so increment timer.
            else :
                flashDelay += 1
                # Have we waited 1s (50x20mS)?
                if flashDelay >= 50 :
                    # Reset timer and invert flash.
                    flashDelay = 0
                    flashCycle ^= 1
                    # Toggle the status led.
                    GPIO.output(C.STATUS_LED_1, GPIO.input(C.STATUS_LED_1)^1)                  
                    # Now go and set leds to new state.
                    break
                   
                # Get here if no command and not time to service leds so wait 20mS.
                else :
                    time.sleep (0.02)
            
        # Use saved STATE to set leds to required states. As flashCycle inverts each time through we will use one of the two
        # values that we look up alternately. So if the values are the same a led will either be on for (1,1) or off for (0,0).
        # If the values are different (0,1) or (1,0) the led will flash.
        GPIO.output (C.RED_LED_OUTPUT, stateLookup ['RED']['STATE'][flashCycle])    
        GPIO.output (C.GREEN_LED_OUTPUT, stateLookup ['GREEN']['STATE'][flashCycle])
        GPIO.output (C.FRONT_LED_OUTPUT, stateLookup ['FRONT']['STATE'][flashCycle])
        GPIO.output (C.DRIVE_LED_OUTPUT, stateLookup ['DRIVE']['STATE'][flashCycle])
        GPIO.output (C.SIGN_LED_OUTPUT, stateLookup ['SIGN']['STATE'][flashCycle])

