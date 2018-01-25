print 'Loaded system module'

import GD
import zones

################################################################################
##
## Class: systemControlBit
##
## Parameters: 
##
## Methods:
##
## Globals modified:
##
## Comments: Control bits can be input, output or configuration bits. For each I/O control bit we keep the I2C address and bit
## location. The value of the control bit is controlled by two status bits. The current status bit is the value required by normal
## system operation. The override status bit is controlled by manual operations and will override the current status whenever
## the override bit is active.
##
################################################################################

class systemControlBit :

    # When we are displaying control status we keep the index for the status being displayed here.
    statusIndex = 0

    def __init__ (self, text, state, address, bit, override, timer) :
        self.displayText = text
        # Bit to indicate status: 1 = high, 0 = low.
        self.currentStatus = state
        # Last status.
        self.previousStatus = -1
        # I2C address.
        self.ioAddress = address
        # Bit set for location in byte.
        self.bitMask = bit
        # Manual operations will set this flag to override normal status: 2 = no override, 1 = force high, 0 = force low.
        self.overrideStatus = override
        # Each bit has a timer for use on pulsed outputs or for debouncing inputs
        self.timerStatus = timer
        
    def SaveStatusIndex (self, index) :
        self.statusIndex = index
        
    def GetStatusIndex (self) :
        return self.statusIndex
        
#    def IncrementStatusIndex (self) :
 #       self.statusIndex += 1
  #      return self.statusIndex
        
#    def DecrementStatusIndex (self) :
 #       self.statusIndex -= 1
  #      return self.statusIndex
        
    def GetDisplayText (self) :
        return self.displayText
        
    def GetAddress (self) :
        return self.ioAddress
        
    def GetBitMask (self) :
        return self.bitMask
        
    def SetOutputBitHigh (self) :
        # Flag we want the output high.
        self.currentStatus = GD.BIT_HIGH
        # If the override status was high clear the override flag as the actual required state is now high.
        if self.overrideStatus == GD.BIT_HIGH :
            self.overrideStatus = GD.BIT_OVERRIDE_NONE
                
        # We check to see if this is a pulsed line. If it is we will set the pulse period. We also need to clear the last status so that
        # the relay code will detect that we need to pulse the line. This is because status is used to hold the last action and so if
        # the last action had been a high the relay code would perform no action as it would assume the line was already high.
        if self.timerStatus != GD.BIT_NOT_TIMED :
            # Pulsed line so set timer and clear last status.
            self.timerStatus = GD.BIT_SET_TIMING_60
            self.previousStatus = GD.BIT_LOW 
            
        # Tell caller if we actually changed the bit.
        return self.CheckIfBitChanged ()

    def SetOutputBitLow (self) :
        self.currentStatus = GD.BIT_LOW
        # If the override status was low clear the override flag as the actual required state is now low.
        if self.overrideStatus == GD.BIT_LOW :
            self.overrideStatus = GD.BIT_OVERRIDE_NONE
        
        # Tell caller if we actually changed the bit.
        return self.CheckIfBitChanged ()

    def SetOutputOverrideBitHigh (self) :
        # We check to see if this is a pulsed line. If it is we will set the pulse period. We also need to clear the last status so that
        # the relay code will detect that we need to pulse the line. This is because status is used to hold the last action and so if
        # the last action had been a high the relay code would perform no action as it would assume the line was already high.
        if self.timerStatus != GD.BIT_NOT_TIMED :
            # Pulsed line so set timer and clear last status.
            self.timerStatus = GD.BIT_SET_TIMING_60
            self.previousStatus = GD.BIT_LOW 

            # Only set override high if bit is low. If the bit is already high there is nothing to do
        if self.currentStatus == GD.BIT_LOW :
            self.overrideStatus = GD.BIT_OVERRIDE_HIGH

                # Return true as we have changed level.
            return True
        else :
            # We are already high so clear override because if we are already in override this is a request to stop a low override.
            self.overrideStatus  = GD.BIT_OVERRIDE_NONE

            # We return false as we have now restored the bit to the original state.
            return False
        
    def SetOutputOverrideBitLow (self) :
        # Only set override if bit is NOT already in state required (low).
        if self.currentStatus != GD.BIT_LOW :
            self.overrideStatus = GD.BIT_OVERRIDE_LOW
            return True
        else :
            # If we are already in override this is a request to stop a high override.
            self.overrideStatus  = GD.BIT_OVERRIDE_NONE
            # We return false as we have now restored the bit to the original state.
            return False

    def SetOverrideNone (self) :
        self.overrideStatus  = GD.BIT_OVERRIDE_NONE
        
    def CheckIfBitChanged (self) :
        if self.overrideStatus  == GD.BIT_OVERRIDE_NONE :
            return self.currentStatus != self.previousStatus
        else :
            return self.overrideStatus != self.previousStatus

    def CheckIfBitHigh (self) :
        if self.overrideStatus  == GD.BIT_OVERRIDE_NONE :
            return self.currentStatus == GD.BIT_HIGH
        else :
            return self.overrideStatus == GD.BIT_OVERRIDE_HIGH
            
    def CheckIfOverrideActive (self) :
        return self.overrideStatus  != GD.BIT_OVERRIDE_NONE
        
    def UpdateBitChangedStatus (self) :
        if self.overrideStatus  == GD.BIT_OVERRIDE_NONE :
            self.previousStatus = self.currentStatus
        else :
            self.previousStatus = self.overrideStatus
            
    def CheckIfBitTimerFinished (self) :
        # A timer is +ve if it is active, zero (BIT_TIMING_FINISHED) when finished and -ve (BIT_NOT_TIMED) for not used.
        # If the timer is active we decrement it and return true if we timed out.
        if self.timerStatus > GD.BIT_TIMING_FINISHED :
            self.timerStatus  -= 1
            if self.timerStatus  == GD.BIT_TIMING_FINISHED :
                return True
                
        return False
                
    def UpdateInputBit (self, newState) :
        # Check if value has changed
        if newState != self.CheckIfBitHigh () :
            # Value changed so update timer. If it has finished set the new value and reset timer.
            if self.CheckIfBitTimerFinished () == True :
                self.previousStatus = self.currentStatus
                self.currentStatus = newState
                self.timerStatus = GD.BIT_SET_TIMING_05
    
                print newState, self.GetDisplayText ()
        else :
            # Value not changed so reset timer. This will also debounce changing input.
            self.timerStatus = GD.BIT_SET_TIMING_05
                
        # If this is not a timed line or it has previously timed out return false
        return False
        
    def UpdateTemperature (self, newState) :
        self.previousStatus = self.currentStatus
        self.currentStatus = newState

    def GetTemperature (self) :
        return self.currentStatus
        

        
################################################################################
##
## Function: WoodburnerPumpControl ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: The woodburner components consist of 2 pumps, a flow sensor and 2 temperature sensors. The temperature
## sensors are mounted on the flow and return pipes adjacent to the woodburner. The 2 pumps are connected in series such
## that either pump can generate the flow through the woodburner. This gives us a fail safe option so that in the event of 1
## pump failing we can use the other. The flow sensor is in series with the pumps to detect that a pump is operating and
## producing flow.
## The operation is as follows: When we detect that the flow is 5 degrees greater than return temperature we activate a pump.
## When the flow is less than 2 degrees greater than the return temperature we stop the pump. Each pump is used alternately
## to avoid pump sticking from non use. When a pump is activated we will check that flow starts. If flow does not start we
## will start the other pump and generate an alarm to warn of the pump failure.
## We will call this code once a second on our main timer tick.
##
################################################################################

def WoodburnerPumpControl () :

    # Pump status values.
    pump1LastOn = 0
    pump2LastOn = 1
    pump1OnWaitingFlow = 2
    pump2OnWaitingFlow = 3
    pump1On = 4
    pump2On = 5
    pumpFail = 6
    # Delay times in seconds.
    flowDelayTime = 10
    pumpOnTime = 300
    pumpOffTime = 30
    # Temperature trip values in degrees C.
    startDifference = 3
    stopDifference = 1
    
    # Initialise our status and delay timer 1st time through. This creates pseudo static/globals.
    # woodburnerStatus holds the current state of the woodburner hardware. E.g. pump 1 on, flow detected etc.
    # Start with pumps off, say pump 1 was last on.
    if 'woodburnerStatus' not in WoodburnerPumpControl.__dict__:
        WoodburnerPumpControl.woodburnerStatus = pump1LastOn
    
    # We use woodburnerDelay to time how long the pump will operate after it is activated and also to time the delay from
    # starting a pump to checking if flow has started.
    # Start with a delay to give time for the sensors to be read a 1st time.
    if 'woodburnerDelay' not in WoodburnerPumpControl.__dict__:
        WoodburnerPumpControl.woodburnerDelay = 10
    
    # Check if it time to do something?
    if WoodburnerPumpControl.woodburnerDelay <= 0 :
    
        # Get the flow and return temperatures.
        flowTemperature = systemControl [GD.SYSTEM_WOODBURNER_FLOW_TEMP].GetTemperature ()
        returnTemperature = systemControl [GD.SYSTEM_WOODBURNER_RETURN_TEMP].GetTemperature ()
        temperatureDifference = flowTemperature - returnTemperature

        # Are we waiting to start a pump and flow pipe temperature exceeds return pipe temperature by X?
        if WoodburnerPumpControl.woodburnerStatus in (pump1LastOn, pump2LastOn) and temperatureDifference > startDifference :
        
            # Was pump 1 on last? 
            if WoodburnerPumpControl.woodburnerStatus == pump1LastOn :
                # Pump 1 on last so start pump 2.
                systemControl [GD.SYSTEM_WOODBURNER_PUMP_2].SetOutputBitHigh ()
                # Flag we are waiting for flow detect.
                WoodburnerPumpControl.woodburnerStatus = pump2OnWaitingFlow          
                print 'pump 2 on waiting flow'
                
            else :
                # Pump 2 on last so start pump .
                systemControl [GD.SYSTEM_WOODBURNER_PUMP_1].SetOutputBitHigh ()
                # Flag we are waiting for flow detect.
                WoodburnerPumpControl.woodburnerStatus = pump1OnWaitingFlow              
                print 'pump 1 on waiting flow'

            # Set delay to give pumps time to get flow started.
            WoodburnerPumpControl.woodburnerDelay = flowDelayTime
            
        # Are we waiting to detect flow after starting a pump?
        elif WoodburnerPumpControl.woodburnerStatus in (pump1OnWaitingFlow, pump2OnWaitingFlow) :
        
            # Set delay to give pumps a run time of X.
            WoodburnerPumpControl.woodburnerDelay = pumpOnTime
            
            # Have we got flow?
            if systemControl [GD.SYSTEM_WOODBURNER_FLOW_DETECT].CheckIfBitHigh () == True :
            
                # We have flow so flag the appropriate pump on.
                if WoodburnerPumpControl.woodburnerStatus == pump1OnWaitingFlow :
                    WoodburnerPumpControl.woodburnerStatus = pump1On                   
                    print 'pump 1 on'
                    
                else :
                    WoodburnerPumpControl.woodburnerStatus = pump2On                   
                    print 'pump 2 on'

            # No flow detected so start both pumps and sound alarm.
            else :
                systemControl [GD.SYSTEM_WOODBURNER_PUMP_1].SetOutputBitHigh ()
                systemControl [GD.SYSTEM_WOODBURNER_PUMP_2].SetOutputBitHigh ()
                WoodburnerPumpControl.woodburnerStatus = pumpFail
                print 'pump fail'
                
                ## TODO: START ALARM

        # Is a pump on and the flow temperature does not exceed the return temperature by X?
        elif WoodburnerPumpControl.woodburnerStatus in (pump1On, pump2On, pumpFail) and temperatureDifference < stopDifference :

            # Set delay to give pumps off time of X.
            WoodburnerPumpControl.woodburnerDelay = pumpOffTime
            
            # Turn appropriate pump(s) off.
            if WoodburnerPumpControl.woodburnerStatus == pump1On :
                WoodburnerPumpControl.woodburnerStatus = pump1LastOn
                systemControl [GD.SYSTEM_WOODBURNER_PUMP_1].SetOutputBitLow ()               
                print 'pump 1 off'
                
            elif WoodburnerPumpControl.woodburnerStatus == pump2On :
                WoodburnerPumpControl.woodburnerStatus = pump2LastOn
                systemControl [GD.SYSTEM_WOODBURNER_PUMP_2].SetOutputBitLow ()               
                print 'pump 2 off'
            
            else :
                WoodburnerPumpControl.woodburnerStatus = pump1LastOn
                systemControl [GD.SYSTEM_WOODBURNER_PUMP_1].SetOutputBitLow ()               
                systemControl [GD.SYSTEM_WOODBURNER_PUMP_2].SetOutputBitLow ()
                print ' fail off'

                
                    
    # Timer still non zero so decrement it.
    else :
        WoodburnerPumpControl.woodburnerDelay -= 1

    
################################################################################
##
## Function: Tank1PumpControl ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: Tank1 pump performs 2 functions. When HW is required it turns on to pump water from tank 1 through the HW
## heat exchanger. When either immersion 1 or 2 are heating tank 1 it turns on to circulate the water in tank 1 so that the
## entire tank is heated.
##
## TODO: LEAVE PUMP ON FOR 5 MINUTES AFTER BOTH IMMERSIONS REACH MAX.
##
################################################################################

def Tank1PumpControl () :

    # The tank 1 pump is on if we have HW demand or either immersion 1 or 2 is on and heating. Note that system inputs are
    #  inverted in the hardware so a low config input means on.
    # Set the pump bit off by default. This does not physically turn the pump off, it only clears the config bit.
    systemControl [GD.SYSTEM_TANK_1_PUMP].SetOutputBitLow ()
    # Is the system enabled (any mode except off)?
    if systemControl [GD.SYSTEM_OFF_MODE].CheckIfBitHigh () == False :
        # System is on.
        # Have we got HW demand? 
        if systemControl [GD.SYSTEM_HW_DEMAND].CheckIfBitHigh () == True :
            # HW demand so turn pump on.
            systemControl [GD.SYSTEM_TANK_1_PUMP].SetOutputBitHigh ()
            
        #Is immersion 1 on and not at max temperature?
        elif (systemControl [GD.SYSTEM_IMM_1].CheckIfBitHigh () == True
                and 
                systemControl [GD.SYSTEM_IMM_1_MAX].CheckIfBitHigh () == False) :
            # Immersion 1 is on and not at max temperature so turn pump on.
            systemControl [GD.SYSTEM_TANK_1_PUMP].SetOutputBitHigh ()
            
        #Is immersion 2 on and not at max temperature?
        elif (systemControl [GD.SYSTEM_IMM_2].CheckIfBitHigh () == True
                and 
                systemControl [GD.SYSTEM_IMM_2_MAX].CheckIfBitHigh () == False) :
            # Immersion 2 is on and not at max temperature so turn pump on.
            systemControl [GD.SYSTEM_TANK_1_PUMP].SetOutputBitHigh ()
            
        else :
            systemControl [GD.SYSTEM_TANK_1_PUMP].SetOutputBitLow ()


################################################################################
##
## Function: GetActiveSystemBit (bitGroup)
##
## Parameters: bitGroup - tuple - the group of bits to scan
##
## Returns: integer - the active bit
##
## Globals modified:
##
## Comments: Scans through the group of supplied system bits and returns the bit that is active high. It is assumed the bits
## are mutually exclusive as only the first bit found to be high is returned.
##
################################################################################

def GetActiveSystemBit (bitGroup) :

    for systemBit in bitGroup :
        if systemControl [systemBit].CheckIfBitHigh () == True :       
            # Exit with bit now we have found the active mode.
            return systemBit
            
    # Error exit.
    return GD.SYSTEM_NONE

################################################################################
##
## Function: ConfigureOutputBits (configBit)
##
## Parameters: configBit - integer - the configuration bit that we are setting outputs for
##
## Returns:
##
## Globals modified:
##
## Comments: Sets all the outputs to the levels required for a particular mode. E.g. for boiler to heating we will set valves 1 and
## 3 to connect the boiler to heating, turn on the boiler and tank2 pump. We hold all the output bits and levels required for a
## particular configuration bit in a lookup table. Note that there is interaction between the various modes and the configuration
## of the heating should be done before the configuration of the boiler as configuring the heating will turn the boiler off in
## some modes.
##
################################################################################

def ConfigureOutputBits (configBit) :

    # This table holds the values to set outputs to for the mode required. For each mode there is a list of bit, value pairs that
    # we can sequence through to set the outputs to the levels specified.
    # Note that we do not control all outputs here. The immersions, rad and ufh pumps will turn off when the zones shut down.
    # Tank 1 pump will not operate in off mode and therefore there will be no hot water.
    # The woodburner temperture sensors are always set on. This is to ensure the woodburner pumps will operate in case it
    # is lit with the system turned off.
    outputConfigurationLookUp = {
    
        ## SYSTEM OFF
        
        # Set outputs to idle or off state.
        GD.SYSTEM_OFF_MODE : (GD.SYSTEM_V1_EXT_TO_TANK_1, GD.BIT_HIGH,
                                               GD.SYSTEM_TANK_2_PUMP, GD.BIT_LOW,
                                               GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_LOW,
                                               GD.SYSTEM_BOILER_ON, GD.BIT_LOW),
        
       ## MANUAL MODE

       # For tank1 to heating we set valve 1 for ext to tank1 which also sets tank1 to heating.     
        GD.SYSTEM_MANUAL_TANK_1_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_TANK_1, GD.BIT_HIGH,
                                                                             GD.SYSTEM_TANK_2_PUMP, GD.BIT_LOW,
                                                                             GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_LOW),
        
        # For tank2 to heating we set valve 1 for ext to heating and set tank2 pump on.
        GD.SYSTEM_MANUAL_TANK_2_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_HEATING, GD.BIT_HIGH,
                                                                             GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                             GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_LOW),
 
        # For boiler to heating we set valve 1 for ext to heating, set tank2 pump on, set valve3 for boiler to int and turn boiler on.
        GD.SYSTEM_MANUAL_OIL_BOILER_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_HEATING, GD.BIT_HIGH,
                                                                                   GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                                   GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_HIGH,
                                                                                   GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),

        # For boiler to tank1 we set valve 1 for ext to tank1, set tank2 pump on, set valve3 for boiler to int and turn boiler on.
        GD.SYSTEM_MANUAL_OIL_BOILER_TO_TANK1 : (GD.SYSTEM_V1_EXT_TO_TANK_1, GD.BIT_HIGH,
                                                                                GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                                GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_HIGH,
                                                                                GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),

        # For boiler to tank2 we set tank2 pump on and turn boiler on.
        # NOTE: In the current hardware the tank2 pump line is used to indicate that ext should go to int so we hold it low for now.
        GD.SYSTEM_MANUAL_OIL_BOILER_TO_TANK2 : (GD.SYSTEM_TANK_2_PUMP, GD.BIT_LOW,
                                                                                GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),
    
        # For boiler off we turn boiler off.
        GD.SYSTEM_MANUAL_OIL_BOILER_OFF : (GD.SYSTEM_BOILER_ON, GD.BIT_LOW),
        
        ## AUTO MODE 
        
        # For tank1 to heating we set valve 1 for ext to tank1 which also sets tank1 to heating.     
        GD.SYSTEM_AUTO_TANK_1_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_TANK_1, GD.BIT_HIGH,
                                                                         GD.SYSTEM_TANK_2_PUMP, GD.BIT_LOW,
                                                                         GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_LOW),
        
        # For tank2 to heating we set valve 1 for ext to heating and set tank2 pump on.
        GD.SYSTEM_AUTO_TANK_2_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_HEATING, GD.BIT_HIGH,
                                                                         GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                         GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_LOW),

        # For boiler to heating we set valve 1 for ext to heating, set tank2 pump on, set valve3 for boiler to int and turn boiler on.
        GD.SYSTEM_AUTO_OIL_BOILER_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_HEATING, GD.BIT_HIGH,
                                                                               GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                               GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_HIGH,
                                                                               GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),

        # For boiler to tank1 we set valve 1 for ext to tank1, set tank2 pump on, set valve3 for boiler to int and turn boiler on.
        GD.SYSTEM_AUTO_OIL_BOILER_TO_TANK1 : (GD.SYSTEM_V1_EXT_TO_TANK_1, GD.BIT_HIGH,
                                                                           GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                           GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_HIGH,
                                                                           GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),

        # For boiler to tank2 we set tank2 pump on and turn boiler on.
        # NOTE: In the current hardware the tank2 pump line is used to indicate that ext should go to int so we hold it low for now.
        GD.SYSTEM_AUTO_OIL_BOILER_TO_TANK2 : (GD.SYSTEM_TANK_2_PUMP, GD.BIT_LOW,
                                                                  GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),
    
        # For boiler off we turn boiler off.
        GD.SYSTEM_AUTO_OIL_BOILER_OFF : (GD.SYSTEM_BOILER_ON, GD.BIT_LOW),
        
        ## HOLIDAY MODE
        
        # For tank1 to heating we set valve 1 for ext to tank1 which also sets tank1 to heating.     
        GD.SYSTEM_HOLIDAY_TANK_1_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_TANK_1, GD.BIT_HIGH,
                                                                             GD.SYSTEM_TANK_2_PUMP, GD.BIT_LOW,
                                                                             GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_LOW),
        
        # For tank2 to heating we set valve 1 for ext to heating and set tank2 pump on.
        GD.SYSTEM_HOLIDAY_TANK_2_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_HEATING, GD.BIT_HIGH,
                                                                             GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                             GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_LOW),
 
        # For boiler to heating we set valve 1 for ext to heating, set tank2 pump on, set valve3 for boiler to int and turn boiler on.
        GD.SYSTEM_HOLIDAY_OIL_BOILER_TO_HEATING : (GD.SYSTEM_V1_EXT_TO_HEATING, GD.BIT_HIGH,
                                                                                   GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                                   GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_HIGH,
                                                                                   GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),

        # For boiler to tank1 we set valve 1 for ext to tank1, set tank2 pump on, set valve3 for boiler to int and turn boiler on.
        GD.SYSTEM_HOLIDAY_OIL_BOILER_TO_TANK1 : (GD.SYSTEM_V1_EXT_TO_TANK_1, GD.BIT_HIGH,
                                                                                GD.SYSTEM_TANK_2_PUMP, GD.BIT_HIGH,
                                                                                GD.SYSTEM_V3_BOILER_TO_INT, GD.BIT_HIGH,
                                                                                GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),

        # For boiler to tank2 we set tank2 pump on and turn boiler on.
        # NOTE: In the current hardware the tank2 pump line is used to indicate that ext should go to int so we hold it low for now.
        GD.SYSTEM_HOLIDAY_OIL_BOILER_TO_TANK2 : (GD.SYSTEM_TANK_2_PUMP, GD.BIT_LOW,
                                                                                GD.SYSTEM_BOILER_ON, GD.BIT_HIGH),
    
        # For boiler off we turn boiler off.
        GD.SYSTEM_HOLIDAY_OIL_BOILER_OFF : (GD.SYSTEM_BOILER_ON, GD.BIT_LOW),
        
    }

    # Make sure entry is valid.
    if configBit in outputConfigurationLookUp :
        
        # The lookup table is arranged as: bit, value, bit, value..... So we calculate the last index for a bit and traverse the table
        # picking every second pair of elements.
        lastIndex = len (outputConfigurationLookUp [configBit]) -1
        
        # Set the outputs to the levels required.
        for index in range (0, lastIndex, 2) :
            # Get the bit.
            outputBit = outputConfigurationLookUp [configBit][index]
            
            print index, systemControl [outputBit].GetDisplayText(),
            
            # Set bit high or low from data in lookup table.
            if outputConfigurationLookUp [configBit][index+1]  == GD.BIT_HIGH :
                systemControl [outputBit].SetOutputBitHigh()  

                print 'on'
                
            else :
                systemControl [outputBit].SetOutputBitLow()

                print 'off'
                
################################################################################
##
## Function: SetModeOutputControlBitsFromConfigBits ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: Sets the system output control bits as required by the config bits for the mode we are in and the
## options set for that mode.  UpdateSystemOutputs () will then set or clear the relays as required. We will call this function
## when we enter run mode, either by pressing 'Finished' or timeout to finish. It will also be called when we are in auto mode
## if the configuration changes. E.g. The heating source switches from tank1 to tank2.
##
################################################################################

def SetModeOutputControlBitsFromConfigBits () :

    # This table holds the lists of control bits for the heating and boiler modes for each global system mode. E.g. if we are in
    # manual mode we scan through the heating and boiler control groups for manual mode to find which options are active. This
    # could be tank 1 to heating and bolier off. We then use these options to set all the outputs to the levels required to set this
    # mode.
    controlGroupLookUp = {
        GD.SYSTEM_MANUAL_MODE : (GD.HEATING_MANUAL_CONTROL_GROUP, GD.BOILER_MANUAL_CONTROL_GROUP),
        GD.SYSTEM_AUTO_MODE : (GD.HEATING_AUTO_CONTROL_GROUP, GD.BOILER_AUTO_CONTROL_GROUP),
        GD.SYSTEM_HOLIDAY_MODE : (GD.HEATING_HOLIDAY_CONTROL_GROUP, GD.BOILER_HOLIDAY_CONTROL_GROUP)   
   }
    
   # Scan through the system control bits to find which mode is active (Off, Auto, Manual or Holiday). Bits are mutually exclusive.
    systemModeBit = GetActiveSystemBit (GD.SYSTEM_CONTROL_GROUP)
            
    print systemControl [systemModeBit].GetDisplayText()
    
    # If this is system off set everything idle/off and clear any override bits that have been set. 
    if systemModeBit == GD.SYSTEM_OFF_MODE :
        # Clear all output overrides.
        for controlBit in GD.SYSTEM_OUTPUT_GROUP :
            systemControl [controlBit].SetOverrideNone ()
        # Set outputs for off mode.    
        ConfigureOutputBits (GD.SYSTEM_OFF_MODE)
    else :
        #  Not off so make sure entry is valid.
        if systemModeBit in controlGroupLookUp :
            # Set the selected heating source and boiler mode. The heating source is set first as it may set
            # the boiler off, but this will be corrected when the boiler mode is set.
            ConfigureOutputBits (GetActiveSystemBit (controlGroupLookUp [systemModeBit][0]))
            # Scan through the boiler control bits to find the boiler mode and set the bits as required.
            ConfigureOutputBits (GetActiveSystemBit (controlGroupLookUp [systemModeBit][1]))
            
################################################################################
##
## Function: SetZonePumpOutputControlBitsFromZonePumpStatus (zone)
##
## Parameters: zone - integer - the heating zone (rad or ufh) that we want to check if a pump is required.
##
## Returns:
##
## Globals modified:
##
## Comments: Looks up the status of a zone pump and set the system control bits as required. The UpdateSystemOutputs () will
## then set or clear the relay as required. Note that when we check if a pump is required we actually ignore the zone and
## check if a pump is required for any zone so that if any zone is on we turn the pump on and if all zones are off we turn the
## pump off. We will also check here if the system is turned off and set the pump off if it is. There are 2 zone pumps, one
## for rads and the other for ufh.
##
################################################################################

def SetZonePumpOutputControlBitsFromZonePumpStatus (zone) :

    # Make sure we are dealing with heating zones. Immersions are zones 30-33.
    if zone < 30 :
        # Select rad or ufh pump.
        controlBit = GD.SYSTEM_UFH_PUMP  if zone >= 14 else GD.SYSTEM_RAD_PUMP
        # Turn pump on only if system is on (not off) and pump is required.
 #       if (systemControl [GD.SYSTEM_OFF_MODE].CheckIfBitHigh () == False
        if (True
            and
            zones.zoneData[zone].CheckIfPumpRequired () == True) :
            systemControl [controlBit].SetOutputBitHigh ()
        else :
            systemControl [controlBit].SetOutputBitLow ()
        
################################################################################
##
## Function: SetImmersionOutputControlBitsFromImmersionStatus (zone)
##
## Parameters: zone - the immersion zone that we want to update the system control bits.
##
## Returns:
##
## Globals modified:
##
## Comments: Looks up the status of an immersion and set the system control bit as required. The UpdateSystemOutputs will
## then set or clear the relay as required. Immersions are treated as zones for the purpose of setting the times they are on or
## off. During a mains failure we turn the immersions off so that when the house switches to use the UPS backup supply the
## immersions will not load the backup supply. This is done in hardware via a relay that is held on when mains is present and
## connects the system outputs through to the immersion power relays. When mains fails the immersions will be disconnected
## and the mains fail input line will be set active.
##
################################################################################

def SetImmersionOutputControlBitsFromImmersionStatus (zone) :

    # Calculate keyvalue from zone.
    keyValue = zone + 1
        
    # Get control bit from lookup. Check if valid first.
    if keyValue in GD.KEY_TO_CONTROL_BIT_LOOKUP :
        controlBit = GD.KEY_TO_CONTROL_BIT_LOOKUP [keyValue]
            
        # If status of this zone has changed we will update system bits.
        if zones.zoneData [zone].CheckIfZoneStatusChanged () == True :
        
            # The status has changed so we need to update our current zone status.
            zones.zoneData [zone].UpdateCurrentZoneStatus ()
            
            # Do we need to turn on or off?
            if zones.zoneData [zone].CheckIfZoneOnRequested () == True :
                systemControl [controlBit].SetOutputBitHigh ()
            else :
                systemControl [controlBit].SetOutputBitLow ()
               
################################################################################
##
## Function: UpdateSystemControlBits (bitsHigh = GD.SYSTEM_NONE, bitsLow = GD.SYSTEM_NONE)
##
## Parameters: bitsHigh / bitsLow - integer or tuple - the bit(s) to set high or low
##
## Returns:
##
## Globals modified:
##
## Comments: Used to update a group of control bits. Normally this is used to set a single control bit high and all
## the other control bits low for a group of mutually exclusive control bits. Note that the control bit to make high should also
## be in the low list so that we can use the same list whenever we make a control bit high in a particular group.
##
################################################################################

def UpdateSystemControlBits (bitsHigh = GD.SYSTEM_NONE, bitsLow = GD.SYSTEM_NONE) :

    # Do low first.
    # Check if single or multiple bits (single = int, multiple = tuple).
    if type (bitsLow) is int :
        #Turn int to tuple.
        bitsLow = (bitsLow,)
    # Have we got a bit to set low?
    if bitsLow[0] != GD.SYSTEM_NONE :
        for bit in (bitsLow) :
            systemControl [bit].SetOutputBitLow ()
        
    # Now do high.
    # Check if single or multiple bits (single = int, multiple = tuple).
    if type (bitsHigh) is int :
        #Turn int to tuple.
        bitsHigh = (bitsHigh,)
    # Have we got a bit to set high?
    if bitsHigh[0] != GD.SYSTEM_NONE :
        for bit in (bitsHigh) :
            systemControl [bit].SetOutputBitHigh ()

################################################################################
##
## Function: InitialiseSystemControlBits () 
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments:
## Creates dictionary for all the control bits. 
## For all bits we load a text identifier and load the state bit with the initial state.
## For input and output bits we load the I2C address and bit mask for this bit. 
## All bits have an 'override bit' which is used to override the state bit when we do a manual override operation.
## All bits have a timer that is used to set the time the bit is active if it is a pulsed bit or a validation timer for an input bit.
##
################################################################################

def InitialiseSystemControlBits () :

     # Define dictionaries for system control objects
    global systemControl
    systemControl = {}
    
    # Startup configuration values for the system control output objects. We specify the name and I/O info here.
    systemOutputConfig = (
    
        (GD.SYSTEM_IMM_1, 'Immersion 1', GD.BIT_LOW, GD.I2C_ADDRESS_0X3A, GD.BIT_7_MASK),
         
        (GD.SYSTEM_IMM_2, 'Immersion 2', GD.BIT_LOW, GD.I2C_ADDRESS_0X3A, GD.BIT_0_MASK),
         
        (GD.SYSTEM_IMM_3, 'Immersion 3', GD.BIT_LOW, GD.I2C_ADDRESS_0X3B, GD.BIT_7_MASK),
         
        (GD.SYSTEM_IMM_4, 'Immersion 4', GD.BIT_LOW, GD.I2C_ADDRESS_0X3B, GD.BIT_5_MASK),
         
        (GD.SYSTEM_TANK_2_PUMP, 'Tank 2 Pump', GD.BIT_LOW, GD.I2C_ADDRESS_0X3A, GD.BIT_5_MASK), 
         
        (GD.SYSTEM_TANK_1_PUMP, 'Tank 1 Pump', GD.BIT_LOW, GD.I2C_ADDRESS_0X3A, GD.BIT_6_MASK),
         
        (GD.SYSTEM_BOILER_ON, 'Oil Boiler', GD.BIT_LOW,  GD.I2C_ADDRESS_0X3B, GD.BIT_1_MASK),
        
        (GD.SYSTEM_V3_BOILER_TO_INT, 'Boiler to Int', GD.BIT_LOW, GD.I2C_ADDRESS_0X3B, GD.BIT_0_MASK),
        
        (GD.SYSTEM_V1_EXT_TO_HEATING, 'Ext to Heating', GD.BIT_LOW, GD.I2C_ADDRESS_0X3A, GD.BIT_4_MASK),
        
        (GD.SYSTEM_V1_EXT_TO_TANK_1, 'Ext to Tank 1', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3A, GD.BIT_3_MASK),
        
        (GD.SYSTEM_WOODBURNER_PUMP_1, 'Woodburner Pump 1', GD.BIT_LOW,  GD.I2C_ADDRESS_0X3A, GD.BIT_1_MASK),
        
        (GD.SYSTEM_WOODBURNER_PUMP_2, 'Woodburner Pump 2', GD.BIT_LOW,  GD.I2C_ADDRESS_0X3A, GD.BIT_2_MASK),
        
        (GD.SYSTEM_RAD_PUMP, 'Rad Pump 1', GD.BIT_LOW,  GD.I2C_ADDRESS_0X39, GD.BIT_7_MASK),
        
        (GD.SYSTEM_UFH_PUMP, 'Ufh Pump 2', GD.BIT_LOW,  GD.I2C_ADDRESS_0X38, GD.BIT_7_MASK),
        
        (GD.SYSTEM_EXT_TO_INT, 'Ext to Int', GD.BIT_LOW,  GD.I2C_ADDRESS_0X3B, GD.BIT_6_MASK) #Not used at present
    )
    # Startup configuration values for the system control input objects. We specify the name and I/O info here.
    # Note that input lines are active low logic (low = on).
    systemInputConfig = (
    
        (GD.SYSTEM_RAD_DEMAND, 'Rad Demand', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3C, GD.BIT_0_MASK),
       
        (GD.SYSTEM_UFH_DEMAND, 'Ufh Demand', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3C, GD.BIT_1_MASK),
        
        (GD.SYSTEM_HW_DEMAND, 'HW Demand', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3C, GD.BIT_2_MASK),
        
        (GD.HEATING_FLOW_PULSE, 'Flow Pulse', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3C, GD.BIT_3_MASK),
        
        (GD.SYSTEM_IMM_1_MAX, 'Immersion 1 Max', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3C, GD.BIT_4_MASK),
        
        (GD.SYSTEM_IMM_2_MAX, 'Immersion 2 Max', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3C, GD.BIT_5_MASK),
        
        (GD.SYSTEM_WOODBURNER_FLOW_DETECT, 'Woodburner Flow Detect', GD.BIT_HIGH,  GD.I2C_ADDRESS_0X3C, GD.BIT_6_MASK),
        
        (GD.SYSTEM_MAINS_FAIL, 'Mains Fail', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3C, GD.BIT_7_MASK),
        
##        (GD.SYSTEM_WOODBURNER_SENSOR_CONNECTED, 'Woodburner Sensor Connected', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3E, GD.BIT_0_MASK),
        
 ##       (GD.SYSTEM_HEATING_SENSOR_CONNECTED, 'Heating Sensor Connected', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3E, GD.BIT_1_MASK),
        
 ##       (GD.SYSTEM_TANK_1_SENSOR_CONNECTED, 'Tank 1 Sensor Connected', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3E, GD.BIT_2_MASK),
        
        (GD.SYSTEM_BATH_3_4_SHOWER_ACTIVE, 'Bath 3/4 Shower active', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3D, GD.BIT_0_MASK),
        
        (GD.SYSTEM_BATH_2_SHOWER_ACTIVE, 'Bath 2 Shower active', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3D, GD.BIT_1_MASK),
        
        (GD.SYSTEM_BATH_1_SHOWER_ACTIVE, 'Bath 1 Shower active', GD.BIT_HIGH, GD.I2C_ADDRESS_0X3D, GD.BIT_2_MASK)
    )
    # Startup configuration values for the system temperature input objects. We specify the name and I/O info here.
    # Note that temperature lines are monitored via a 1 wire bus controller.
    systemTemperatureConfig = (

# These are bench test    
#        (GD.SYSTEM_WOODBURNER_FLOW_TEMP, 'Woodburner flow temperature', 0, '0F7AD1010000',),
       
#        (GD.SYSTEM_WOODBURNER_RETURN_TEMP, 'Woodburner return temperature', 0, '3E5A33070000')

# These are in enclosure
 #       (GD.SYSTEM_WOODBURNER_FLOW_TEMP, 'Woodburner flow temperature', 0, '422AB6060000',),
       
 #       (GD.SYSTEM_WOODBURNER_RETURN_TEMP, 'Woodburner return temperature', 0, '5D63B6060000')

# These are back boiler        
        (GD.SYSTEM_WOODBURNER_FLOW_TEMP, 'Woodburner flow temperature', 0, GD.OW_WOODBURNER_FLOW),
       
        (GD.SYSTEM_WOODBURNER_RETURN_TEMP, 'Woodburner return temperature', 0, GD.OW_WOODBURNER_RETURN)
    )
        
    # Startup configuration values for the system control mode config objects. We specify the name and initial state here.
    systemGlobalModeConfig = (
    
        (GD.SYSTEM_OFF_MODE, 'System Off', GD.BIT_HIGH),
        
        (GD.SYSTEM_AUTO_MODE, 'Auto Mode', GD.BIT_LOW),
        
        (GD.SYSTEM_MANUAL_MODE, 'Manual Mode', GD.BIT_LOW),
        
        (GD.SYSTEM_HOLIDAY_MODE, 'Holiday Mode', GD.BIT_LOW)  
    )        
    # Startup configuration values for the system control manual config objects. We specify the name and initial state here.
    systemManualModeConfig = (

        (GD.SYSTEM_MANUAL_TANK_1_TO_HEATING, 'Manual Tank 1 To Heating', GD.BIT_HIGH), 
        
        (GD.SYSTEM_MANUAL_TANK_2_TO_HEATING, 'Manual Tank  2 To Heating', GD.BIT_LOW),
        
        (GD.SYSTEM_MANUAL_OIL_BOILER_TO_HEATING, 'Manual Oil Boiler To Heating', GD.BIT_LOW),
        
        (GD.SYSTEM_MANUAL_OIL_BOILER_TO_TANK1, 'Manual Oil Boiler To Internal', GD.BIT_LOW),
        
        (GD.SYSTEM_MANUAL_OIL_BOILER_TO_TANK2, 'Manual Oil Boiler To Tank 2', GD.BIT_LOW),
        
        (GD.SYSTEM_MANUAL_OIL_BOILER_OFF, 'Manual Oil Boiler Off', GD.BIT_HIGH)
    )
    # Startup configuration values for the system control auto config objects. We specify the name and initial state here.
    systemAutoModeConfig = (

        (GD.SYSTEM_AUTO_TANK_1_TO_HEATING, 'Auto Tank 1 To Heating', GD.BIT_HIGH), 
        
        (GD.SYSTEM_AUTO_TANK_2_TO_HEATING, 'Auto Tank  2 To Heating', GD.BIT_LOW),
        
        (GD.SYSTEM_AUTO_OIL_BOILER_TO_HEATING, 'Auto Oil Boiler To Heating', GD.BIT_LOW),
        
        (GD.SYSTEM_AUTO_OIL_BOILER_TO_TANK1, 'Auto Oil Boiler To Internal', GD.BIT_LOW),
        
        (GD.SYSTEM_AUTO_OIL_BOILER_TO_TANK2, 'Auto Oil Boiler To Tank 2', GD.BIT_LOW),
        
        (GD.SYSTEM_AUTO_OIL_BOILER_OFF, 'Auto Oil Boiler Off', GD.BIT_HIGH)
    )    
    # Startup configuration values for the system control holiday config objects. We specify the name and initial state here.
    systemHolidayModeConfig = (

        (GD.SYSTEM_HOLIDAY_TANK_1_TO_HEATING, 'Holiday Tank 1 To Heating', GD.BIT_HIGH), 
        
        (GD.SYSTEM_HOLIDAY_TANK_2_TO_HEATING, 'Holiday Tank  2 To Heating', GD.BIT_LOW),
        
        (GD.SYSTEM_HOLIDAY_OIL_BOILER_TO_HEATING, 'Holiday Oil Boiler To Heating', GD.BIT_LOW),
        
        (GD.SYSTEM_HOLIDAY_OIL_BOILER_TO_TANK1, 'Holiday Oil Boiler To Internal', GD.BIT_LOW),
        
        (GD.SYSTEM_HOLIDAY_OIL_BOILER_TO_TANK2, 'Holiday Oil Boiler To Tank 2', GD.BIT_LOW),
        
        (GD.SYSTEM_HOLIDAY_OIL_BOILER_OFF, 'Holiday Oil Boiler Off', GD.BIT_HIGH)
    )
    # Startup configuration values for lines we have not implented yet.
    systemFutureConfig = (
    
        
        (GD.SYSTEM_IMM_3_MAX, 'Immersion 3 Max', GD.BIT_HIGH),
        
        (GD.SYSTEM_IMM_4_MAX, 'Immersion 4 Max', GD.BIT_HIGH)       
    )

    # 1st entry is blank.
    systemControl [GD.SYSTEM_NONE] = systemControlBit (0, 0, 0, 0, 0, 0)
    
    # Load the dictionary with system control output objects. Load status for override , set timer as required.
    for configBit, name, state, address, bit in systemOutputConfig :
        # For a pulsed line set timer to timing state, for a normal line flag as timer not used.
        if configBit in GD.SYSTEM_PULSED_OUTPUTS_GROUP :
            systemControl [configBit] = systemControlBit (name, state, address, bit, GD.BIT_OVERRIDE_NONE, GD.BIT_SET_TIMING_60)
        else :
            systemControl [configBit] = systemControlBit (name, state, address, bit, GD.BIT_OVERRIDE_NONE, GD.BIT_NOT_TIMED)

    # Load the dictionary with system control input objects. Load status for bit override and set timer.
    for configBit, name, state, address, bit in systemInputConfig :
        systemControl [configBit] = systemControlBit (name, state, address, bit, GD.BIT_OVERRIDE_NONE, GD.BIT_SET_TIMING_05)

    # Load the dictionary with system control temperature objects. Load status for unused bit mask, override and timer.
    for configBit, name, state, address in systemTemperatureConfig :
        systemControl [configBit] = systemControlBit (name, state, address, 0, GD.BIT_OVERRIDE_NONE, GD.BIT_NOT_TIMED)

    # Load dictionary with system control mode config objects. Load zeros for unused address and bit mask.
    for configBit, name, state in systemGlobalModeConfig :
        systemControl [configBit] = systemControlBit (name, state, 0, 0, GD.BIT_OVERRIDE_NONE, GD.BIT_NOT_TIMED)

    # Load dictionary with system control manual mode config objects. Load zeros for unused address and bit mask.
    for configBit, name, state in systemManualModeConfig :
        systemControl [configBit] = systemControlBit (name, state, 0, 0, GD.BIT_OVERRIDE_NONE, GD.BIT_NOT_TIMED)

    # Load dictionary with system control auto mode config objects. Load zeros for unused address and bit mask.
    for configBit, name, state in systemAutoModeConfig :
        systemControl [configBit] = systemControlBit (name, state, 0, 0, GD.BIT_OVERRIDE_NONE, GD.BIT_NOT_TIMED)

    # Load dictionary with system control holiday mode config objects. Load zeros for unused address and bit mask.
    for configBit, name, state in systemHolidayModeConfig :
        systemControl [configBit] = systemControlBit (name, state, 0, 0, GD.BIT_OVERRIDE_NONE, GD.BIT_NOT_TIMED)

    # Load dictionary with system control future config objects. Load zeros for unused address and bit mask.
    for configBit, name, state in systemFutureConfig :
        systemControl [configBit] = systemControlBit (name, state, 0, 0, GD.BIT_OVERRIDE_NONE, GD.BIT_NOT_TIMED)  
        








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
