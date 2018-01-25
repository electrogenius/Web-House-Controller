#! /usr/bin/python

import display
import time
import GD
import keys
import threading
import smbus
import zones
import relay
import system
import keyData
import sensor
import multiprocessing
import ow

################################################################################
##
## Function:  OneSecondTimeout ()
##
## Parameters: timerStatus - threading flag
##
## Returns: timerStatus threading flag is set to show timer tick.
##
## Globals modified:
##
## Comments: This function is called by a threading.Timer. We use this timer to set the period at which we will process all the
##                    1 second operations. When the timer expires we simply call this function to set an event flag.
##
################################################################################

def OneSecondTimeout (timerStatus) :

    # Flag we have had a tick.
    timerStatus.set ()
    
################################################################################
##
## Function: UpdateCleardownTimers ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments:  Scan through and update all the cleardown timers. Tell caller if any have finished.
##
################################################################################

def UpdateCleardownTimers () :

    timerFinished = False

    for cleardownTimer in range (0,30) :
        if zones.zoneData[cleardownTimer].UpdateCleardownTimer () == -1 :
            timerFinished = True
            
    return timerFinished

################################################################################
##
## Function: UpdatePumpTimers ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: Scan through and update all the pump timers. Tell caller if any have finished.
##
################################################################################

def UpdatePumpTimers () :

    timerFinished = False

    for pumpTimer in range (0,30) :
        if zones.zoneData[pumpTimer].UpdatePumpTimer () == True :
            timerFinished = True
            
    return timerFinished

################################################################################
##
## Function: ProcessOneSecondOperations (I2CPort)
##
## Parameters: I2CPort - port object for the I2C bus
##
## Returns:
##
## Globals modified:
##
## Comments: Do all the operations that are done at 1 second intervals.
##
################################################################################

def ProcessOneSecondOperations (I2CPort, resultQueue) :
    
    # Scan the pulsed output lines to see if the pulse time is finished for any of the lines.
    relay.UpdatePulsedOutputLines (I2CPort)
    
    # Scan the system hardware inputs and update the input config bits with new values.
    sensor.ReadSystemInputs (I2CPort)
    
    # Scan through all the output config bits and set outputs (relays) as required.
    relay.UpdateSystemOutputs (I2CPort)
 
    # Decrement activity timer. This gets reloaded when we detect a keypress so with no keypresses it will time out.
    # It will be set to -1 when we are in run mode.
    if GD.timeToRunMode > 0 :
        GD.timeToRunMode -=1

    # Invert flash flag. We use this for deciding which image to display for flashing bands on the keyboard.
    GD.flashOn ^= True
            
    # Check the woodburner.
    system.WoodburnerPumpControl ()
    
    # Are we in run mode? Run mode is when keyboard entry has finished and we are servicing all the system functions.
    if GD.currentMode == GD.MODE_RUN :
        # In run mode so move the 'press to start' message to a new location every second.
        if GD.flashOn == True :
            display.DisplayPressToStart ()
            
        # Service tank1 pump.
        system.Tank1PumpControl ()
         
    else :
        # Still in keyboard entry so update clock display and illuminate bands and text on keys.
        display.TopRightInfoPrompt (GD.CLOCK_DISPLAY)
        display.IlluminateKeys (GD.flashOn)

    # Scan through all the cleardown timers and update as required. If any have finished start a zones check.
    if UpdateCleardownTimers () == True :
        GD.checkZone = 0
        
    # Scan through all the pump timers and update as required. If any have finished start a zones check.
    if UpdatePumpTimers () == True :
        GD.checkZone = 0
                  
    # If we have moved to a new minute start a zones check.
    newMinute = time.localtime (time.time()).tm_min
    if  newMinute != GD.lastMinute :
        GD.lastMinute = newMinute
        GD.checkZone = 0
        newWeekDay = time.localtime (time.time()).tm_wday
            
################################################################################
##
## Function: SwitchToRunMode ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: In run mode we service all the zones. On Visi Genie we will display a moving Press To Start. For Android we
## will blank all the keys and display a Press any key to start prompt.
##
################################################################################

def SwitchToRunMode () :

    # Clear all the prompts.
    display.DisplayZoneMode ()
    display.TopRightInfoPrompt (GD.BLANK_PROMPT)
    display.DisplayProgOnTime (GD.BLANK_PROMPT)
    display.DisplayProgOffTimeAndDays (GD.BLANK_PROMPT)
    display.DisplayEntries (GD.BLANK_PROMPT)
    display.DisplayBottomLeftInfoPrompt (GD.BLANK_PROMPT)
    display.DisplayBottomRightInfoPrompt (GD.BLANK_PROMPT)
    
    # Set system bits as required.
    system.SetModeOutputControlBitsFromConfigBits ()

    # Switch to run mode.
    GD.currentMode = GD.MODE_RUN
    
    # Put display into waiting for a press mode.
    display.WriteToDisplay (GD.BACKLIGHT_OFF)
    display.DisplayForm (GD.BLANK_SCREEN_FORM)
    display.DisplayPressToStart ()
    display.WriteToDisplay (GD.BACKLIGHT_LOW)
    
    # For android screen
    display.DisplayMiddleLeftInfoPrompt (GD.PRESS_ANY_KEY_PROMPT)
    
    # Clear any boost presses so they are not there when we restart later.
    GD.boostPresses = 0
    
    # Start a zones check to update any changes to zones.
    GD.checkZone = 0



################################################################################
##
## Function: main ()
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
 
# Main program starts here.
def main () :

    #Initialise the I2C port used for the relays and get I2C port object.
    I2CPort = smbus.SMBus (1)
    
    #Initialise 1 wire.
    ow.init('localhost:4304')

    # Create data structures to hold zone data.
    zones.InitialiseZones()
    
    # Initialise all the system control bits.
    system.InitialiseSystemControlBits ()
    
    # Initialise the RS232 serial port and the display module and get serial port object.
    display.RS232Port = display.InitialiseDisplayKeyboardModule ()

    # We run a process to read the 1 wire bus for the temperature sensors. Communication with the process is via 2 queues.
    # The command queue takes a 2 element tuple of the sensor id to start reading and the rad interval.
    # The result queue will contain a 2 element tuple of a sensor id and the temperature just read.
    # So here we initialise 2 queues and start the process.
    commandQueue = multiprocessing.Queue()
    resultQueue = multiprocessing.Queue()
    p = multiprocessing.Process(target = sensor.ReadTemperatures, args = (commandQueue, resultQueue,))
    p.start()
    
    # Start reading the woodburner temperature sensors. We always have the woodburner code operational, even when the
    # system is in OFF mode. This is for safety lest the woodburner is lit with the system turned off.
    commandQueue.put ((GD.SYSTEM_WOODBURNER_FLOW_TEMP, 1))
    commandQueue.put ((GD.SYSTEM_WOODBURNER_RETURN_TEMP, 1))

    # DEBUG OUTPUT
    for entry in system.systemControl :
        print system.systemControl [entry].GetDisplayText(), system.systemControl [entry].GetAddress () 
    
    # This is the zone that is currently selected for viewing or editing. Initialise to the 1st zone (rad 1).
    selectedZone = GD.RAD_BED1
    
    # We keep the last zone selected so that we can determine if a new zone has been selected.
    lastSelectedZone = GD.NO_ZONE

    # We need to read a zone to create a time object to use later.
    zones.ReadZoneTimes (selectedZone)

    # We time how long since the user last pressed a key so that we can blank the screen on no key activity and
    # also start zone checking and relay operation, which is suspended while key activity is in operation.
    lastKeypressTime = time.time()
    lastKeyImage = ''
    
    # This is a flag for our 1 second threading timer. When the timer expires we set this flag to give us a 1 second tick.
    oneSecondTimerTick = threading.Event ()
    # Set it so that we do the 1st 1 second operations.
    oneSecondTimerTick.set ()
    
    # Use same startup screen as wakeup so simply call wakeup key code.
    keys.ProcessWakeupKey (-1)
    
    # Set volume on the display to max.
    display.AdjustVolume (GD.SOUND_VOLUME_MAX)
    
    # This is our main loop
    while (1) :
    
        # Let the CPU have a break from us.
        time.sleep (0.01)

        # Check if we have received any temperature readings and if we have get and save them. We do this in the
        # main loop so we can empty the queue faster than the readTemperatures process can fill it.
        if not resultQueue.empty () : 
            systemId, sensorTemperature = resultQueue.get ()
            system.systemControl [systemId].UpdateTemperature (sensorTemperature)
            print system.systemControl [systemId].GetDisplayText(), sensorTemperature

        # Process possible key message from display module.
        keyCode = display.CheckForSerialInput (GD.CHECK_FOR_BUTTON)

        # Have we got a key? KeyCode is the physical button value on the display module
        if keyCode :
            # Sound key press.
            display.GenerateSound (GD.SOUND_CLICK)
            # Delay and then check for a key again. This will remove any key bounce that occurs in the delay time.
            # The delay also allows the sound to output without interference caused by sending data to the display
            # whilist it is generating the sound. We just ignore any keycode returned.
            time.sleep (0.4)
            display.CheckForSerialInput (GD.CHECK_FOR_BUTTON)

            # If we detect a longer keybounce (2 keypresses within a set time) ignore the key by making it zero.
            if time.time() < (lastKeypressTime + 0.85) :
                print 'BOUNCE',time.time()-lastKeypressTime
                # Re-display the last key image again as we will have lost it on the bounce.
                display.WriteToDisplay (lastKeyImage)
                # Clear the key
                keyCode = 0
                keyValue = 0
            else :    
                # Get the actual value for the key. Each physical key can have several different keyValues. It depends on the
                # mode we are in as we display different keyboards for each mode.
                keyValue = keyData.GetKeyValue (keyCode)
                print 'INITIAL KEYVALUE',keyValue
            # Found a key so reload our bounce timer. 
            lastKeypressTime = time.time()
            
            # Have we got a key value? We may not have if it was a key bounce or a blank key.
            if keyValue :
                # We have a key so reload activity timer.
                GD.timeToRunMode = GD.KEYPRESS_WAIT_TIME
                
                # If it is a zone select key save it for later use.
                if keyValue in GD.KEY_GROUP_ALL_ZONES :
                    # Adjust key value as zones start at 0 and key is 1 for zone 0.
                    selectedZone = keyValue - 1
                    
                      # If we have moved zones reset the boost key counter so we start at 1st boost for new zone.
                    if lastSelectedZone != selectedZone :
                        GD.boostPresses = 0
                        lastSelectedZone = selectedZone
                        print 'SELECTED ZONE',selectedZone
                
                # If it is status select key save it for later use.
                elif keyValue in GD.KEY_GROUP_STATUS :
                    selectedZone = keyValue
                    
                # Go and process key.
                keys.ProcessKeys (keyValue, selectedZone)
                
                # We may now be in a different mode so we need to update the keyvalue for the new mode.
                keyValue = keyData.GetKeyValue (keyCode)
                                        
                # Update key image. Keep image so we can redisplay key after a key bounce.
                # If the key is displayed elsewhere lastKeyImage will be set null and the image will not be changed.
                lastKeyImage = keyData.GetKeyImageSequence (keyValue)
                display.WriteToDisplay (lastKeyImage)
                print 'KEYVALUE NOW',keyValue

               # If we are in a zone select mode read the programmed times and update display so user can see the zone status. 
                if GD.currentMode  in (GD.MODE_RAD_ZONE_SELECT, GD.MODE_UFH_ZONE_SELECT, GD.MODE_IMMERSION_SELECT) :
                    zones.ReadZoneTimes (selectedZone)
                    zoneStatus =  zones.UpdateZoneStatus (selectedZone)
                    display.DisplayZoneStatus (selectedZone, zoneStatus)
                    display.DisplayZoneMode (selectedZone)
                    display.DisplayBottomLeftInfoPrompt ()
                    
                    # Update boost key image and if it is the key currently pressed save the image.
                    tempKeyImage = display.DisplayBoostKeyImage (selectedZone)
                    if keyValue == GD.KEYVALUE_BOOST :
                        lastKeyImage = tempKeyImage
                    
                    # Update cancel / resume key image and if it is the key currently pressed save the image.
                    tempKeyImage = display.DisplayCancelResumeKeyImage (selectedZone)
                    if keyValue == GD.KEYVALUE_CAN_RES :
                        lastKeyImage = tempKeyImage
                    
                # If we are in a  programming mode update the auto / manual / enable / disable key image and if it is
                # the key currently pressed save the image.
                if GD.currentMode in (GD.MODE_PROG_TIME, GD.MODE_PROG_ON_AT, GD.MODE_PROG_OFF_AT,
                                                     GD.MODE_PROG_DAY, GD.MODE_PROG_DAYS_ON) :
                
                    tempKeyImage = display.DisplayAutoEnableKeyImage (selectedZone)
                    if keyValue in (GD.KEYVALUE_AUTO_MANUAL, GD.KEYVALUE_ENABLE_DISABLE) :
                        lastKeyImage = tempKeyImage
                        
        # If there has been no activity we will revert to run mode and display the 'press to start' screen.
        if GD.timeToRunMode == 0 :
            # Make flag -ve so we don't come here again.
            GD.timeToRunMode -=1
            
            # Set up run mode.
            SwitchToRunMode ()
            
        # Has our 1 second timer ticked? If it has, do all the operations we do at 1 second intervals.
        # Restart the 1 second timer. It will set the oneSecondTimerTick event flag on timeout. This provides us with a 1 second tick.
        if oneSecondTimerTick.isSet () :
        
            oneSecondTimerTick.clear ()         
            threading.Timer (1, OneSecondTimeout, args = (oneSecondTimerTick,)).start()     

            # Do our 1 second operations.
            ProcessOneSecondOperations (I2CPort, resultQueue) 
            
        # Are we in run mode and a zone check is required. checkZone will have been set to 0 if a check is required
        if GD.currentMode == GD.MODE_RUN and GD.checkZone >= 0 :
        
            # Update a zone's status.
            zones.UpdateZoneStatus (GD.checkZone)
            
            # Do any heating zone relay operation required. Heating zones are from 0 to 29. The relays for heating zones
            # are latching and in a matrix and are therefore accessed differently to system relays.
            if GD.checkZone < 30 :
                relay.ActivateHeatingZoneRelay (I2CPort, GD.checkZone)
                
            # Immersion zones are from 30 to 33. Zones 30-33 are the 4 immersions. We will set the output control bits here and
            # the system relay code will control the actual outputs (relays).
            else :
                system.SetImmersionOutputControlBitsFromImmersionStatus (GD.checkZone)
                
            # If a zone pump is required set bits so system relay code sets it on.
            system.SetZonePumpOutputControlBitsFromZonePumpStatus (GD.checkZone)
            
            # Update the band status for a heating or immersion zone.
            keyData.SetZoneSelectBandStatus (GD.checkZone)
            
           # Move to next zone to check. When we pass the last zone stop further checking.
            GD.checkZone += 1
            if GD.checkZone >= 34 :
                GD.checkZone = -1
            
        # Not in run mode. Are we in a select mode where a zone's state is displayed by a band?
        elif GD.currentMode in (GD.MODE_RAD_WAITING_ZONE_SELECT, GD.MODE_RAD_ZONE_SELECT,
                                              GD.MODE_IMMERSION_WAITING_SELECT, GD.MODE_IMMERSION_SELECT,
                                              GD.MODE_UFH_WAITING_ZONE_SELECT, GD.MODE_UFH_ZONE_SELECT) :
            
            # If this is the 1st time here since run mode (checkZone = -1) or we have reached the end we need to set checkZone
            # to zero, otherwise move to next zone.
            if GD.checkZone < 0 or GD.checkZone >= 33 :
                GD.checkZone = 0
            else :
                GD.checkZone += 1
            
            # Update the band status for a heating or immersion zone.
            keyData.SetZoneSelectBandStatus (GD.checkZone)
                
           
if __name__ == '__main__' :
    main ()
    
################################################################################
#
# Function:
#
# Parameters:
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################






