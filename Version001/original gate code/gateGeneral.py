import commonNetControl as netControl

import commonStrings as STR
import gateConstants as C

import RPi.GPIO as GPIO

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
    outputPins = (C.START_GATE_OUTPUT, C.STOP_GATE_OUTPUT, C.PED_OUTPUT,
                        C.GREEN_LED_OUTPUT, C.RED_LED_OUTPUT,
                        C.DRIVE_LED_OUTPUT, C.FRONT_LED_OUTPUT, C.SIGN_LED_OUTPUT,
                        C.STATUS_LED_2, C.STATUS_LED_1)

    # List of input pins.
    inputPins = (C.GATE_MOVING_INPUT, C.STOP_CALL_BUTTON_INPUT, C.OPEN_CLOSE_BUTTON_INPUT,
    C.LEFT_GATE_CLOSED_SWITCH_INPUT, C.LEFT_GATE_OPEN_SWITCH_INPUT, C.RIGHT_GATE_CLOSED_SWITCH_INPUT,
    C.RIGHT_GATE_OPEN_SWITCH_INPUT, C.EXTERIOR_LIGHTS_RELAY_INPUT)

    # We are using board pin numbers.
    GPIO.setmode (GPIO.BOARD)
    
    # Initialise all the outputs, set them low. Note: high = active for outputs.
    for outputPin in outputPins :
    
        GPIO.setup (outputPin, GPIO.OUT)
        GPIO.output (outputPin, GPIO.LOW)
             
    # Initialise all the inputs, need pullups. Note: low = active for inputs.
    for inputPin in inputPins :
        GPIO.setup(inputPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

