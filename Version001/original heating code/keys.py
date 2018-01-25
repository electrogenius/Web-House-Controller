print 'Loaded keys module'
import time
import GD
import display
import zones
import system
import keysSystem
import keyData

################################################################################
#
# Function: ProcessCanResKey (zone)
#
# Parameters: zone - the selected zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessCanResKey (zone) :

    # We only process Cancel / Resume if the user has selected a zone. 
    if GD.currentMode in (GD.MODE_RAD_ZONE_SELECT, GD.MODE_UFH_ZONE_SELECT, GD.MODE_IMMERSION_SELECT) :
    
        # Cancel / resume only allowed if no boost is in operation.
        if  zones.zoneData[zone].CheckIfZoneBoostOn() == False :
     
            print 'Can - Res'
            # Find the current status of this zone. Returns tuple. Location 0 has status code.
            zoneStatus = zones.UpdateZoneStatus (zone)

            # If the zone is currently active we set it to CANcelled, This will turn it off.
            if zoneStatus[0] == GD.STATUS_ZONE_ACTIVE :
                zones.zoneData[zone].SetZoneTimedCancelled ()

            # If the zone is CANcelled we clear the cancel and make it ON so that the zone RESumes normal operation.
            elif zoneStatus[0] == GD.STATUS_ZONE_CANCELLED :
                zones.zoneData[zone].SetZoneTimedOn ()

    return 1

################################################################################
#
# Function: ProcessBoostKey (zone) 
#
# Parameters: zone - integer - the zone to boost
#
# Returns: Nothing
#
# Globals modified: boostPresses - number of times boost button pressed
#                             zoneDataStatus - list of status and boost times for all zones
#
# Comments: The boost key allows the user to turn a RAD (UFH) zone on for 1(4) or 2(8) hours. The key toggles through
#                    1 (4) hour(s), 2 (8) hours or off. If the boost key is pressed when a boost period has been previousy set the
#                    1st operation will be off.
#
################################################################################

def ProcessBoostKey (zone) :

    # We only process a boost if the user has selected a zone. 
    if GD.currentMode  in (GD.MODE_RAD_ZONE_SELECT, GD.MODE_UFH_ZONE_SELECT, GD.MODE_IMMERSION_SELECT) :
    
        # Get the current time
        timenow = time.localtime(time.time())
        
        # Get current hour & day.
        boostHour = timenow.tm_hour
        boostDay =  timenow.tm_wday
        
        # Increment number of presses so we cycle through +1 (4) hour, +2 (8) hours, boost off.
        GD.boostPresses += 1

        # If button pressed 3 times or boost is ON and we have arrived here for the 1st time since another operation we will
        # turn boost off.
        if (GD.boostPresses >= 3
            or
            (zones.zoneData[zone].CheckIfZoneBoostOn () == True and GD.boostPresses == 1)) :
            # Cancel boost.
            zones.zoneData[zone].SetZoneBoostOff ()
            GD.boostPresses = 0
           
        # Button pressed once or twice so set boost ON and update off hour. UFH has longer boost period.
        else :
            boostPeriod = 1
            # Set longer boost time for UFH zones.
            if zone >= 14 : boostPeriod = 4
            # Add boost time to current hour to get end time.
            boostHour = boostHour + boostPeriod
            # 2 presses give twice the time.
            if GD.boostPresses == 2 :
                boostHour = boostHour + boostPeriod
            # If we have rolled over into next day adust hour and day.
            if boostHour > 23 :
                boostHour -= 24
                boostDay += 1
                if boostDay >6 : boostDay = 0

            # Set boost on and provide off time..
            zones.zoneData[zone].SetZoneBoostOn (boostDay, boostHour, timenow.tm_min)
    
    return 1 

################################################################################
#
# Function:  ProcessProgramKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments:
#
################################################################################

def ProcessProgramKey (zone) :

    # Switch to the program keyboard (time entry).
    display.DisplayKeyboardImage (GD.TIME_SELECT_KEYBOARD_IMAGE)

    # Say we are in programming mode. We start in time entry mode.
    GD.currentMode = GD.MODE_PROG_TIME

    # Clear the zone select data ready for displaying programming data fields.
    display.DisplayMiddleLeftInfoPrompt (GD.BLANK_PROMPT)

    # Read the programmed times and display the 1st programming data entry. Force a display update.
    zones.ReadZoneTimes (zone)
    display.DisplayProgEntry (1, forceUpdate = True)
    display.DisplayBottomLeftInfoPrompt ()
    display.DisplayBottomRightInfoPrompt ()
      
    return 1 

################################################################################
##
## Function: ProcessRadKey (zone)
##
## Parameters: zone - integer - the current zone
##
## Returns:
##
## Globals modified:
##
## Comments:The Rad key takes you to the rad room select screen.
##
################################################################################

def ProcessRadKey (zone) :

    # Move to rad waiting mode and display keyboard.
    GD.currentMode = GD.MODE_RAD_WAITING_ZONE_SELECT
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    
    # Set rad key active.
   # keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_RAD, GD.KEY_GROUP_WAITING_MODE)
   # display.UpdateSelectKeyImages (GD.KEY_GROUP_WAITING_MODE, GD.UPDATE_CHANGED)
    
    # Clear any previously active select key and display any active bands.
    keyData.UpdateSelectKeyGroupText (textIdle = GD.KEY_GROUP_RADS)
    display.UpdateSelectKeyImages (GD.KEY_GROUP_RADS)

    # Display user prompt.
    display.DisplayMiddleLeftInfoPrompt (GD.RAD_SELECT_PROMPT)
        
    return 1
    
################################################################################
##
## Function: ProcessRadSelectKey (keyValue)
##
## Parameters: keyValue - integer - the keyValue of the selected zone
##
## Returns:
##
## Globals modified:
##
## Comments: Any rad select key is processed here.
##
################################################################################

def ProcessRadSelectKey (keyValue) :

    # We have a zone selected so move to rad select mode, keyboard and refresh select keys if we are not already there.
    if GD.currentMode != GD.MODE_RAD_ZONE_SELECT :
        GD.currentMode = GD.MODE_RAD_ZONE_SELECT
        display.DisplayKeyboardImage (useMode = GD.currentMode)
        display.UpdateSelectKeyImages (GD.KEY_GROUP_RADS)

    # Set the zone select key active.
    keyData.UpdateSelectKeyGroupText (keyValue, GD.KEY_GROUP_RADS)
    display.UpdateSelectKeyImages (GD.KEY_GROUP_RADS, GD.UPDATE_CHANGED)
        
    return 1
    
################################################################################
#
# Function: ProcessUfhKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments:The Ufh key takes you to the Ufh room select screen.
#
################################################################################

def ProcessUfhKey (zone) :

    # Only process if we are not already in ufh waiting mode.
    if  GD.currentMode != GD.MODE_UFH_WAITING_ZONE_SELECT :
    
        # Move to ufh waiting mode and display keyboard.
        GD.currentMode = GD.MODE_UFH_WAITING_ZONE_SELECT
        display.DisplayKeyboardImage (useMode = GD.currentMode)
        
        # Set ufh key active.
        #keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_UFH, GD.KEY_GROUP_WAITING_MODE)
       # display.UpdateSelectKeyImages (GD.KEY_GROUP_WAITING_MODE, GD.UPDATE_CHANGED)
   
        # Clear any previously active select key and display any active bands.
        keyData.UpdateSelectKeyGroupText (textIdle = GD.KEY_GROUP_UFH)
        display.UpdateSelectKeyImages (GD.KEY_GROUP_UFH)

        # Display user prompt.
        display.DisplayMiddleLeftInfoPrompt (GD.UFH_SELECT_PROMPT)
        
    return 1
    
################################################################################
#
# Function: ProcessUfhSelectKey (keyValue)
#
# Parameters: keyValue - integer - the keyValue of the selected zone
#
# Returns:
#
# Globals modified:
#
# Comments: Any ufh select key is processed here.
#
################################################################################

def ProcessUfhSelectKey (keyValue) :

    # We have a zone selected so move to ufh select mode, keyboard and refresh select keys if we are not already there.
    if GD.currentMode != GD.MODE_UFH_ZONE_SELECT :
        GD.currentMode = GD.MODE_UFH_ZONE_SELECT
        display.DisplayKeyboardImage (useMode = GD.currentMode)
        display.UpdateSelectKeyImages (GD.KEY_GROUP_UFH)

    # Set ufh select key active.
    keyData.UpdateSelectKeyGroupText (keyValue, GD.KEY_GROUP_UFH)
    display.UpdateSelectKeyImages (GD.KEY_GROUP_UFH, GD.UPDATE_CHANGED)
        
    return 1
    
################################################################################
##
## Function: ProcessSystemKey (zone)
##
## Parameters: zone - integer - the current zone
##
## Returns:
##
## Globals modified:
##
## Comments:The System key takes you to the System select screen. This screen allows you to select the mode the system
## will run in and to go to the options for each mode. We also call this function when we exit back here from another menu.
## We will check the config bits to determine which mode key to return to.
##
################################################################################

def ProcessSystemKey (zone) :

    # Scan through the system 'mode' keys to find which mode should be active.
    for systemKey in GD.KEY_GROUP_SYSTEM_MODE :
        systemBit = GD.KEY_TO_CONTROL_BIT_LOOKUP [systemKey]
        if system.systemControl [systemBit].CheckIfBitHigh () == True :       
            # Exit now we have found the active mode.
            break

    # Move to required mode.
    GD.currentMode = GD.KEY_TO_MODE_LOOKUP [systemKey]
    
    # Display keyboard for this mode
    display.DisplayKeyboardImage (useMode = GD.currentMode)

    # Read the config bits and update the bands on the control keys.
    keyData.SetControlBandStatus (GD.SYSTEM_CONTROL_GROUP, GD.KEY_GROUP_SYSTEM_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_SYSTEM_MODE, GD.UPDATE_ALL)

    # Display user prompt.
    display.DisplayMiddleLeftInfoPrompt (GD.SYSTEM_SELECT_PROMPT)

    return 1
    
################################################################################
##
## Function: ProcessNextProgramEntrytKey (zone)
##
## Parameters: zone - integer - the current zone
##
## Returns:
##
## Globals modified:
##
## Comments: The next and previous keys are used to cycle through entries in programming or status display modes.
##
################################################################################

def ProcessNextProgramEntrytKey (zone) :

    # Return to initial state if we are in ON AT, OFF AT or day select mode and turn all pointers on.
    if GD.currentMode in (GD.MODE_PROG_ON_AT, GD.MODE_PROG_OFF_AT, GD.MODE_PROG_DAYS_ON) :
        GD.currentMode = GD.MODE_PROG_DAY if GD.currentMode == GD.MODE_PROG_DAYS_ON else GD.MODE_PROG_TIME

    # Display the next programming data entry.
    display.DisplayProgEntry (99)
    display.DisplayBottomRightInfoPrompt ()

    return 1 

################################################################################
##
## Function: ProcessPreviousProgramEntrytKey (zone)
##
## Parameters: zone - integer - the current zone
##
## Returns:
##
## Globals modified:
##
## Comments: The next and previous keys are used to cycle through entries in programming or status display modes.
##
################################################################################

def ProcessPreviousProgramEntrytKey (zone) :

    # Return to initial state if we are in ON AT, OFF AT or day select mode and turn all pointers on.
    if GD.currentMode in (GD.MODE_PROG_ON_AT, GD.MODE_PROG_OFF_AT, GD.MODE_PROG_DAYS_ON) :
        GD.currentMode = GD.MODE_PROG_DAY if GD.currentMode == GD.MODE_PROG_DAYS_ON else GD.MODE_PROG_TIME

    # Display the previous programming data entry.
    display.DisplayProgEntry (-1)
    display.DisplayBottomRightInfoPrompt ()

    return 1 

################################################################################
#
# Function: ProcessRadSelectExitKey (keyValue)
#
# Parameters: keyValue - integer - the current key value
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessRadSelectExitKey (keyValue) :

    # Return to rad waiting select mode and keyboard.
    GD.currentMode = GD.MODE_RAD_WAITING_ZONE_SELECT
    display.DisplayKeyboardImage (useMode =  GD.currentMode)
    
    # Clear any previously active select key and display any active bands.
    keyData.UpdateSelectKeyGroupText (textIdle = GD.KEY_GROUP_RADS)
    display.UpdateSelectKeyImages (GD.KEY_GROUP_RADS)

    # Update prompts.
    display.DisplayMiddleLeftInfoPrompt (GD.RAD_SELECT_PROMPT)
    display.DisplayBottomLeftInfoPrompt (GD.INFO_1_BLANKED)
    display.DisplayZoneMode ()

    return 1
    
################################################################################
#
# Function: ProcessUfhSelectExitKey (keyValue)
#
# Parameters: keyValue - integer - the current key value
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessUfhSelectExitKey (keyValue) :

    # Return to ufh waiting select mode and keyboard.
    GD.currentMode = GD.MODE_UFH_WAITING_ZONE_SELECT
    display.DisplayKeyboardImage (useMode =  GD.currentMode)
    
    # Clear any previously active select key and display any active bands.
    keyData.UpdateSelectKeyGroupText (textIdle = GD.KEY_GROUP_UFH)
    display.UpdateSelectKeyImages (GD.KEY_GROUP_UFH)

    # Update prompts.
    display.DisplayMiddleLeftInfoPrompt (GD.UFH_SELECT_PROMPT)
    display.DisplayBottomLeftInfoPrompt (GD.INFO_1_BLANKED)
    display.DisplayZoneMode ()

    return 1
    
################################################################################
##
## Function: CheckForEditAbort (updateDisplay = True)
##
## Parameters: updateDisplay- boolean - if true redisplay the original data
##
## Returns:
##
## Globals modified:
##
## Comments: Check if any edit has been aborted and if it has restore and, if required, redisplay the original data.
##
################################################################################

def CheckForEditAbort (updateDisplay = True) :

    # Check if cursor character is still in data to see if an edit has been aborted and if it has restore the original data.
    if GD.EDIT_CURSOR in zones.zoneTimes.GetTime (GD.ON_TIME_INDEX) :
        zones.zoneTimes.RecoverPreEditTime (GD.ON_TIME_INDEX)
        if updateDisplay :
            display.DisplayProgOnTime () 
         
    elif GD.EDIT_CURSOR in zones.zoneTimes.GetTime (GD.OFF_TIME_INDEX) :
        zones.zoneTimes.RecoverPreEditTime (GD.OFF_TIME_INDEX)
        if updateDisplay :
            display.DisplayProgOffTimeAndDays () 
         




################################################################################
#
# Function: ProcessOnAtKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessOnAtKey (zone) :

    # We only process key if we are NOT already in ON AT mode.
    if  GD.currentMode != GD.MODE_PROG_ON_AT :

        # Save current mode.
        lastMode = GD.currentMode
    
        # Say we are now in ON AT programming mode.
        GD.currentMode = GD.MODE_PROG_ON_AT

        # Were we in DAY mode?
        if lastMode in (GD.MODE_PROG_DAY, GD.MODE_PROG_DAYS_ON) :
        
            # Switch to the program time keyboard.
            display.DisplayKeyboardImage (GD.TIME_SELECT_KEYBOARD_IMAGE)
               
        # Check if any edit has been aborted and if it has restore the original data. No need to update
        # display as we do this below.
        CheckForEditAbort (updateDisplay = False)
        
        # Blank the on time and set cursor on. Must be done after CheckForEditAbort.
        zones.zoneTimes.ClearTime (GD.ON_TIME_INDEX)
        zones.zoneTimes.SetCursor (GD.ON_TIME_INDEX, GD.EDIT_CURSOR)
        
        # Display the current programming data entry. Cursor will be at position 1 of on time.
        display.DisplayProgEntry (0, forceUpdate = True) 

    return 1 

################################################################################
#
# Function: ProcessOffAtKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessOffAtKey (zone) :

    # We only process key if we are NOT already in OFF AT mode.
    if  GD.currentMode != GD.MODE_PROG_OFF_AT :

        # Save current mode.
        lastMode = GD.currentMode
    
        # Say we are now in OFF AT programming mode.
        GD.currentMode = GD.MODE_PROG_OFF_AT

        # Were we in DAY mode?
        if lastMode in (GD.MODE_PROG_DAY, GD.MODE_PROG_DAYS_ON) :
        
            # Switch to the program time keyboard.
            display.DisplayKeyboardImage (GD.TIME_SELECT_KEYBOARD_IMAGE)
           
        # Check if any edit has been aborted and if it has restore the original data. No need to update
        # display as we do this below.
        CheckForEditAbort (updateDisplay = False)
        
        # Blank the off time and set cursor on. Must be done after CheckForEditAbort.
        zones.zoneTimes.ClearTime (GD.OFF_TIME_INDEX)
        zones.zoneTimes.SetCursor (GD.OFF_TIME_INDEX, GD.EDIT_CURSOR)
        
        # Display the current programming data entry. Cursor will be at position 1 of off time.
        display.DisplayProgEntry (0, forceUpdate = True) 

    return 1 

################################################################################
#
# Function: ProcessEditExitKey (keyValue)
#
# Parameters: keyValue - integer - the current key value
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessEditExitKey (keyValue) :

    # Check if cursor character is still in data to see if an edit has been aborted and if it has restore the original data.
    CheckForEditAbort () 
         
    # Return to time programming mode.
    GD.currentMode = GD.MODE_PROG_TIME
    display.DisplayKeyboardImage (useMode =  GD.currentMode)
   
    return 1
    
################################################################################
#
# Function: ProcessExitKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessExitKey (zone) :

  #  global GD.exitPending
   
    # Keep the current mode so we can check if it changes and we need to re-display the keyboard.
    lastCurrentMode = GD.currentMode

    # If the data has not changed or the user has pressed EXIT at the 'Save or Exit?' prompt we will exit back to a select mode.
    if zones.zoneTimes.CheckIfDataChanged () == False  or  GD.exitPending == True :
    
        # Clear info messages.
        display.DisplayBottomRightInfoPrompt ()     
        display.DisplayBottomLeftInfoPrompt (GD.BLANK_PROMPT)
        display.DisplayZoneMode ()
        

        # No exit pending now.
        GD.exitPending = False
        
        # Move back to a select mode. Use correct select for rad, ufh or sys.
        if zone < 14 :
            ProcessRadKey (zone)
        elif zone < 30 :
            ProcessUfhKey (zone)
        else :
            keysSystem.ProcessImmersionTimesKey (zone)
        
    # We have changed the data so we will set exit pending flag and prompt for save or exit.
    else :
        GD.exitPending = True
        display.DisplayBottomLeftInfoPrompt ()

    return 1 

################################################################################
#
# Function: ProcessSaveKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessSaveKey (zone) :

    # Only save if a change has been made.
    if zones.zoneTimes.CheckIfDataChanged () == True :
        zones.zoneTimes.UpdateProgramEntries ()

    # Return to initial state if we are in ON AT, OFF AT or day select mode.
    if GD.currentMode in (GD.MODE_PROG_ON_AT, GD.MODE_PROG_OFF_AT, GD.MODE_PROG_DAYS_ON) :
        GD.currentMode = GD.MODE_PROG_DAY if GD.currentMode == GD.MODE_PROG_DAYS_ON else GD.MODE_PROG_TIME

    # Clear the flag now we have saved data and update prompts.
    GD.exitPending = False
    display.DisplayBottomLeftInfoPrompt ()
    display.DisplayBottomRightInfoPrompt ()

    # We need to re-display as the current entry may be blank and will be removed on save. Go back to 1st entry.
    display.DisplayProgEntry (1, forceUpdate = True) 

    return 1 

################################################################################
#
# Function: ProcessEnableDisableKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessEnableDisableKey (zone) :

    # Only allow disable if we are in days entry mode.
    if GD.currentMode == GD.MODE_PROG_DAYS_ON :
        # Do disable/enable (toggle action).
        zones.zoneTimes.ModifyDay (GD.DAYS_INDEX, GD.DAYS_DISABLED)  
        # Update save prompt as we have changed the data.
        display.DisplayBottomLeftInfoPrompt ()
        display.DisplayBottomRightInfoPrompt ()
        # Display the Current programming data entry. Force a display update.
        display.DisplayProgEntry (0, forceUpdate = True)

    return 1 

################################################################################
#
# Function: ProcessAutoManualKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessAutoManualKey (zone) :

    # Switch between Auto and Manual mode with each press.
    zones.zoneTimes.SwitchModes ()
    display.DisplayBottomLeftInfoPrompt ()
    display.DisplayZoneMode (zone)


    return 1 

################################################################################
#
# Function: ProcessDayKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessDaysKey (zone) :

    #We only process key if we are NOT already in day edit mode
    if GD.currentMode != GD.MODE_PROG_DAYS_ON:
        
        # Say we are now in day edit mode.
        GD.currentMode = GD.MODE_PROG_DAYS_ON
        
        # Switch to the day entry program keyboard.
        display.DisplayKeyboardImage (GD.DAY_SELECT_KEYBOARD_IMAGE)
        
        # Check if any edit has been aborted and if it has restore the original data. No need to update
        # display as we do this below.
        CheckForEditAbort (updateDisplay = False)

        # Update info prompts.
        display.DisplayBottomLeftInfoPrompt ()
        display.DisplayBottomRightInfoPrompt ()

        # Display the Current programming data entry. Force a display update.
        display.DisplayProgEntry (0, forceUpdate = True)

    return 1 

################################################################################
#
# Function: ProcessClearKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessClearKey (zone) :

  #  global GD.clearPending

    if GD.currentMode == GD.MODE_PROG_ON_AT :

        # Clear the on time.
        zones.zoneTimes.ClearTime (GD.ON_TIME_INDEX)
        # Display the new time.
        display.DisplayProgOnTime ()

    elif GD.currentMode == GD.MODE_PROG_OFF_AT :

        # Clear the off time.
        zones.zoneTimes.ClearTime (GD.OFF_TIME_INDEX)
        # Display the new time.
        display.DisplayProgOffTimeAndDays ()

    elif GD.currentMode == GD.MODE_PROG_DAYS_ON  and zones.zoneTimes.CheckIfDisabled (GD.DAYS_INDEX) == False :

        # Clear the days if we are not disabled.
        zones.zoneTimes.ClearDays (GD.DAYS_INDEX)
        # Display the new day info. Days info is displayed with the off time.
        display.DisplayProgOffTimeAndDays ()

    elif GD.currentMode in (GD.MODE_PROG_TIME, GD.MODE_PROG_DAY)  :

        if GD.clearPending == True :
            GD.clearPending = False
            # Clear the on time
            zones.zoneTimes.ClearTime (GD.ON_TIME_INDEX)
            # Clear the off time
            zones.zoneTimes.ClearTime (GD.OFF_TIME_INDEX)
            # Clear the days
            zones.zoneTimes.ClearDays (GD.DAYS_INDEX)

            # Display the on time, off time and days.
            display.DisplayProgOnTime ()
            display.DisplayProgOffTimeAndDays ()

        else :
            GD.clearPending = True
            
    # Update info prompts now we have chaged the data
    display.DisplayBottomLeftInfoPrompt ()
    display.DisplayBottomRightInfoPrompt ()


    return 1 

################################################################################
#
# Function: ProcessNewKey (zone)
#
# Parameters: zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessNewKey (zone) :

    #Limit number of entries to a reasonable number.
    if  zones.zoneTimes.GetNumberOfProgramEntries () < 8 :
        # Create new entry and get the number.
        newEntryNumber = zones.zoneTimes.AddNewEntry ()

        # Return to initial state if we are in ON AT, OFF AT or day select mode.
        if GD.currentMode in (GD.MODE_PROG_ON_AT, GD.MODE_PROG_OFF_AT, GD.MODE_PROG_DAYS_ON) :
            GD.currentMode = GD.MODE_PROG_DAY if GD.currentMode == GD.MODE_PROG_DAYS_ON else GD.MODE_PROG_TIME

        # Update info prompts now we have changed the data.
        display.DisplayBottomLeftInfoPrompt ()
        display.DisplayBottomRightInfoPrompt ()

        # Display the new programming data entry.
        display.DisplayProgEntry (newEntryNumber, forceUpdate = True) 

    return 1 

################################################################################
#
# Function: ProcessDigitKey (key)
#
# Parameters: key - integer - the digits key code (50=0, 51=1...59=9)
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessDigitKey (key) :

    # Only process key if we are in a time on or off edit mode.
    if GD.currentMode in (GD.MODE_PROG_ON_AT, GD.MODE_PROG_OFF_AT) :

        # Convert keycode to character '0' to '9'
        key = chr (key-2)

        if GD.currentMode == GD.MODE_PROG_ON_AT :
            # Update and display the on time. Call to modify will return -ve when all digits done and +ve if OK.
            status = zones.zoneTimes.ModifyTime (GD.ON_TIME_INDEX, key)
            display.DisplayProgOnTime ()

        else :
            # Update and display the off time. Call to modify will return -ve when all digits done and +ve if OK.
            status = zones.zoneTimes.ModifyTime (GD.OFF_TIME_INDEX, key)
            display.DisplayProgOffTimeAndDays ()
           
        # Update save and valid prompts now we have changed the data
        display.DisplayBottomLeftInfoPrompt ()
        display.DisplayBottomRightInfoPrompt ()
        
        # Check to see if we have edited all the digits.
        if status < 0 :
            # Return to time programming mode.
            GD.currentMode = GD.MODE_PROG_TIME
            display.DisplayKeyboardImage (useMode =  GD.currentMode)
    
    
    return 1

################################################################################
#
# Function: ProcessDayOfWeekKey (key)
#
# Parameters: key - integer - the days key code (60=Mon...66=Sun, 67=M to F, 68=S & S, 69 = everyday)
#
# Returns:
#
# Globals modified:
#
# Comments: Day keys Mon to Sun are toggle action, M to F, S & S and everyday will turn the days on at 1st press then off
#
################################################################################

def ProcessDayOfWeekKey (key) :

    # Only process key if we are in correct mode and not disabled.
    if GD.currentMode == GD.MODE_PROG_DAYS_ON and zones.zoneTimes.CheckIfDisabled (GD.DAYS_INDEX) == False :
        # Convert keycode to values 0 to 9 so we can use as index to string of days.
        key = key-60

        # Update the day.
        zones.zoneTimes.ModifyDay (GD.DAYS_INDEX, key)
        # Display the new day info.
        display.DisplayProgOffTimeAndDays ()
        
        # Update the save and valid prompts now we have changed the data.
        display.DisplayBottomLeftInfoPrompt ()
        display.DisplayBottomRightInfoPrompt ()

    return 1

################################################################################
#
# Function: ProcessWakeupKey (zone)
#
# Parameters: zone - integer - the last selected zone
#
# Returns:
#
# Globals modified:
#
# Comments: Called when the user touches the blank screen to wake up the screen.
#
################################################################################

def ProcessWakeupKey (zone) :
    
    # Start up the display by setting the correct form. Clear any info messages.
    display.DisplayForm (GD.MAIN_SCREEN_FORM)
    display.DisplayBottomLeftInfoPrompt (GD.BLANK_PROMPT)     
    display.DisplayBottomRightInfoPrompt () 
   
    # Check if the system is on or off. If we are on we display the rad select screen. If we are off we display the system screen.
    if system.systemControl [GD.SYSTEM_OFF_MODE].CheckIfBitHigh () == True :       
        ProcessSystemKey (-1)
    else:
        ProcessRadKey (-1)
    
    display.WriteToDisplay (GD.BACKLIGHT_HALF)

    return 1

################################################################################
#
# Function: ProcessFinishedKey (zone)
#
# Parameters: zone - integer - the last selected zone
#
# Returns:
#
# Globals modified:
#
# Comments: Switches back to run mode to enable I/O operation again.
#
################################################################################

def ProcessFinishedKey (zone) :

    # Force run mode by clearing timer so we get an instant run.
    GD.timeToRunMode = 0
    return 1

################################################################################
#
# Function: ProcessKeys (keyValue, zone)
#
# Parameters: keyValue - integer - the key value to process
#                      zone - integer - the current zone
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ProcessKeys (keyValue, zone) :

    # Dictionary holds keycodes with functions to call.
    keyList = {

        GD.KEYVALUE_DAY : ProcessDaysKey,
        GD.KEYVALUE_BOOST : ProcessBoostKey,
        GD.KEYVALUE_CAN_RES : ProcessCanResKey,
        GD.KEYVALUE_PROGRAM : ProcessProgramKey,
        GD.KEYVALUE_RAD : ProcessRadKey,
        GD.KEYVALUE_UFH : ProcessUfhKey,
        GD.KEYVALUE_NEXT_PROGRAM_ENTRY : ProcessNextProgramEntrytKey,
        GD.KEYVALUE_NEXT_STATUS_ENTRY : keysSystem.ProcessNextStatusEntrytKey,
        GD.KEYVALUE_PREV_PROGRAM_ENTRY : ProcessPreviousProgramEntrytKey,
        GD.KEYVALUE_PREV_STATUS_ENTRY : keysSystem.ProcessPreviousStatusEntrytKey,
        GD.KEYVALUE_ON_AT : ProcessOnAtKey,
        GD.KEYVALUE_OFF_AT : ProcessOffAtKey,
        GD.KEYVALUE_CLEAR : ProcessClearKey,
        GD.KEYVALUE_SAVE : ProcessSaveKey,
        GD.KEYVALUE_NEW : ProcessNewKey,
        GD.KEYVALUE_ENABLE_DISABLE : ProcessEnableDisableKey,
        GD.KEYVALUE_AUTO_MANUAL : ProcessAutoManualKey,
        GD.KEYVALUE_WAKEUP : ProcessWakeupKey,
        GD.KEYVALUE_SYSTEM : ProcessSystemKey,
        GD.KEYVALUE_FINISHED : ProcessFinishedKey,

        GD.KEYVALUE_SYSTEM_OFF : keysSystem.ProcessSystemModeKeys,
        GD.KEYVALUE_AUTO_MODE : keysSystem.ProcessSystemModeKeys,
        GD.KEYVALUE_MANUAL_MODE : keysSystem.ProcessSystemModeKeys,
        GD.KEYVALUE_HOLIDAY_MODE : keysSystem.ProcessSystemModeKeys,
        
        GD.KEYVALUE_SYSTEM_OPTIONS : keysSystem.ProcessSystemOptionsKey,
        GD.KEYVALUE_MANUAL_OPTIONS : keysSystem.ProcessManualOptionsKey,
        GD.KEYVALUE_AUTO_OPTIONS : keysSystem.ProcessAutoOptionsKey,
        GD.KEYVALUE_HOLIDAY_OPTIONS : keysSystem.ProcessHolidayOptionsKey,

        GD.KEYVALUE_IMMERSION_TIMES : keysSystem.ProcessImmersionTimesKey,

        GD.KEYVALUE_T1_TO_HEAT : keysSystem.ProcessT1ToHeatingKey,
        GD.KEYVALUE_T2_TO_HEAT : keysSystem.ProcessT2ToHeatingKey,
        GD.KEYVALUE_OIL_TO_HEAT : keysSystem.ProcessOilToHeatingKey,
        GD.KEYVALUE_OIL_TO_T1 : keysSystem.ProcessOilToT1Key,
        GD.KEYVALUE_OIL_TO_T2 : keysSystem.ProcessOilToT2Key,
        GD.KEYVALUE_OIL_OFF : keysSystem.ProcessOilOffKey,
        GD.KEYVALUE_MANUAL_OVERRIDE : keysSystem.ProcessManualOverrideKey,
        GD.KEYVALUE_DISPLAY_STATUS : keysSystem.ProcessDisplayStatusKey,
        
        GD.KEYVALUE_IMMERSION_CONTROL : keysSystem.ProcessManualOverrideKeySubMenu,
        GD.KEYVALUE_WOODBURNER_CONTROL : keysSystem.ProcessManualOverrideKeySubMenu,
        GD.KEYVALUE_TANK_1_CONTROL : keysSystem.ProcessManualOverrideKeySubMenu,
        GD.KEYVALUE_TANK_2_CONTROL : keysSystem.ProcessManualOverrideKeySubMenu,
        GD.KEYVALUE_HEATING_CONTROL : keysSystem.ProcessManualOverrideKeySubMenu,
        GD.KEYVALUE_BOILER_CONTROL : keysSystem.ProcessManualOverrideKeySubMenu,
        
        GD.KEYVALUE_EXIT : ProcessExitKey,
        GD.KEYVALUE_RAD_SELECT_EXIT : ProcessRadSelectExitKey,
        GD.KEYVALUE_UFH_SELECT_EXIT : ProcessUfhSelectExitKey,
        GD.KEYVALUE_EDIT_EXIT : ProcessEditExitKey,
        GD.KEYVALUE_RETURN_TO_SYSTEM_EXIT : ProcessSystemKey,
        GD.KEYVALUE_MANUAL_CONTROL_MAIN_MENU_EXIT : keysSystem.ProcessManualOptionsKey,
        GD.KEYVALUE_MANUAL_CONTROL_OPTION_EXIT : keysSystem.ProcessManualOverrideKey,
        GD.KEYVALUE_RETURN_TO_SYSTEM_OPTIONS_EXIT : keysSystem.ProcessSystemOptionsKey
    }

    # If we have a pending exit we need to check if the key is SAVE, EXIT or something else.
    if GD.exitPending == True  and keyValue not in (GD.KEYVALUE_SAVE, GD.KEYVALUE_EXIT) :
        # Not SAVE or EXIT so clear pending status.
        GD.exitPending = False
        display.DisplayBottomLeftInfoPrompt ()
        
    # If we have a pending clear we need to check if the key is CLEAR or something else.
    if GD.clearPending == True  and keyValue != GD.KEYVALUE_CLEAR :
        # Not CLEAR so clear pending status.
        GD.clearPending = False
        display.DisplayBottomLeftInfoPrompt ()
        
    # If the key is a general control type key then call the function for the supplied key.
    if keyValue in keyList :
        # If we are processing a system key we pass the key value to the function.
        # If it is a zone control or edit key we pass the current zone.
        passData = keyValue if keyValue >= GD.SYSTEM_KEY_START else zone        
        status = keyList [keyValue] (passData)
        
    # Is it a manual override key? These all call the same function.
    elif keyValue in (GD.KEY_GROUP_ALL_MANUAL_OVERRIDE) :
        
        # At present imm 3 and imm 4 are in parallel so we need to activate both.
#        if keyValue in (GD.KEYVALUE_IMM_3_ON, GD.KEYVALUE_IMM_4_ON) :
#            status = keysSystem.ProcessManualOverrideOnOffKey (GD.KEYVALUE_IMM_3_ON)
#            status = keysSystem.ProcessManualOverrideOnOffKey (GD.KEYVALUE_IMM_4_ON)
#        elif keyValue in (GD.KEYVALUE_IMM_3_OFF, GD.KEYVALUE_IMM_4_OFF) :
#            status = keysSystem.ProcessManualOverrideOnOffKey (GD.KEYVALUE_IMM_3_OFF)
#            status = keysSystem.ProcessManualOverrideOnOffKey (GD.KEYVALUE_IMM_4_OFF)
#        else :
        # Process key
        status =  keysSystem.ProcessManualOverrideOnOffKey (keyValue)
    
    # Is it a rad select key?, these all call the same function. 
    elif keyValue in GD.KEY_GROUP_RADS :
        status = ProcessRadSelectKey (keyValue)

    # Is it a ufh select key?, these all call the same function. 
    elif keyValue in GD.KEY_GROUP_UFH :
        status = ProcessUfhSelectKey (keyValue)

    # Is it an immersion select key?, these all call the same function. 
    elif keyValue in GD.KEY_GROUP_IMMERSIONS :
        status = keysSystem.ProcessImmersionSelectKey (keyValue)

    # Is it a numeric key?, these all call the same function. 
    elif keyValue in GD.KEY_GROUP_NUMERIC :
        status = ProcessDigitKey (keyValue)

    # Is it a day key?, these all call the same function. 
    elif keyValue in GD.KEY_GROUP_DAYS :
        status = ProcessDayOfWeekKey (keyValue)
            
    # Is it a status key?, these all call the same function. 
    elif keyValue in GD.KEY_GROUP_STATUS :
        status = keysSystem.ProcessStatusKey (keyValue)
            
    return 

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





