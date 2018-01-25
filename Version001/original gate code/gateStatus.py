import commonStrings as STR
import gateConstants as C
import gateGeneral as general

import RPi.GPIO as GPIO

class rpiLine :

    def __init__ (self, pin, pinLow, pinHigh) :
    
        # Rpi pin number.
        self.ioLine = pin
        # Status to return if line is low.
        self.pinLowMessage = pinLow
        # Status to return if line is high.
        self.pinHighMessage = pinHigh
        # Last state of the pin. Set to unknown.
        self.lastState = -1
        # Debounce timer. Set to idle.
        self.timer = -1

    def CheckLine (self, changedOnly = True) :
    
        # Initialise flag that we will return to indicate status.
        lineStatus = None
        
        # Get state of line.
        lineState = GPIO.input(self.ioLine)
        
        # If changedOnly is True this function will need to be called in a loop so that the lines are debounced. We need
        # to debounce as some inputs are from switches.
        if changedOnly :
            # Has input changed state?
            if lineState != self.lastState :
                # Line has changed state. Is debounce timer running? This would mean we have already detected the change and # are debouncing the line.
                if self.timer > 0 :
                    # Input has changed state and timer is running so we decrement the timer to debounce line.
                    self.timer -= 1
                # Is debounce timer idle?
                elif self.timer < 0 :           
                    # Line has changed state and timer is idle so we must start it.
                    self.timer = 5               
                else :
                    # Line has changed state and timer has expired (zero) so we set timer to idle. We now save the new state and
                    # set line status to indicate if the line is high or low. If lastState is -ve this means this is our 1st time so we
                    # will simply set the new state and not flag a change.
                    if self.lastState >= 0 :
                        lineStatus = 'Required'
                    self.timer = -1
                    self.lastState = lineState
            else :     
                # Line has not changed state so put debounce timer to idle. This means that if line bounces we will reset the timer.
                self.timer = -1
        else :
            # We just want the actual state of a line.
            lineStatus = 'Required'
            
        # If we have to return line status send message according to level.
        if lineStatus :
            lineStatus = self.pinHighMessage if lineState == GPIO.HIGH else self.pinLowMessage
        
        return lineStatus
        
        
# Use  rpiLine class to initialise each rpi line status. Build a dictionary with the rpi line number as the key and the
# instance as the value.  
rpiLines = {
    C.GATE_MOVING_INPUT : rpiLine (C.GATE_MOVING_INPUT,
                                                     STR.GATES_ARE_MOVING,
                                                     STR.GATES_ARE_STOPPED),
                                             
    C.STOP_CALL_BUTTON_INPUT : rpiLine (C.STOP_CALL_BUTTON_INPUT,
                                                             STR.BUTTON_STOP_RELEASED,
                                                             STR.BUTTON_STOP_PRESSED), 
                                                 
    C.OPEN_CLOSE_BUTTON_INPUT : rpiLine (C.OPEN_CLOSE_BUTTON_INPUT,
                                                               STR.BUTTON_OPEN_PRESSED,
                                                               STR.BUTTON_OPEN_RELEASED),
                                                     
    C.LEFT_GATE_CLOSED_SWITCH_INPUT : rpiLine (C.LEFT_GATE_CLOSED_SWITCH_INPUT,
                                                                          STR.SWITCH_LEFT_CLOSED_ACTIVE,
                                                                          STR.SWITCH_LEFT_CLOSED_INACTIVE),
                                                          
    C.LEFT_GATE_OPEN_SWITCH_INPUT : rpiLine (C.LEFT_GATE_OPEN_SWITCH_INPUT,
                                                                       STR.SWITCH_LEFT_OPEN_ACTIVE,
                                                                       STR.SWITCH_LEFT_OPEN_INACTIVE),
                                                         
    C.RIGHT_GATE_CLOSED_SWITCH_INPUT : rpiLine (C.RIGHT_GATE_CLOSED_SWITCH_INPUT,
                                                                            STR.SWITCH_RIGHT_CLOSED_ACTIVE,
                                                                            STR.SWITCH_RIGHT_CLOSED_INACTIVE),
                                                             
    C.RIGHT_GATE_OPEN_SWITCH_INPUT : rpiLine (C.RIGHT_GATE_OPEN_SWITCH_INPUT,
                                                                         STR.SWITCH_RIGHT_OPEN_ACTIVE,
                                                                         STR.SWITCH_RIGHT_OPEN_INACTIVE),
                                                          
    C.EXTERIOR_LIGHTS_RELAY_INPUT : rpiLine (C.EXTERIOR_LIGHTS_RELAY_INPUT,
                                                                     STR.EXTERIOR_LIGHTS_ON,
                                                                     STR.EXTERIOR_LIGHTS_OFF),
    
    C.START_GATE_OUTPUT : rpiLine (C.START_GATE_OUTPUT,
                                                     STR.OUTPUT_START_IS_OFF,
                                                     STR.OUTPUT_START_IS_ON),
                                   
    C.STOP_GATE_OUTPUT : rpiLine (C.STOP_GATE_OUTPUT,
                                                   STR.OUTPUT_STOP_IS_OFF,
                                                   STR.OUTPUT_STOP_IS_ON),
                                                   
    C.PED_OUTPUT : rpiLine (C.PED_OUTPUT,
                                        STR.OUTPUT_PED_IS_OFF,
                                        STR.OUTPUT_PED_IS_ON),
                                        
    C.GREEN_LED_OUTPUT : rpiLine (C.GREEN_LED_OUTPUT,
                                                   STR.OUTPUT_GREEN_IS_OFF,
                                                   STR.OUTPUT_GREEN_IS_ON),
                                                   
    C.RED_LED_OUTPUT : rpiLine (C.RED_LED_OUTPUT,
                                               STR.OUTPUT_RED_IS_OFF,
                                               STR.OUTPUT_RED_IS_ON),
                                               
    C.DRIVE_LED_OUTPUT : rpiLine (C.DRIVE_LED_OUTPUT,
                                                   STR.OUTPUT_DRIVE_IS_OFF,
                                                   STR.OUTPUT_DRIVE_IS_ON),
                                                   
    C.FRONT_LED_OUTPUT : rpiLine (C.FRONT_LED_OUTPUT,
                                                   STR.OUTPUT_FRONT_IS_OFF,
                                                   STR.OUTPUT_FRONT_IS_ON),
                                                   
    C.SIGN_LED_OUTPUT : rpiLine (C.SIGN_LED_OUTPUT,
                                                 STR.OUTPUT_SIGN_IS_OFF,
                                                 STR.OUTPUT_SIGN_IS_ON)
}

################################################################################
##
## Function: CheckRpiLines (changed = True)
##
## Parameters:  changed - boolean - if true report only changes, defaults to true.
##                    
##
## Returns:       list of all mesages sent.
##
## Globals modified:
##
## Comments: Check each of the rpi GPIO lines and send state of line message to user.
##
################################################################################

def CheckRpiLines (changed = True) :

    # Initialise list that will contain all the messages sent that we will return to caller.
    messageList = []
    
    # Check all GPIO lines.
    for line in rpiLines :

        # Get state of line. If changed was passed False we will report every input line. No debounce done.
        lineStatus = rpiLines [line].CheckLine (changed)
        
        # Have we got a status to send?
        if lineStatus :
            # Put message in list.
            messageList.append (lineStatus)
            
    # Send list of any status messages back to the caller.
    return messageList       


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


