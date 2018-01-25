import gsmGlobals as G
import gsmConstants as C
import gsmSms as sms

import RPi.GPIO as GPIO
from copy import deepcopy

################################################################################
##
## Function:  InitialiseGPIO ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: Initialise all the IO lines required. Set all outputs low and all inputs to pullup.
##
################################################################################

def InitialiseGPIO () :

    # List of output pins.
    outputPins = (C.TEXECOM_NET1_EXP3_ZONE_29, C.TEXECOM_NET1_EXP3_ZONE_30,
                        C.TEXECOM_NET1_EXP3_ZONE_31, C.TEXECOM_NET1_EXP3_ZONE_32, C.STATUS_LED_1)

    # List of input pins.
    inputPins = (C.TEXECOM_NET1_EXP3_OUTPUT_4, C.TEXECOM_NET1_EXP3_OUTPUT_5,
                       C.TEXECOM_NET1_EXP3_OUTPUT_6, C.TEXECOM_NET1_EXP3_OUTPUT_7)

    # We are using board pin numbers.
    GPIO.setmode (GPIO.BOARD)
    
    # Initialise all the outputs, set them low. Note: high = active for outputs.
    for outputPin in outputPins :
    
        GPIO.setup (outputPin, GPIO.OUT)
        GPIO.output (outputPin, GPIO.LOW)
        
    # We need to keep the zone we are using for gate button chime high.
    GPIO.output (C.TEXECOM_NET1_EXP3_ZONE_29, GPIO.HIGH)
    
    # Initialise all the inputs, need pullups. Note: low = active for inputs.
    for inputPin in inputPins :
        GPIO.setup(inputPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

################################################################################
##
## Function: RemovePhoneNumberFromList (number)
##
## Parameters: number - string - the number to remove.
##
## Returns: string - the number added or error message if number error.
##
## Globals modified:
##
## Comments: Attempts to remove the number to our list of numbers. If the number was removed then it will be returned to
## the caller with a 'removed' message. If the number does not exist or is invalid we will return an error message. The caller
## can check the response and see if the 1st character is an 'E' for Error.
##
################################################################################

def RemovePhoneNumberFromList (number) :
 
    # Remove any leading or trailing whitespace. Then remove any spaces in the number.
    number = number.strip()
    number = number.replace(' ', '')
    
    # Load a default response error message
    responseMessage = 'Error ' + number + ' Invalid'
    
    # Have got to remove all numbers?
    if number == 'ALL' :
        # Simply clear the numbers list and return done message.
        G.calledNumbers = []
        return 'All numbers removed'
        
    # Single number so check if the correct length is present. 11 digits if it starts with zero, 13 if it starts with a +.
    if len (number) in (11, 13) :      
        # If 1st digit is a zero we will convert this to '+44'.
        if  number [0] == '0' :
            number = '+44' + number [1 : len (number)]
            
        # Check length, that it starts with + and that the rest is digits.
        if len (number) == 13 and number [0] == '+' and number [1 : 13].isdigit () :      
            # Check that it is in the list.
            if number in G.calledNumbers :       
                # Number is in the list so remove it and set removed response message.
                G.calledNumbers.remove (number)
                responseMessage = number + ' Removed'
            else:
                # Number not in list so return error message.
                responseMessage = 'Error ' + number + ' Unknown'               
            
    # Pass response message back to caller
    return responseMessage

################################################################################
##
## Function: CheckForValidNumber (numberList)
##
## Parameters: numberList - list of strings - the original data after the command. numberList [0] is the number.
##
## Returns: list of strings - the orignal list with a valid 13 digit number in [0] or empty list for a bad number.
##
## Globals modified:
##
## Comments: Attemps to create a valid number from the supplied list. The number will start at location 0 and could be
## broken into the following locations. E.g. the original command could be "Add 01963 220 623". If a number can be
## created it will be placed back in location 0 and a leading 0 will be replaced with +44. Any locations used after the 1st
## to create the number are removed from numberList any unused locations will be returned after the number.
##
################################################################################

def CheckForValidNumber (numberList) :

    # 1st make sure we have been given some data.
    if numberList :
        # Check for ALL numbers option. If it is pass it back.
        if numberList [0] == 'ALL' :
            return numberList
        
        # The number will start in numberList [0] and the 1st digit must be 0 or +. If it is 0 we will change it to +44.
        number = numberList [0]
        if number.startswith ('0') :
            number  = '+44' + number [1 : len (number)]
        
        # Only carry on if the number starts with +.
        if number.startswith ('+') :
            # We need to make a deep copy of the numberList as we will be removing locations in the for loop below.
            numberListCopy = deepcopy (numberList)
            # Now we will add any further locations until we get a 13 digit number. Location [0] is already used.
            for location in numberListCopy [1 : ] :
            
                # If we have 13 digits or more or the location is not all digits we exit.
                if len (number) >= 13 or not location.isdigit () :
                    break
                # Get here if valid location so append to number and remove from list.
                number += location
                numberList.remove (location)
                
            # If the number is the correct length and is all digits, excluding the +, return number to caller.
            if  len (number) == 13 and number [1:].isdigit () :
                numberList [0] = number
                return numberList
        
    # If we get here number is not valid so return empty list.
    return []


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

