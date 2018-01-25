import commonStrings as STR
import gateConstants as C

import time
import RPi.GPIO as GPIO

################################################################################
##
## Function: GateControl (command, status)
##
## Parameters: command - multiprocessing queue - 2 element tuple - the command parameters.
##                   status - multiprocessing queue - list - messages from gate control functions.
##
## Returns:
##
## Globals modified:
##
## Comments: This function is run as a process. This enables us to control the gate operation without constant sampling
## in the main program loop. Commands to control the gate are sent via a multiprocessing queue. Each command consists
## of 2 parameters. We use these parameters to lookup the gate function to call via a 2 dimensional array. Any messages
## from the gate functions are returned in a list via a multiprocessing queue to the main program. 
##
################################################################################

def GateControl (command, status) :

################################################################################

    def SetStartLineHigh () :
        GPIO.output (C.START_GATE_OUTPUT, GPIO.HIGH)
        
################################################################################

    def SetStartLineLow () :
        GPIO.output (C.START_GATE_OUTPUT, GPIO.LOW)
        timers [STR.START] = -1

################################################################################

    def SetStopLineHigh () :
        GPIO.output (C.STOP_GATE_OUTPUT, GPIO.HIGH)
        
################################################################################

    def SetStopLineLow () :
        GPIO.output (C.STOP_GATE_OUTPUT, GPIO.LOW)
        
################################################################################

    def SetPedLineHigh () :
        GPIO.output (C.PED_OUTPUT, GPIO.HIGH)
        
################################################################################

    def SetPedLineLow () :
        GPIO.output (C.PED_OUTPUT, GPIO.LOW)
        
################################################################################

    def CheckTimer (timer, action) :
        # Check a timer (timer) and if it has expired call a function (action).
        if timers [timer] >= 0 :
            timers [timer] -= 1
            if timers [timer] < 0 :
                action ()

################################################################################
 
    def AutoOpen (status) :
    
        # If both the gates are already open tell user and exit.
        if status [STR.RIGHT_GATE] == STR.OPEN and status [STR.LEFT_GATE] == STR.OPEN :
            return STR.GATES_OPEN
        
        # If the gates are being operated by the buttons or remotes tell user and exit.
        elif status [STR.BUTTON_OPEN] == STR.PRESSED or status [STR.BUTTON_STOP] == STR.PRESSED or status [STR.GATES] == STR.MOVING :
            return  STR.GATES_BUSY
        
        # We need to open the gates so set the start line to the gate controller high and start timer to turn it off.
        # There is no result to report yet so return none.
        else :
            SetStartLineHigh ()
            timers [STR.START] = 100
            status [STR.AUTO] = STR.OPEN 
            return None
        
################################################################################            
    def AutoClose (status) :
    
        # If both the gates are already closed tell user and exit.
        if status [STR.RIGHT_GATE] == STR.CLOSED and status [STR.LEFT_GATE] == STR.CLOSED :
            return STR.GATES_CLOSED
        
        # If the gates are being operated by the buttons or are already in use tell user and exit.
        elif (status [STR.BUTTON_OPEN] == STR.PRESSED or
               status [STR.BUTTON_STOP] == STR.PRESSED or
               status [STR.GATES] == STR.MOVING) :
            return STR.GATES_BUSY
        
        # We need to close the gates so set the start line to the gate controller high and start timer to turn it off.
        # There is no result to report yet so return none.
        else :
            SetStartLineHigh ()
            timers [STR.START] = 100
            status [STR.AUTO] = STR.CLOSE
            return None
        
################################################################################        
    def ButtonOpenPressed (status) :
    
        # One of the open buttons is pressed. If the gates are stationary this will start them in the opposite direction to the
        # last direction. If the gates are moving it will cause them to stop.
        status [STR.BUTTON_OPEN] = STR.PRESSED
        
        # Set the input to the gate controller start line high. Initialise timer to set it low in case button is held down.
        SetStartLineHigh ()
        timers [STR.START] = 100
        return STR.GATE_BUTTON_OPEN_PRESSED
        
################################################################################

    def ButtonOpenReleased (status) :
    
        # Both of the open buttons are released. This has no effect on the gates as the input to the gate controller is alternate
        # action and activates on the pressed condition.
        status [STR.BUTTON_OPEN] = STR.RELEASED
        
        # Set the input to the gate controller start line low and clear timer we started.
        SetStartLineLow ()
        return STR.GATE_BUTTON_OPEN_RELEASED
        
################################################################################

    def ButtonStopPressed (status) :
    
        # One of the stop buttons is pressed. If the gates are moving it will cause them to stop. The stop button and input to
        # the gate controller are both n/c.
        status [STR.BUTTON_STOP] = STR.PRESSED
        
        # Set the input to the gate controller stop line low.  The stop input is normally high. 
        # Initialise timer to set it high in case button is held down.
        SetStopLineLow ()
        timers [STR.STOP] = 100       
        return STR.GATE_BUTTON_STOP_PRESSED
        
################################################################################
 
    def ButtonStopReleased (status) :
    
        # Both of the stop buttons are released.
        status [STR.BUTTON_STOP] = STR.RELEASED
        
        # Set the input to the gate controller stop line high. Clear timer we started.
        SetStopLineHigh ()
        timers [STR.STOP] = -1
        return STR.GATE_BUTTON_STOP_RELEASED

################################################################################
     
    def ButtonPedPressed (status) :
    
        # If we are in pedestrian mode we treat the open buttons as ped buttons. In pedestrian mode we only partially open the
        # left gate and the right gate is kept closed.
        status [STR.BUTTON_PED] = STR.PRESSED
        
        # Set the input to the gate controller ped line high. Initialise timer to set it low if button is held down.
        SetPedLineHigh ()         
        timers [STR.PED] = 100
        return STR.GATE_BUTTON_PED_PRESSED
        
################################################################################

    def ButtonPedReleased (status) :
    
        status [STR.BUTTON_PED] = STR.RELEASED
        
        # Set the input to the gate controller ped line low. Clear timer we started.
        SetPedLineLow ()         
        timers [STR.PED] = -1
        return STR.GATE_BUTTON_PED_RELEASED
        
################################################################################

    def RightOpenSwitchActive (status) :
    
        # The right OPEN switch has signalled that the right gate is open. It will still be moving as the switch operates just
        # before gate is fully open. We do not return that the gate is open until we detect that the gate is stopped. The gate
        # stops via it's own internal limit switches, at which point we get a gate stopped signal.
        
        status [STR.RIGHT_GATE] = STR.OPEN_SWITCH      
        return STR.GATE_SWITCH_RIGHT_OPEN_ACTIVE

################################################################################
   
    def RightOpenSwitchInactive (status) :
    
        # The right OPEN switch has signalled that the right gate is NOT open. If it was previously open and the gate is
        # moving we will assume it is closing. If it was previously open and the gate is stopped we will assume it is being
        # forced closed. If the previous status is not open then we can ignore this as it was probably from our 1st
        # initialisation when we read the actual switch levels and not a change.

        if status [STR.RIGHT_GATE] == STR.OPEN : 
            if status [STR.GATES] == STR.MOVING :
                status [STR.RIGHT_GATE] = STR.CLOSING
                return STR.GATE_RIGHT_CLOSING
            else :
                status [STR.RIGHT_GATE] = None
                return STR.GATE_RIGHT_FORCED
            
        # State of gate unkown so just return switch status.
        return STR.GATE_SWITCH_RIGHT_OPEN_INACTIVE
        
################################################################################
    
    def RightClosedSwitchActive (status) :
    
        # The right CLOSED switch has signalled that the right gate is closed. It will still be moving as the switch operates just
        # before gate is fully closed. We do not return that the gate is closed until we detect that the gate is stopped. The gate
        # stops via it's own internal limit switches, at which point we get a gate stopped signal.
        
        status [STR.RIGHT_GATE] = STR.CLOSED_SWITCH       
        return STR.GATE_SWITCH_RIGHT_CLOSED_ACTIVE

################################################################################

    def RightClosedSwitchInactive (status) :
    
        # The right CLOSED switch has signalled that the right gate is NOT closed. If it was previously closed and the gate is
        # moving we will assume it is opening. If it was previously closed and the gate is stopped we will assume it is being
        # forced open. If the previous status is not closed then we can ignore this as it was probably from our 1st
        # initialisation when we read the actual switch levels and not a change.

        if status [STR.RIGHT_GATE] == STR.CLOSED : 
            if status [STR.GATES] == STR.MOVING :
                status [STR.RIGHT_GATE] = STR.OPENING
                return STR.GATE_RIGHT_OPENING
            else :
                status [STR.RIGHT_GATE] = None
                return STR.GATE_RIGHT_FORCED
            
        # State of gate unkown so just return switch status.
        return STR.GATE_SWITCH_RIGHT_CLOSED_INACTIVE

################################################################################
    
    def LeftOpenSwitchActive (status) :
    
        # The left OPEN switch has signalled that the left gate is open. It may still be moving as the switch operates just
        # before gate is fully open. We do not return that the gate is open until we detect that the gate is stopped. The gate
        # stops via it's own internal limit switches, at which point we get a gate stopped signal.
        
        status [STR.LEFT_GATE] = STR.OPEN_SWITCH      
        return STR.GATE_SWITCH_LEFT_OPEN_ACTIVE

################################################################################

    def LeftOpenSwitchInactive (status) :
    
        # The left OPEN switch has signalled that the left gate is NOT open. If it was previously open and the gate is
        # moving we will assume it is closing. If it was previously open and the gate is stopped we will assume it is being
        # forced closed. If the previous status is closed or unknown then we can ignore this as it was probably from our 1st
        # initialisation when we read the actual switch levels and not a change.

        if status [STR.LEFT_GATE] == STR.OPEN : 
            if status [STR.GATES] == STR.MOVING :
                status [STR.LEFT_GATE] = STR.CLOSING
                return STR.GATE_LEFT_CLOSING
            else :
                status [STR.LEFT_GATE] = None
                return STR.GATE_LEFT_FORCED
            
        # State of gate unkown so just return switch status.
        return STR.GATE_SWITCH_LEFT_OPEN_INACTIVE

################################################################################

    def LeftClosedSwitchActive (status) :
    
        # The left CLOSED switch has signalled that the left gate is closed. It will still be moving as the switch operates just
        # before gate is fully closed. We do not return that the gate is closed until we detect that the gate is stopped. The gate
        # stops via it's own internal limit switches, at which point we get a gate stopped signal.
        
        status [STR.LEFT_GATE] = STR.CLOSED_SWITCH       
        return STR.GATE_SWITCH_LEFT_CLOSED_ACTIVE

################################################################################

    def LeftClosedSwitchInactive (status) :
    
        # The left CLOSED switch has signalled that the left gate is NOT closed. If it was previously closed and the gate is
        # moving we will assume it is opening. If it was previously closed and the gate is stopped we will assume it is being
        # forced open. If the previous status is open or unknown then we can ignore this as it was probably from our 1st
        # initialisation when we read the actual switch levels and not a change.

        if status [STR.LEFT_GATE] == STR.CLOSED : 
            if status [STR.GATES] == STR.MOVING :
                status [STR.LEFT_GATE] = STR.OPENING
                return STR.GATE_LEFT_OPENING
            else :
                status [STR.LEFT_GATE] = None
                return STR.GATE_LEFT_FORCED

        # State of gate unkown so just return switch status.
        return STR.GATE_SWITCH_LEFT_CLOSED_INACTIVE

################################################################################

    def GatesMoving (status) :
        # The gate controller has signalled that the gates have started moving. If a gate was halted this indicates that the gate
        # was stopped either by the buttons, remote control or an obstruction. In this case we will set the gate status to the
        # opposite of the halted state as we will assume the gate will move in that direction.
       
        #Flag gates are moving and because they are we can set the start line low as the controller has seen the start line high.
        status [STR.GATES] = STR.MOVING
        SetStartLineLow ()
        
        # Use a lookup to get the new status for the gates and a return message.
        newStatus = {
            STR.CLOSING_HALTED : (STR.OPENING, STR.GATES_OPENING),
            STR.OPENING_HALTED : (STR.CLOSING, STR.GATES_CLOSING)
        }
        # If the gates were not halted we return with no message so initialise it here.
        message = None

        # Check both gates and if they were halted get new status and message. It does not matter that message is overwritten
        # 2nd time through as both gates are going to be opening or closing.
        for gate in (STR.RIGHT_GATE, STR.LEFT_GATE) :    
            if status [gate] in newStatus :
                status [gate], message = newStatus [status [gate]]

        return message

################################################################################

    def GatesStopped (status) :
        # The gate controller has signalled that the gates have stopped moving. If a gate is opening or closing this indicates that
        # the gate was stopped either by the buttons, remote control or an obstruction. In this case we will set the gate status to
        # indicate whether the gate was stopped opening or closing. This will enable us to determine which direction the gate will
        # move the next time it starts moving. When we detect that the gates are open or closed we will see if we were doing
        # an auto open or close operation. If we find the gates are in the wrong state we will restart them so that they will
        # move to the correct state.
       
        #Flag gates are stopped and because they are we can set the start line low as the controller has seen the start line high.
        status [STR.GATES] = STR.STOPPED
        SetStartLineLow ()

        # Use a lookup to get the new status for the gates and a return message.
        statusLookup = {
            STR.CLOSING : (STR.CLOSING_HALTED, STR.GATES_HALTED),
            STR.OPENING : (STR.OPENING_HALTED, STR.GATES_HALTED),
            STR.CLOSED : (STR.CLOSED, STR.GATES_CLOSED),
            STR.OPEN : (STR.OPEN, STR.GATES_OPEN),
            STR.CLOSED_SWITCH : (STR.CLOSED, STR.GATES_CLOSED),
            STR.OPEN_SWITCH : (STR.OPEN, STR.GATES_OPEN)
        }

        # Somewhere to put messages if we match a status
        messages = []

        # Check both gates and if they were open, closed, opening, closing or setting switches get new status and message.
        # Note "status" is a reference parameter so we are updating the callers copy.
        for gate in (STR.RIGHT_GATE, STR.LEFT_GATE) :    
            if status [gate] in statusLookup :
                status [gate], message = statusLookup [status [gate]]
                messages.append (message)
                
        # If a gate has been halted tell user. It dosen't matter which gate was halted.
        if STR.GATES_HALTED in messages :
            return STR.GATES_HALTED
            
        # If we get here with 2 messages they must both be opened or closed so check if we also have an auto status.
        # If we have make sure gates have gone the correct way and if not restart them so they go to the correct state.
        if len (messages) == 2 :
            if ((messages [0] == STR.GATES_CLOSED and status [STR.AUTO]  == STR.OPEN) or
                (messages [0] == STR.GATES_OPEN and status [STR.AUTO]  == STR.CLOSE)) :
                SetStartLineHigh ()
                timers [STR.START] = 100
                return STR.GATES_RESTARTING
            else :
                status [STR.AUTO] = None
        
            # Get here with both gates opened or closed
            return messages [0]
        
        return None
        
################################################################################

    # Timers to check if the gates complete the required operation and to terminate the start, stop and ped signal to the controller.
    timers = {STR.OPEN : -1, STR.CLOSE : -1, STR.START : -1, STR.STOP : -1, STR.PED : -1}
 
    # Create a 2 dimension dictionary. This is used to lookup the function to call for each 2 element tuple command
    # that we receive.
    commandLookup = {
        STR.OPEN : {STR.GATES : AutoOpen},
        STR.CLOSE : {STR.GATES : AutoClose},
        STR.AUTO : {STR.OPEN : AutoOpen, STR.CLOSE : AutoClose},
        STR.BUTTON_OPEN : {STR.PRESSED : ButtonOpenPressed, STR.RELEASED : ButtonOpenReleased},
        STR.BUTTON_STOP : {STR.PRESSED : ButtonStopPressed, STR.RELEASED : ButtonStopReleased},
        STR.BUTTON_PED : {STR.PRESSED : ButtonPedPressed, STR.RELEASED : ButtonPedReleased},
        STR.GATES : {STR.MOVING : GatesMoving, STR.STOPPED : GatesStopped},        
        STR.SWITCH_RIGHT_OPEN : {STR.ACTIVE : RightOpenSwitchActive, STR.INACTIVE : RightOpenSwitchInactive},
        STR.SWITCH_RIGHT_CLOSED : {STR.ACTIVE : RightClosedSwitchActive, STR.INACTIVE : RightClosedSwitchInactive},
        STR.SWITCH_LEFT_OPEN : {STR.ACTIVE : LeftOpenSwitchActive, STR.INACTIVE : LeftOpenSwitchInactive},
        STR.SWITCH_LEFT_CLOSED : {STR.ACTIVE : LeftClosedSwitchActive, STR.INACTIVE : LeftClosedSwitchInactive}
    }
    # Flags for button and gate status.
    statusFlags = { 
        STR.AUTO : None, STR.BUTTON_OPEN : None, STR.BUTTON_STOP : None, STR.BUTTON_PED : None,
        STR.GATES : None, STR.RIGHT_GATE : None, STR.LEFT_GATE : None
    }

    while 1 :
        # We will sample everything at about 20mS intervals.
        time.sleep (0.02)
        
        # If we have got a command use the 2 parameters to lookup dictionary and get function to call. We pass the
        # the current status flags to the function. 
        if not command.empty () : 
            # Get the 2 parameters from the command tuple.
            p1, p2 = command.get ()
            # Call the required function, pass status flags and get return message.
#            result = commandLookup [p1] [p2] (commandLookup [STR.STATUS])
            result = commandLookup [p1] [p2] (statusFlags)
            if result :
                status.put (result)
##                print result
##            print commandLookup [STR.STATUS],'\n\r'
            
        # Check the start line timer. Set start line low if it has expired.
        CheckTimer (STR.START, SetStartLineLow)
        # Check the stop line timer. Set stop line high if it has expired.
        CheckTimer (STR.STOP, SetStopLineHigh)
        # Check the ped line timer. Set ped line low if it has expired.
        CheckTimer (STR.PED, SetPedLineLow)

        
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


