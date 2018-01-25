print 'Loaded keysSystem module'
import time
import GD
import display
import zones
import keys
import keyData
import system


#################################################################################### Function: ProcessSystemModeKeys (keyValue)#### Parameters: keyValue - integer - the current key value#### Returns:#### Globals modified:#### Comments:The Off, Auto, Manual and Holiday mode keys call this function. We will switch to the required mode and## display the correct keyboard.##
################################################################################

def ProcessSystemModeKeys (keyValue) :

    # Move to required mode.
    GD.currentMode = GD.KEY_TO_MODE_LOOKUP [keyValue]
    
    # Display keyboard for this mode
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    
    # Get config bit for this mode.
    systemBit = GD.KEY_TO_CONTROL_BIT_LOOKUP [keyValue]
    
    # Set the config bit and clear the other config bits.
    system.UpdateSystemControlBits (bitsHigh = systemBit, bitsLow = GD.SYSTEM_CONTROL_GROUP)
    
    # Make key text active and clear other mode keys.
    keyData.UpdateSelectKeyGroupText (textActive = keyValue, textIdle = GD.KEY_GROUP_SYSTEM_MODE)

    # Now read the config bits and update the bands on all the system control keys. 
    keyData.SetControlBandStatus (GD.SYSTEM_CONTROL_GROUP, GD.KEY_GROUP_SYSTEM_MODE)

    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_SYSTEM_MODE, GD.UPDATE_ALL)
    
    # Update all the zone statuses. We do this so that the zone on/off bands will show which zones will be turning on when we
    # have switched from off mode to one of the active modes (man, auto or holiday).
    for zone in range (0, 30) :
        zones.UpdateZoneStatus (zone)

    return 1

################################################################################
##
## Function: ProcessDisplayStatusKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The display status key takes you to the screen where all the system status can be viewed.
##
################################################################################

def ProcessDisplayStatusKey (keyValue) :

    # Move to display status mode and display keyboard and prompt.
    GD.currentMode = GD.MODE_DISPLAY_STATUS
    display.DisplayKeyboardImage (useMode = GD.currentMode)    
    display.DisplayMiddleLeftInfoPrompt (GD.DISPLAY_STATUS_PROMPT)
   
    return 1
 
################################################################################
##
## Function: ProcessStatusKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments: Displays the status group selected. This function will display the 1st status and further status in this group
## will be displayed using the next and previous keys.
##
################################################################################

def ProcessStatusKey (keyValue) :

    # Make key text active and clear other mode keys.
    keyData.UpdateSelectKeyGroupText (textActive = keyValue, textIdle = GD.KEY_GROUP_STATUS)

    # Save the index for the 1st status so that we know which status is currently displayed.
    system.systemControl [GD.SYSTEM_NONE].SaveStatusIndex (1)
    
    # Display the 1st status. The number of statuses available is returned so we can check if there are more statuses to display
    # and set the 'Next' key on if there are.
    numberOfStatus = display.DisplayStatus (keyValue, 1)
    
    # Clear the 'previous key'.
    display.DisplayKeyImageSequence (GD.KEYVALUE_PREV_STATUS_ENTRY, GD.KEY_IMAGE_BLANK)
    
    # If there is more than 1 status display the 'next' key.
    if numberOfStatus > 1 :
        display.DisplayKeyImageSequence (GD.KEYVALUE_NEXT_STATUS_ENTRY, GD.KEY_IMAGE_NEXT)
    else :
        display.DisplayKeyImageSequence (GD.KEYVALUE_NEXT_STATUS_ENTRY, GD.KEY_IMAGE_BLANK)

    return 1
 
################################################################################
##
## Function: ProcessNextStatusEntrytKey (keyvalue)
##
## Parameters: keyvalue - integer - the current zone
##
## Returns:
##
## Globals modified:
##
## Comments: The next and previous keys are used to cycle through entries in programming or status display modes.
##
################################################################################

def ProcessNextStatusEntrytKey (keyValue) :

    # Get the number of statuses and the number of the status currently displayed.
    numberOfStatus = display.DisplayStatus (keyValue)
    currentStatus = system.systemControl [GD.SYSTEM_NONE].GetStatusIndex ()
    
    # If we are not on the last status go to the next status and display it. Save index for later use.
    if currentStatus < numberOfStatus :
        currentStatus += 1
        display.DisplayStatus (keyValue, currentStatus)
        system.systemControl [GD.SYSTEM_NONE].SaveStatusIndex (currentStatus)
    
    # If there are more statuses to display then show the 'next' key.
    if currentStatus < numberOfStatus :
        display.DisplayKeyImageSequence (GD.KEYVALUE_NEXT_STATUS_ENTRY, GD.KEY_IMAGE_NEXT)
    
    # If we are not on the 1st status show the 'previous' key.
    if currentStatus > 1 :
        display.DisplayKeyImageSequence (GD.KEYVALUE_PREV_STATUS_ENTRY, GD.KEY_IMAGE_PREVIOUS)

################################################################################
##
## Function: ProcessPreviousStatusEntrytKey (keyvalue)
##
## Parameters: keyvalue - integer - the current zone
##
## Returns:
##
## Globals modified:
##
## Comments: The next and previous keys are used to cycle through entries in programming or status display modes.
##
################################################################################

def ProcessPreviousStatusEntrytKey (keyValue) :

    # Get the number of statuses and the number of the status currently displayed.
    numberOfStatus = display.DisplayStatus (keyValue)
    currentStatus = system.systemControl [GD.SYSTEM_NONE].GetStatusIndex ()
    
    # If we are not on the 1st status go to the previous status and display it. Save index for later use.
    if currentStatus > 1 :
        currentStatus -= 1
        display.DisplayStatus (keyValue, currentStatus)
        system.systemControl [GD.SYSTEM_NONE].SaveStatusIndex (currentStatus)
    
    # If there are more statuses to display then show the 'next' key.
    if currentStatus < numberOfStatus :
        display.DisplayKeyImageSequence (GD.KEYVALUE_NEXT_STATUS_ENTRY, GD.KEY_IMAGE_NEXT)
    
    # If we are not on the 1st status show the 'previous' key.
    if currentStatus > 1 :
        display.DisplayKeyImageSequence (GD.KEYVALUE_PREV_STATUS_ENTRY, GD.KEY_IMAGE_PREVIOUS)


################################################################################
##
## Function: ProcessSystemOptionsKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The system options key takes you to the screen where system options can be set.
##
################################################################################

def ProcessSystemOptionsKey (keyValue) :

    # Move to system options select mode and display keyboard and prompt.
    GD.currentMode = GD.MODE_SYSTEM_OPTIONS
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    display.DisplayMiddleLeftInfoPrompt (GD.SYSTEM_OPTIONS_PROMPT)
   
    return 1
 
################################################################################
##
## Function: ProcessImmersionTimesKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The immersion times key takes you to the screen where the immersion (1 to 4) to program is selected.
##
################################################################################

def ProcessImmersionTimesKey (keyValue) :

    # Move to immersion times select mode and display keyboard.
    GD.currentMode = GD.MODE_IMMERSION_WAITING_SELECT
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    
    # Clear any previously active select key and display any active bands.
    keyData.UpdateSelectKeyGroupText (textIdle = GD.KEY_GROUP_IMMERSIONS)
    display.UpdateSelectKeyImages (GD.KEY_GROUP_IMMERSIONS)

    # Display user prompt.
    display.DisplayMiddleLeftInfoPrompt (GD.SELECT_IMMERSION_PROMPT)
   
    return 1
 
################################################################################
##
## Function: ProcessImmersionSelectKey (keyValue)
##
## Parameters: keyValue - integer - the keyValue of the selected zone
##
## Returns:
##
## Globals modified:
##
## Comments: Any immersion select key is processed here. If the immersion is in override mode we do not allow any actions
## and warn the user.
##
################################################################################

def ProcessImmersionSelectKey (keyValue) :

    # Check if we are in override. If we are; move back to waiting select and warn user no operation allowed.
    if system.systemControl [GD.KEY_TO_CONTROL_BIT_LOOKUP [keyValue]].CheckIfOverrideActive () == True :
        GD.currentMode = GD.MODE_IMMERSION_WAITING_SELECT
        display.DisplayKeyboardImage (useMode = GD.currentMode)
        display.DisplayMiddleLeftInfoPrompt (GD.OPTIONS_DISABLED_PROMPT)
        
    else :
        # We have a zone selected so move to immersion select mode, keyboard and refresh select keys if we are not already there.
        if GD.currentMode != GD.MODE_IMMERSION_SELECT :
            GD.currentMode = GD.MODE_IMMERSION_SELECT
            display.DisplayKeyboardImage (useMode = GD.currentMode)
            display.UpdateSelectKeyImages (GD.KEY_GROUP_IMMERSIONS)

    # Set the zone select key active.
    keyData.UpdateSelectKeyGroupText (keyValue, GD.KEY_GROUP_IMMERSIONS)
    display.UpdateSelectKeyImages (GD.KEY_GROUP_IMMERSIONS, GD.UPDATE_CHANGED)
        
    return 1
    
#################################################################################### Function: ProcessAutoOptionsKey (keyValue)#### Parameters: keyValue - integer - the current key value#### Returns:#### Globals modified:#### Comments:The Auto options key takes you to the screen where auto options can be set.##
################################################################################

def ProcessAutoOptionsKey (keyValue) :

    # Move to auto options select mode and display keyboard and prompt.
    GD.currentMode = GD.MODE_AUTO_OPTIONS
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    display.DisplayMiddleLeftInfoPrompt (GD.AUTO_OPTIONS_PROMPT)
   
    return 1
 
################################################################################
#### Function: ProcessManualOptionsKey (keyValue)#### Parameters: keyValue - integer - the current key value#### Returns:## ## Globals modified:#### Comments:The Manual options key takes you to the screen where manual options can be set. If a manual override is in
## operation we prevent the user from selecting any manual option as these will not be valid. The prompt will be set to
## inform the user.##
################################################################################

def ProcessManualOptionsKey (keyValue) :

    # Move to manual options select mode and display keyboard.
    GD.currentMode = GD.MODE_MANUAL_OPTIONS
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    
    # We have displayed a select keyboard so we need to set the select keys text idle and clear any bands.
    keyData.UpdateSelectKeyGroupText  (textIdle = GD.KEY_GROUP_MANUAL_MODE)
    keyData.UpdateSelectKeyGroupBand (bandNone = (GD.KEY_GROUP_MANUAL_MODE))

    # Clear any previous band on manual control key and select keys on the following menu.
    keyData.SetDefaultKeyImage (GD.KEYVALUE_MANUAL_OVERRIDE)
    keyData.UpdateSelectKeyGroupText  (textIdle = GD.KEY_GROUP_MANUAL_CONTROL_SELECT)
    keyData.UpdateSelectKeyGroupBand (bandNone = (GD.KEY_GROUP_MANUAL_CONTROL_SELECT))

    # We will check if an override is active for any manual controls. If it is we will set the manual control key and the select key
    # on the following menu to flash (yellow band). We will move to manual options disabled mode so the user cannot select a
    # manual option except manual control.
    
    # Get each manual control group.
    for group in range (0, len (GD.ALL_MANUAL_OVERRIDE_GROUPS)) :
        # Scan each group.
        for controlBit in GD.ALL_MANUAL_OVERRIDE_GROUPS [group] :
            # If the override bit is active set band flashing on manual control key and the select key on following menu.
            if system.systemControl [controlBit].CheckIfOverrideActive () == True :
                keyData.SetKeyBand1Flashing (GD.KEYVALUE_MANUAL_OVERRIDE)
                keyData.SetKeyBand1Flashing (GD.KEY_GROUP_MANUAL_CONTROL_SELECT [group])
                # If this is a manual control for tank 1, tank 2 or the boiler then disable manual options
                if controlBit in (GD.DISABLED_MANUAL_OVERRIDE_GROUPS) :
                    GD.currentMode = GD.MODE_MANUAL_OPTIONS_DISABLED

    # If we are NOT disabled read the config bits and update the bands on the control keys. There are 2 groups of keys: the heating
    # control keys and the boiloer control keys.
    if GD.currentMode == GD.MODE_MANUAL_OPTIONS :
        
        keyData.SetControlBandStatus (GD.HEATING_MANUAL_CONTROL_GROUP, GD.KEY_GROUP_HEATING_MODE)
        keyData.SetControlBandStatus (GD.BOILER_MANUAL_CONTROL_GROUP, GD.KEY_GROUP_BOILER_MODE)
        
        # Display all the control keys with their new band status.
        display.UpdateSelectKeyImages (GD.KEY_GROUP_MANUAL_MODE, GD.UPDATE_ALL)
    
        # Tell user they can select an option.
        userPrompt = GD.MANUAL_OPTIONS_PROMPT       
        
    else :
    
        # Tell user options not available
        userPrompt = GD.OPTIONS_DISABLED_PROMPT
        
    # Display new prompt to user.
    display.DisplayMiddleLeftInfoPrompt (userPrompt)
   
    return 1
    
#################################################################################### Function: ProcessHolidayOptionsKey (keyValue)#### Parameters: keyValue - integer - the current key value#### Returns:#### Globals modified:#### Comments:The Holiday options key takes you to the screen where holiday options can be set.##
################################################################################

def ProcessHolidayOptionsKey (keyValue) :

    # Move to holiday options select mode and display keyboard and prompt.
    GD.currentMode = GD.MODE_HOLIDAY_OPTIONS
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    display.DisplayMiddleLeftInfoPrompt (GD.HOLIDAY_OPTIONS_PROMPT)
   
    return 1
    
#################################################################################### Function: ProcessT1ToHeatingKey (keyValue)#### Parameters: keyValue - integer - the current key value#### Returns:#### Globals modified:#### Comments: The T1 to Heating key will set Tank 1 to feed the heating circuits. The key will show as active and## the on band will be set on. The T2 to Heating and Oil to Heating keys will be set to their idle state. If Oil to heating is## active we will set the oil boiler off.##
################################################################################

def ProcessT1ToHeatingKey (keyValue) :

    # Do not process if we are disabled.
    if GD.currentMode == GD.MODE_MANUAL_OPTIONS_DISABLED : return 1
    
    # If oil to heating is active we need to make it idle and set boiler to off. Set boiler off key text active. Note this test must
    # be done first before we change any config bits.
    if (system.systemControl [GD.SYSTEM_MANUAL_OIL_BOILER_TO_HEATING].CheckIfBitHigh () == True) :
         
        system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_OIL_BOILER_OFF, bitsLow = GD.BOILER_MANUAL_CONTROL_GROUP)
        keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_OIL_OFF, textIdle = GD.KEY_GROUP_BOILER_MODE)
        
    # Set the T1 to heating config bit and make T1 to heating key text active.
    system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_TANK_1_TO_HEATING, bitsLow = GD.HEATING_MANUAL_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_T1_TO_HEAT, textIdle = GD.KEY_GROUP_HEATING_MODE)
    
    # Read the config bits and update the bands on all the manual option control keys. 
    keyData.SetControlBandStatus (GD.ALL_MANUAL_CONTROL_GROUP, GD.KEY_GROUP_MANUAL_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_MANUAL_MODE, GD.UPDATE_ALL)
   
    return 1
    
#################################################################################### Function: ProcessT2ToHeatingKey (keyValue)#### Parameters: keyValue - integer - the current key value#### Returns:#### Globals modified:#### Comments: The T2 to Heating key will set Tank 2 to feed the heating circuits. The key will show as active and## the on band will be set on. The T1 to Heating and Oil to Heating keys will be set to their idle state.  If Oil to heating is## active we will set the oil boiler off. If Oil to T1 is currently active we will set it to idle and set Oil boiler to off as T2 and Oil  ## share the same pipework to feed T1 and the heating, hence only one can be active at once. ##################################################################################

def ProcessT2ToHeatingKey (keyValue) :

    # Do not process if we are disabled.
    if GD.currentMode == GD.MODE_MANUAL_OPTIONS_DISABLED : return 1
    
    # If oil to heating or oil to T1 is active we need to make it idle and set boiler to off. Set boiler off key text active.
    # Note this test must be done first before we change any config bits.
    if (system.systemControl [GD.SYSTEM_MANUAL_OIL_BOILER_TO_HEATING].CheckIfBitHigh () == True
        or
        system.systemControl [GD.SYSTEM_MANUAL_OIL_BOILER_TO_TANK1].CheckIfBitHigh () == True) :
        
            system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_OIL_BOILER_OFF, bitsLow = GD.BOILER_MANUAL_CONTROL_GROUP)
            keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_OIL_OFF, textIdle = GD.KEY_GROUP_BOILER_MODE)
        
     # Set the T2 to heating config bit and make T2 to heating key text active.
    system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_TANK_2_TO_HEATING, bitsLow = GD.HEATING_MANUAL_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_T2_TO_HEAT, textIdle = GD.KEY_GROUP_HEATING_MODE)
    
   # Read the config bits and update the bands on all the manual option control keys. 
    keyData.SetControlBandStatus (GD.ALL_MANUAL_CONTROL_GROUP, GD.KEY_GROUP_MANUAL_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_MANUAL_MODE, GD.UPDATE_ALL)
    
    return 1
    
################################################################################
##
## Function: ProcessOilToHeatingKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments: The Oil to Heating key will set the oil boiler to feed the heating circuits. The key is set active and the green band
## will be set on. The T1 to Heating ,T2 to Heating, Oil to T1, Oil to T2 and Oil off  keys will be set to their idle state.
##
################################################################################

def ProcessOilToHeatingKey (keyValue) :

    # Do not process if we are disabled.
    if GD.currentMode == GD.MODE_MANUAL_OPTIONS_DISABLED : return 1
    
    # Set the Oil to heating config bit and make Oil to heating key text active.
    system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_OIL_BOILER_TO_HEATING, bitsLow = GD.ALL_MANUAL_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_OIL_TO_HEAT, textIdle = GD.KEY_GROUP_MANUAL_MODE)
    
    # Read the config bits and update the bands on all the manual option control keys. 
    keyData.SetControlBandStatus (GD.ALL_MANUAL_CONTROL_GROUP, GD.KEY_GROUP_MANUAL_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_MANUAL_MODE, GD.UPDATE_ALL)

    return 1
    
################################################################################
##
## Function: ProcessOilToT1Key (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments: The Oil to T1 key will set the oil boiler to feed tank 1. The key is set active and the green band
## will be set on. The Oil to Heating ,T2 to Heating,  Oil to T2 and Oil off  keys will be set to their idle state.
## If oil to heating is or T2 to heating is active we will set it to idle and set T1 to heating as T2 and Oil share the
## same pipework to feed T1 or the heating, hence only one can be active at once. 
##
################################################################################

def ProcessOilToT1Key (keyValue) :

    # Do not process if we are disabled.
    if GD.currentMode == GD.MODE_MANUAL_OPTIONS_DISABLED : return 1
    
    # If oil to heating or T2 to heating is active we need to make it idle and set T1 to heating. Set T1 to heating key text active.
    # Note this test must be done first before we change any config bits.
    if (system.systemControl [GD.SYSTEM_MANUAL_OIL_BOILER_TO_HEATING].CheckIfBitHigh () == True
        or
        system.systemControl [GD.SYSTEM_MANUAL_TANK_2_TO_HEATING].CheckIfBitHigh () == True) :
        
            system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_TANK_1_TO_HEATING, bitsLow = GD.HEATING_MANUAL_CONTROL_GROUP)
            keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_T1_TO_HEAT, textIdle = GD.KEY_GROUP_HEATING_MODE)
        
    # Set the Oil to T1 config bit and make Oil to T1 key text active.
    system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_OIL_BOILER_TO_TANK1, bitsLow = GD.BOILER_MANUAL_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_OIL_TO_T1, textIdle = GD.KEY_GROUP_BOILER_MODE)
    
   # Read the config bits and update the bands on all the manual option control keys. 
    keyData.SetControlBandStatus (GD.ALL_MANUAL_CONTROL_GROUP, GD.KEY_GROUP_MANUAL_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_MANUAL_MODE, GD.UPDATE_ALL)
    
    return 1
    
################################################################################
##
## Function: ProcessOilToT2Key (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments: The Oil to T2 key will set the oil boiler to feed tank 2. The key is set active and the green band
## will be set on. The Oil to Heating, Oil to T1 and Oil off  keys will be set to their idle state.
## If oil to heating is active we will set it to idle and set T1 to heating as T2 and Oil share the
## same pipework to feed T1 or the heating, hence only one can be active at once. 
##
################################################################################

def ProcessOilToT2Key (keyValue) :

    # Do not process if we are disabled.
    if GD.currentMode == GD.MODE_MANUAL_OPTIONS_DISABLED : return 1
    
    # If oil to heating is active we need to make it idle and set T1 to heating. Set T1 to heating key text active.
    # Note this test must be done first before we change any config bits.
    if (system.systemControl [GD.SYSTEM_MANUAL_OIL_BOILER_TO_HEATING].CheckIfBitHigh () == True) :
    
        system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_TANK_1_TO_HEATING, bitsLow = GD.HEATING_MANUAL_CONTROL_GROUP)
        keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_T1_TO_HEAT, textIdle = GD.KEY_GROUP_HEATING_MODE)
        
    # Set the Oil to T2 config bit and make Oil to T2 key text active.
    system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_OIL_BOILER_TO_TANK2, bitsLow = GD.BOILER_MANUAL_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_OIL_TO_T2, textIdle = GD.KEY_GROUP_BOILER_MODE)
    
   # Read the config bits and update the bands on all the manual option control keys. 
    keyData.SetControlBandStatus (GD.ALL_MANUAL_CONTROL_GROUP, GD.KEY_GROUP_MANUAL_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_MANUAL_MODE, GD.UPDATE_ALL)
   
    return 1
    
################################################################################
##
## Function: ProcessOilOffKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments: The Oil off key will set the oil boiler to off. The key is set active and the red band will be set on. The
## Oil to Heating, Oil to T1 and Oil to T2  keys will be set to their idle state. If oil to heating is active we will set it to idle
## and set T1 to heating. 
##
################################################################################

def ProcessOilOffKey (keyValue) :

    # Do not process if we are disabled.
    if GD.currentMode == GD.MODE_MANUAL_OPTIONS_DISABLED : return 1
    
    # If oil to heating is active we need to make it idle and set T1 to heating. Set T1 to heating key text active.
    # Note this test must be done first before we change any config bits.
    if (system.systemControl [GD.SYSTEM_MANUAL_OIL_BOILER_TO_HEATING].CheckIfBitHigh () == True) :
    
        system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_TANK_1_TO_HEATING, bitsLow = GD.HEATING_MANUAL_CONTROL_GROUP)
        keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_T1_TO_HEAT, textIdle = GD.KEY_GROUP_HEATING_MODE)
        
    # Set the Oil boiler off config bit and make boiler off key text active.
    system.UpdateSystemControlBits (bitsHigh = GD.SYSTEM_MANUAL_OIL_BOILER_OFF, bitsLow = GD.BOILER_MANUAL_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_OIL_OFF, textIdle = GD.KEY_GROUP_BOILER_MODE)
    
   # Read the config bits and update the bands on all the manual option control keys. 
    keyData.SetControlBandStatus (GD.ALL_MANUAL_CONTROL_GROUP, GD.KEY_GROUP_MANUAL_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_MANUAL_MODE, GD.UPDATE_ALL)
   
    return 1
    
################################################################################
##
## Function: ProcessManualOverrideKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The Manual Override key takes you to the screen where various manual overrides can be selected.
##
################################################################################

def ProcessManualOverrideKey (keyValue) :

    # Move to manual override select mode and display keyboard.
    GD.currentMode = GD.MODE_MANUAL_OVERRIDE_MAIN_MENU
    display.DisplayKeyboardImage (useMode = GD.currentMode)

    # Display new prompt to user.
    display.DisplayMiddleLeftInfoPrompt (GD.MANUAL_OVERRIDE_PROMPT)
   
    return 1
    
################################################################################
##
## Function: ProcessManualOverrideKeySubMenu (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:Selects the sub menu for each of the manual override keys: Immersion Control, W/B Control, Boiler Control etc.
##
################################################################################

def ProcessManualOverrideKeySubMenu (keyValue) :

    # Keep a list of parameters for each manual control key.
    parameters = {
    
       GD.KEYVALUE_IMMERSION_CONTROL : (GD.MODE_IMMERSION_MANUAL_CONTROL, GD.IMMERSION_MANUAL_OVERRIDE_GROUP,
                                                                  GD.KEY_GROUP_ALL_IMM, GD.IMMERSION_SELECT_PROMPT),
                                                                  
       GD.KEYVALUE_WOODBURNER_CONTROL : (GD.MODE_WOODBURNER_MANUAL_CONTROL, GD.WOODBURNER_MANUAL_OVERRIDE_GROUP,
                                                                      GD.KEY_GROUP_ALL_WB, GD.WB_PUMP_SELECT_PROMPT),
                                                                      
       GD.KEYVALUE_TANK_1_CONTROL : (GD.MODE_TANK_1_MANUAL_CONTROL, GD.TANK_1_MANUAL_OVERRIDE_GROUP,
                                                                      GD.KEY_GROUP_ALL_T1, GD.TANK_1_CONTROL_PROMPT),
                                                                      
       GD.KEYVALUE_TANK_2_CONTROL : (GD.MODE_TANK_2_MANUAL_CONTROL, GD.TANK_2_MANUAL_OVERRIDE_GROUP,
                                                                      GD.KEY_GROUP_ALL_T2, GD.TANK_2_CONTROL_PROMPT),
                                                                      
       GD.KEYVALUE_BOILER_CONTROL : (GD.MODE_BOILER_MANUAL_CONTROL, GD.BOILER_MANUAL_OVERRIDE_GROUP,
                                                                      GD.KEY_GROUP_ALL_BOILER, GD.BOILER_CONTROL_PROMPT),
                                                                      
       GD.KEYVALUE_HEATING_CONTROL : (GD.MODE_HEATING_MANUAL_CONTROL, GD.HEATING_MANUAL_OVERRIDE_GROUP,
                                                                      GD.KEY_GROUP_ALL_HEATING, GD.HEATING_CONTROL_PROMPT)
    }
        
    if keyValue in parameters :
    
        # Get parameters for this manual control select key.
        mode, control, keyGroup, prompt = parameters [keyValue]
        
        # The onkeys are the 1st half and the offkeys are the 2nd half of the keygroup list.
        onKeys = keyGroup [0:len(keyGroup)/2]
        offKeys = keyGroup [len(keyGroup)/2:len(keyGroup)]

         # Move to the new mode and display keyboard.
        GD.currentMode = mode
        display.DisplayKeyboardImage (useMode = GD.currentMode)

        # Set the control key bands according to the system configuration data bits.
        keyData.SetControlBandStatus (control, onKeys)
        keyData.SetControlBandStatus (control, offKeys, checkIfHigh = False)
        
        # Display the updated key images.
        display.UpdateSelectKeyImages (keyGroup, GD.UPDATE_ALL)
        
        # Prompt user for action.
        display.DisplayMiddleLeftInfoPrompt (prompt)
       
    return 1
   
################################################################################
##
## Function: ProcessManualOverrideOnOffKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments: Used to override a control. If the control is currently in the state required no action is taken. If the
## line is already in override and this is a request for the other state the override is cancelled.
## Key indications are as follows:
## If there is no overrride and the state is inactive the base key is displayed. 
## If there is no overrride and the state is active the green/red band1 is displayed. 
## If there is an overrride the key will flash alternate yellow band green/red band.
## Note: Manual control keys have a dedicated on or off function and so they will have either red or green band image as
## band 1. This is different to zone keys which have green band on band 1 and red band on band 2. 
################################################################################

def ProcessManualOverrideOnOffKey (keyValue) :

    # This is a lookup dictionary of tuples for parameters for the key we are processing. For each key we keep the following values:
    # (0) The keyvalue for the opposite key - if this is an on key this value would be the off key.
    # (1) The system control bit this key controls.
    # (2) The system control bit for the opposite control. This is none for for an on/off key as there is no opposite control bit.
    # (3) An index into a 2nd lookup table that holds values for the group this key is in.
    keyParameters = {
    
        # keyValue: (opposite key (0), system bit for this key (1), system bit for opposite key (2), index to group parameter (3)).
        # Immersion control.
        GD.KEYVALUE_IMM_1_ON :  (GD.KEYVALUE_IMM_1_OFF, GD.SYSTEM_IMM_1, GD.SYSTEM_NONE, 0),
        GD.KEYVALUE_IMM_2_ON :  (GD.KEYVALUE_IMM_2_OFF, GD.SYSTEM_IMM_2, GD.SYSTEM_NONE, 0),
        GD.KEYVALUE_IMM_3_ON :  (GD.KEYVALUE_IMM_3_OFF, GD.SYSTEM_IMM_3, GD.SYSTEM_NONE, 0),
        GD.KEYVALUE_IMM_4_ON :  (GD.KEYVALUE_IMM_4_OFF, GD.SYSTEM_IMM_4, GD.SYSTEM_NONE, 0),
        GD.KEYVALUE_IMM_1_OFF :  (GD.KEYVALUE_IMM_1_ON, GD.SYSTEM_IMM_1, GD.SYSTEM_NONE, 0),
        GD.KEYVALUE_IMM_2_OFF :  (GD.KEYVALUE_IMM_2_ON, GD.SYSTEM_IMM_2, GD.SYSTEM_NONE, 0),
        GD.KEYVALUE_IMM_3_OFF :  (GD.KEYVALUE_IMM_3_ON, GD.SYSTEM_IMM_3, GD.SYSTEM_NONE, 0),
        GD.KEYVALUE_IMM_4_OFF :  (GD.KEYVALUE_IMM_4_ON, GD.SYSTEM_IMM_4, GD.SYSTEM_NONE, 0),

        # Woodburner control.
        GD.KEYVALUE_WB_PUMP_1_ON :  (GD.KEYVALUE_WB_PUMP_1_OFF, GD.SYSTEM_WOODBURNER_PUMP_1, GD.SYSTEM_NONE, 1),
        GD.KEYVALUE_WB_PUMP_2_ON :  (GD.KEYVALUE_WB_PUMP_2_OFF, GD.SYSTEM_WOODBURNER_PUMP_2, GD.SYSTEM_NONE, 1),
        GD.KEYVALUE_WB_PUMP_1_OFF :  (GD.KEYVALUE_WB_PUMP_1_ON, GD.SYSTEM_WOODBURNER_PUMP_1, GD.SYSTEM_NONE, 1),
        GD.KEYVALUE_WB_PUMP_2_OFF :  (GD.KEYVALUE_WB_PUMP_2_ON, GD.SYSTEM_WOODBURNER_PUMP_2, GD.SYSTEM_NONE, 1),
    
        # Tank 1 control.
        GD.KEYVALUE_TANK_1_PUMP_ON :  (GD.KEYVALUE_TANK_1_PUMP_OFF, GD.SYSTEM_TANK_1_PUMP, GD.SYSTEM_NONE, 2),        
        GD.KEYVALUE_V1_EXT_TO_T1 :  (GD.KEYVALUE_V1_EXT_TO_HEATING, GD.SYSTEM_V1_EXT_TO_TANK_1, GD.SYSTEM_V1_EXT_TO_HEATING, 2),        
        GD.KEYVALUE_TANK_1_PUMP_OFF :  (GD.KEYVALUE_TANK_1_PUMP_ON, GD.SYSTEM_TANK_1_PUMP, GD.SYSTEM_NONE, 2),        
        GD.KEYVALUE_V1_EXT_TO_HEATING :  (GD.KEYVALUE_V1_EXT_TO_T1, GD.SYSTEM_V1_EXT_TO_TANK_1, GD.SYSTEM_V1_EXT_TO_HEATING, 2),
    
        # Tank 2 control.
        GD.KEYVALUE_TANK_2_PUMP_ON :  (GD.KEYVALUE_TANK_2_PUMP_OFF, GD.SYSTEM_TANK_2_PUMP, GD.SYSTEM_NONE, 3),        
        GD.KEYVALUE_V2_T2_TO_INT :  (GD.KEYVALUE_V2_T2_RECYCLE, GD.SYSTEM_EXT_TO_INT, GD.SYSTEM_NONE, 3),        
        GD.KEYVALUE_TANK_2_PUMP_OFF :  (GD.KEYVALUE_TANK_2_PUMP_ON, GD.SYSTEM_TANK_2_PUMP, GD.SYSTEM_NONE, 3),        
        GD.KEYVALUE_V2_T2_RECYCLE :  (GD.KEYVALUE_V2_T2_TO_INT, GD.SYSTEM_EXT_TO_INT, GD.SYSTEM_NONE, 3),
    
        # Boiler control.
        GD.KEYVALUE_BOILER_ON :  (GD.KEYVALUE_BOILER_OFF, GD.SYSTEM_BOILER_ON, GD.SYSTEM_NONE, 4),        
        GD.KEYVALUE_V3_BOILER_TO_INT :  (GD.KEYVALUE_V3_BOILER_TO_T2, GD.SYSTEM_V3_BOILER_TO_INT, GD.SYSTEM_NONE, 4),        
        GD.KEYVALUE_BOILER_OFF :  (GD.KEYVALUE_BOILER_ON, GD.SYSTEM_BOILER_ON, GD.SYSTEM_NONE, 4),        
        GD.KEYVALUE_V3_BOILER_TO_T2 :  (GD.KEYVALUE_V3_BOILER_TO_INT, GD.SYSTEM_V3_BOILER_TO_INT, GD.SYSTEM_NONE, 4),
    
        # Heating control.
        GD.KEYVALUE_RAD_PUMP_ON :  (GD.KEYVALUE_RAD_PUMP_OFF, GD.SYSTEM_RAD_PUMP, GD.SYSTEM_NONE, 5),        
        GD.KEYVALUE_UFH_PUMP_ON :  (GD.KEYVALUE_UFH_PUMP_OFF, GD.SYSTEM_UFH_PUMP, GD.SYSTEM_NONE, 5),        
        GD.KEYVALUE_RAD_PUMP_OFF :  (GD.KEYVALUE_RAD_PUMP_ON, GD.SYSTEM_RAD_PUMP, GD.SYSTEM_NONE, 5),        
        GD.KEYVALUE_UFH_PUMP_OFF :  (GD.KEYVALUE_UFH_PUMP_ON, GD.SYSTEM_UFH_PUMP, GD.SYSTEM_NONE, 5)    
    }
    
    # Lookup tuple of tuples for group parameters that a key is in. We keep the following values:
    # (0) The key group that this key is in.
    # (1) The control group that the control bit for this key is in.
    # (3) The control key in the keyboard that selected the current keyboard. This enables us to set the override band for this key.
    groupParameters = (
    
        # key group (0), control group (1), control key (2)
        (GD.KEY_GROUP_ALL_IMM, GD.IMMERSION_MANUAL_OVERRIDE_GROUP, GD.KEYVALUE_IMMERSION_CONTROL),
        (GD.KEY_GROUP_ALL_WB, GD.WOODBURNER_MANUAL_OVERRIDE_GROUP, GD.KEYVALUE_WOODBURNER_CONTROL),
        (GD.KEY_GROUP_ALL_T1, GD.TANK_1_MANUAL_OVERRIDE_GROUP, GD.KEYVALUE_TANK_1_CONTROL),
        (GD.KEY_GROUP_ALL_T2, GD.TANK_2_MANUAL_OVERRIDE_GROUP, GD.KEYVALUE_TANK_2_CONTROL),
        (GD.KEY_GROUP_ALL_BOILER, GD.BOILER_MANUAL_OVERRIDE_GROUP, GD.KEYVALUE_BOILER_CONTROL),
        (GD.KEY_GROUP_ALL_HEATING, GD.HEATING_MANUAL_OVERRIDE_GROUP, GD.KEYVALUE_HEATING_CONTROL)
    )
                            
    if keyValue in keyParameters :
    
        # Get the opposite key, control bit and group index for this key.
        oppositeKey, controlBit, oppositeControlBit, groupIndex = keyParameters [keyValue] [0:4]
        
        # Get all the keys, control bits and the menu control key for the group this key is in. 
        keyGroup, controlGroup, controlKey = groupParameters [groupIndex] [0:3]
        
        # The onkeys are the 1st half and the offkeys are the 2nd half of the keygroup list.
        onKeys = keyGroup [0:len(keyGroup)/2]
        offKeys = keyGroup [len(keyGroup)/2:len(keyGroup)]
        
        # Clear any active override indication on the opposite key.
        keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, oppositeKey)        
        
        # Are we doing an on or off operation?
        if keyValue in (onKeys) :
            # Attempt to set bit high. If bit is in override low this will cancel the override. result will be true if we do set bit override high.
            result = system.systemControl [controlBit].SetOutputOverrideBitHigh ()
        else :
            # Attempt to set bit low. If bit is in override high this will cancel the override. result will be true if we do set bit override low.
            result = system.systemControl [controlBit].SetOutputOverrideBitLow ()
            
        # If we have an opposite bit we need to set opposite level as bits are exclusive.
        if oppositeControlBit != GD.SYSTEM_NONE :
            if system.systemControl [controlBit].CheckIfBitHigh () == True :
                system.systemControl [oppositeControlBit].SetOutputBitLow ()
            else :
                system.systemControl [oppositeControlBit].SetOutputBitHigh ()
 
        # If we did a high or low operation make text active. An override cancel will return false.
        if result == True :
            keyData.UpdateSelectKeyGroupText (keyValue)
        
        # We will check if any override is active for this group. If it is we will set the control key for the group to flash (yellow band).
        keyData.SetKeyNoBand (controlKey)
        for controlBit in controlGroup :
            if system.systemControl [controlBit].CheckIfOverrideActive () == True :
                keyData.SetKeyBand1Flashing (controlKey)
                
        # Set the control key bands according to the system configuration data bits.
        keyData.SetControlBandStatus (controlGroup, onKeys)
        keyData.SetControlBandStatus (controlGroup, offKeys, False)
        
        # Display the updated key images.
        display.UpdateSelectKeyImages (keyGroup, GD.UPDATE_ALL)
           
    return 1
    
#################################################################################### Function: #### Parameters:#### Returns:#### Globals modified:#### Comments:##
################################################################################

#################################################################################### Function: #### Parameters:#### Returns:#### Globals modified:#### Comments:##
################################################################################

#################################################################################### Function: #### Parameters:#### Returns:#### Globals modified:#### Comments:##
################################################################################

   
