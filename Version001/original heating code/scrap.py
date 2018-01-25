#def CheckIfNoBand (keyValue) :
#    if keyValue == GD.KEYVALUE_NONE : return ''
#    return (keyImageLookup [keyValue] [BAND_1_STATUS_INDEX] == 0
#                and
#                keyImageLookup [keyValue] [BAND_2_STATUS_INDEX] == 0)
    
################################################################################
##
## Function: SetSelectKeyActiveWithBandOn (key, group = GD.KEYVALUE_NONE)
##
## Parameters: key - integer - the key to update
##                      group - integer or tuple - the key group the key is in. All keys in the group are set idle
##
## Returns:
##
## Globals modified:
##
## Comments: Sets the supplied key active with the band on. All keys in the group will first be set idle with no band.
##
################################################################################

#def SetSelectKeyActiveWithBandOn (keyValue, group = GD.KEYVALUE_NONE) :

    # Check if single or multiple keys in group (single = int, multiple = tuple).
#    if type (group) is int :
        #Turn int to tuple.
#        group = (group,)

    # Only process key if it is not indicating an on or off condition (no band).
#    if CheckIfNoBand (keyValue) == True :
        # Make key active and all keys in group idle.
#        UpdateSelectKeyGroupText (keyValue, group)
        
#        UpdateSelectKeyGroupBand (keyValue, GD.KEYVALUE_NONE, group)
        
        # Now update all the key images that have changed.           
#        display.UpdateSelectKeyImages (group, GD.UPDATE_CHANGED)



################################################################################
##
## Function: GetKeyImageSequenceOld (keyValue, image = -1)
##
## Parameters: keyValue - integer - key value of the sequence required
##                   image - integer - if an image value is supplied it will used instead of the offset lookup value.
##
## Returns: The sequence of bytes to send to the display module to show the required image (excluding checksum).
##
## Globals modified:
##
## Comments: Uses the 'current' status values to lookup the image offset. Normally used to get an image or the flash on image.
##
################################################################################

def GetKeyImageSequenceOld (keyValue, image = -1) :

    # Get base address.
    baseAddress = keyImageLookup [keyValue] [BASE_ADDRESS_INDEX]
    
    # If an image offset is supplied use instead of lookup value.
    offset = image if image >= 0 else keyImageLookup [keyValue] [OFFSET_INDEX]
    
    # If the offset is not valid it means do not display, so return nothing,
    if offset < 0 :
        return ''
        
    # We have an offset so calculate full offset from offset of image set + idle status + band1 status + band2 status.
    for index in range (CURRENT_TEXT_STATUS_INDEX, LAST_TEXT_STATUS_INDEX) :
        offset += keyImageLookup [keyValue] [index] 
        
    # Return sequence to caller (excluding checksum).
    return (chr (0x01) + chr (0x1B) + chr (baseAddress) + chr (0x00) + chr (offset))
    

################################################################################
##
## Function: GetKeyImageLastSequence (keyValue, image = -1)
##
## Parameters: keyValue - integer - key value of the sequence required
##                   image - integer - if an image value is supplied it will used instead of the offset lookup value.
##
## Returns: The sequence of bytes to send to the display module to show the required image (excluding checksum).
##
## Globals modified:
##
## Comments: Uses the 'last' status values to lookup the image offset. Normally used to get the flash off image.
##
################################################################################

def GetKeyImageLastSequence (keyValue, image = -1) :

    # Get base address.
    baseAddress = keyImageLookup [keyValue] [BASE_ADDRESS_INDEX]
    
    # If an image offset is supplied use instead of lookup value.
    offset = image if image >= 0 else keyImageLookup [keyValue] [OFFSET_INDEX]
    
    # If the offset is not valid it means do not display, so return nothing,
    if offset < 0 :
        return ''
        
    # We have an offset so calculate full offset from offset of image set + idle status + band1 status + band2 status.
    for index in range (LAST_TEXT_STATUS_INDEX, BAND_FLASHING_INDEX) :
        offset += keyImageLookup [keyValue] [index] 
        
    # Return sequence to caller (excluding checksum).
    return (chr (0x01) + chr (0x1B) + chr (baseAddress) + chr (0x00) + chr (offset))

#   waitingOld =  IOModule.inWaiting()
  #  if waitingOld :
   #     while True :
    #        time.sleep (.05)
    #        waitingNew =  IOModule.inWaiting()
    #        if  waitingOld ==  waitingNew :
    #            break
    #        waitingOld = waitingNew
    
        # Process data in buffer if there is something there.
    #    while IOModule.inWaiting() :
    #        keyboardBuffer = []

            # Get 1st byte so we can check if this is button message or ACK/NAK.
    #        keyboardBuffer.append (IOModule.read (1))
            
            # If it is an ACK or NAK set flag that we will pass back.
    #        if keyboardBuffer[0] in (chr(0x06), chr(0x15)) :
    #            ackNak = ord (keyboardBuffer[0])
            
    #        else :
   #             print 'ID: ', ord (keyboardBuffer[0])
                # Not an ACK or NAK so assume button message. Get remaining 5 bytes of message.
                # Change timeout while we are doing this - message may still be arriving.
                IOModule.timeout = 2
                keyboardBuffer.extend (IOModule.read (5))
                IOModule.timeout = 0
                
                # Did we get all the message?
                if len (keyboardBuffer) >= 6 :
                
                    # Turn the bytes to ints and calculate the checksum.
                    for messageIndex in range (6) :
                        messageByte = ord (keyboardBuffer[messageIndex])
                        keyboardBuffer[messageIndex] = messageByte
                        checksum ^= messageByte
                        #print hex (messageByte),

                    # If the checksum is OK and it is a button or keyboard message load the keycode for the button type.
                    # We keep this in a global as we may be looking for an ACK and need to hang on to it until we are
                    # called to check for  a message.
                    if checksum == 0 and keyboardBuffer[0] == 0x07 :              
                        # Work out button type?
                        if keyboardBuffer[1] == GD.KEYBOARD_MESSAGE :
                            # It is a keyboard message - save the key
                            savedMessageId = keyboardBuffer[4]
                        elif keyboardBuffer[1] == GD.WINBUTTON_MESSAGE :
                            # It is a Winbutton - we only have one at present on the blank waiting screen. Set a keycode for it
                             savedMessageId = GD.KEYCODE_WAKEUP 
                        elif keyboardBuffer[1] == GD.USERBUTTON_MESSAGE :
                            # It is a Userbutton - we only have one at present on the status screen. Set a keycode for it
                             savedMessageId = GD.KEYCODE_EXIT_STATUS

                    else :
                        # Bad checksum so send NAK to display module. TODO
                        print 'nak'
                        #IOModule.write (chr (0x15))

    # Arrive here with all data in buffer processed or no data found. 
    # Were we checking for an ACK?
    if buttonOrAck == GD.CHECK_FOR_ACK :
        # Pass the value we have back - It could be zero if we didn't find an ACK or NAK.
        keycode = ackNak
        
    else :
        # We were checking for a message. Pass back the value. This may be a value we picked up previously
        #while waiting for an ACK/NAK or it could be zero if no message is found. Save it while we clear the global.
        keycode = savedMessageId
        # Clear the global now we are passing the value back.
        savedMessageId = 0
        #print 'key'
    
    # Wait for any possible extra bytes (button bounce) to arrive then clear buffer ready for next keypress.
    #time.sleep (0.1)
    #keyboardBuffer = []
    #IOModule.flushInput ()

    # Pass keycode back to caller, it will be zero if we do not have a valid key message.
    return keycode

    ################################################################################
#
# Function:  ProcessUfhKey (zone)
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

def ProcessUfhKey (zone) :

    # It is the UFH key so switch to UFH keyboard image and say we are in UFH mode.
    display.DisplayKeyboardImage (GD.UFH_SELECT_KEYBOARD_IMAGE)
    GD.currentMode = GD.MODE_UFH_ZONE_SELECT

    #display.DisplayForm (GD.UFH_SELECT_FORM)
    
    # Get zone status and display it.
    zoneStatus = zones.UpdateZoneStatus (zone)
    display.DisplayZoneStatus (zone, zoneStatus)

    return 

################################################################################
#
# Function: ProcessRadKey (zone)
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

def ProcessRadKey (zone) :

    # It is the RAD key so switch to RAD keyboard image and say we are in RAD mode.
    display.DisplayKeyboardImage (GD.RAD_SELECT_KEYBOARD_IMAGE)
    GD.currentMode = GD.MODE_RAD_ZONE_SELECT

    #display.DisplayForm (GD.RAD_SELECT_FORM)
   
   # Get zone status and display it.
    zoneStatus = zones.UpdateZoneStatus (zone)
    display.DisplayZoneStatus (zone, zoneStatus)

    return 
  
  ################################################################################
#
# Function: ProcessShowStatusKey (zone)
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

def ProcessShowStatusKey (zone) :

    # Just display the status form. We will exit back to rad form when user touches screen.
    display.DisplayForm (GD.STATUS_FORM)

    return 

################################################################################
#
# Function: ProcessExitStatusKey (zone)
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

def ProcessExitStatusKey (zone) :

    # Re-display the rad select form.
    display.DisplayForm (GD.MAIN_SCREEN_FORM)
    display.DisplayZoneStatus (zone, zones.UpdateZoneStatus (zone))
    display.DisplayRadPumpStatus()
    display.DisplayUfhPumpStatus()

    return 
################################################################################
#
# Function: SetSystemSelectKeyTextActive (keyValue = -1)
#
# Parameters: keyValue - integer - the key value to set active, if no key value is supplied all keys are set inactive.
#
# Returns:
#
# Globals modified:
#
# Comments: First we set the 4 system select keys text (off, auto, manual and holiday) to idle. We do this whenever one of
# these keys is pressed prior to setting the active state for the key just pressed as these keys are mutually exclusive.
# We then set the supplied key to active with yellow text.
################################################################################

def SetSystemSelectKeyTextActive (keyValue = -1) :

    for key in (GD.KEYVALUE_SYSTEM_OFF, GD.KEYVALUE_AUTO_MODE, 
                     GD.KEYVALUE_MANUAL_MODE, GD.KEYVALUE_HOLIDAY_MODE) :

        keys.keyImageStatus [key].SetKeyIdleText ()
        
    if keyValue >= 0 :
        keys.keyImageStatus [keyValue].SetKeyActiveText ()

        ################################################################################
#
# Function: SetSystemSelectKeyOnBand (keyValue = -1)
#
# Parameters: keyValue - integer - the key value to set the on band, if no key value is supplied all keys are set to no bands.
#
# Returns:
#
# Globals modified:
#
# Comments: First we set the 4 system select key bands (off, auto, manual and holiday) to no band. We do this whenever
# one of these keys is pressed prior to setting the on band for the key just pressed as these keys are mutually exclusive.
# We then set the on band for the supplied key.
################################################################################

def SetSystemSelectKeyOnBand (keyValue = -1) :

    for key in (GD.KEYVALUE_SYSTEM_OFF, GD.KEYVALUE_AUTO_MODE, 
                     GD.KEYVALUE_MANUAL_MODE, GD.KEYVALUE_HOLIDAY_MODE) :

        keys.keyImageStatus [key].SetKeyNoBand ()
    
    if keyValue >= 0 :
        keys.keyImageStatus [keyValue].SetKeyGreenBand ()

################################################################################
#
# Function: SetSystemSelectKeyOffBand (keyValue = -1)
#
# Parameters: keyValue - integer - the key value to set the off band, if no key value is supplied all keys are set to no bands.
#
# Returns:
#
# Globals modified:
#
# Comments: First we set the 4 system select key bands (off, auto, manual and holiday) to no band. We do this whenever
# one of these keys is pressed prior to setting the on band for the key just pressed as these keys are mutually exclusive.
# We then set the off band for the supplied key.
################################################################################

def SetSystemSelectKeyOffBand (keyValue = -1) :

    for key in (GD.KEYVALUE_SYSTEM_OFF, GD.KEYVALUE_AUTO_MODE, 
                     GD.KEYVALUE_MANUAL_MODE, GD.KEYVALUE_HOLIDAY_MODE) :

        keys.keyImageStatus [key].SetKeyNoBand ()
    
    if keyValue >= 0 :
        keys.keyImageStatus [keyValue].SetKeyRedBand ()

                # Have we got a key to set no band?
        if bandNone != GD.KEYVALUE_NONE :
            keys.keyImageStatus [bandNone].SetKeyNoBand ()
    else :
        for key in (bandNone) :
            keys.keyImageStatus [key].SetKeyNoBand ()
                   
    # Check if single or multiple keys (single = int, multiple = tuple).
    if type (bandGreen) is int :
        # Have we got a key to set to green band?
        if bandGreen != GD.KEYVALUE_NONE :
            keys.keyImageStatus [bandGreen].SetKeyGreenBand ()
    else :
        for key in (bandGreen) :
            keys.keyImageStatus [key].SetKeyGreenBand ()
        
    # Check if single or multiple keys (single = int, multiple = tuple).
    if type (bandRed) is int :
        # Have we got a key to set red band?
        if bandRed != GD.KEYVALUE_NONE :
            keys.keyImageStatus [bandRed].SetKeyRedBand ()
    else :
        for key in (bandRed) :
            keys.keyImageStatus [key].SetKeyRedBand ()
                   

                   def DisplayKeyImage (keyCode,  keyImage = -1) :

    # Lookup table  to select the correct key image for the mode we are in and the button pressed. If an index is 50+ this flags
    # it is one of the double button images and we need to subtract 50 to get the actual index. We will also need to adjust
    # the image number for double buttons as it is not a direct match to the keycode.
    
                                                                          #                     User image index for button numbers
    imageLookup = {                                           # 0   1   2   3   4   5   6   7   8   9  10 11 12 13 14 15 16 17 18 19 20 21 22
        GD.MODE_RAD_WAITING_ZONE_SELECT:    (0,  1,  1,  1,  1,  0,  1,  1,  1,  1,  0,  1,  1,  1,  1,  0,  1,  1,  1,  1,  0,  0,  0),
        GD.MODE_UFH_WAITING_ZONE_SELECT:    (0,  2,  2,  2,  2,  0,  2,  2,  2,  2,  0,  2,  2,  2,  2,  0,  2,  2,  2,  2,  0,  0,  0),
        GD.MODE_RAD_ZONE_SELECT:                    (0,  1,  1,  1,  1,  2,  1,  1,  1,  1, -1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1,  0,  0),
        GD.MODE_UFH_ZONE_SELECT:                    (0,  2,  2,  2,  2,  2,  2,  2,  2,  2, -1,  2,  2,  2,  2, -1,  2,  2,  2,  2,  1,  0,  0),
        GD.MODE_PROG_TIME:                                 (0,13,13,13,13,  1,13,13,13,13,  1,13,13,13,13,  1,13,13,13, -1,  1,  0,  0),
        GD.MODE_PROG_ON_AT:                              (0,13,13,13,13,  1,13,13,13,13,  1,13,13,13,13,  1,13,13,13, -1,  1,  0,  0),
        GD.MODE_PROG_OFF_AT:                             (0,13,13,13,13,  1,13,13,13,13,  1,13,13,13,13,  1,13,13,13, -1,  1,  0,  0),
        GD.MODE_PROG_DAY:                                   (0,14,14,14,14,  1,14,14,14,14,  1,14,14,14,14,  2,14,14,14, -1,  1,  0,  0),
        GD.MODE_PROG_DAYS_ON:                          (0,14,14,14,14,  1,14,14,14,14,  1,14,14,14,14,  2,14,14,14,  -1, 1,  0,  0),
        GD.MODE_NONE:                                           (0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
        GD.MODE_RUN:                                             (0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0)
 #       GD.MODE_SYSTEM_SELECT:                          (0,51,51,51,51,  0,51,51,51,51,  0,51,51,51,51,  0,51,51,51,51,  0,  0,  0)
#        GD.MODE_MANUAL_OPTIONS:                       (0,53,53,53,53,  0,53,53,53,53,  0,53,53,53,53,  0,53,53,53,53,  0,  0,  0),
#        GD.MODE_AUTO_OPTIONS:                           (0,55,55,55,55,  0,55,55,55,55,  0,55,55,55,55,  0,55,55,55,55,  0,  0,  0),
 #       GD.MODE_SYSTEM_OPTIONS:                       (0,57,57,57,57,  0,57,57,57,57,  0,57,57,57,57,  0,57,57,57,57,  0,  0,  0),
#        GD.MODE_HOLIDAY_OPTIONS:                     (0,59,59,59,59,  0,59,59,59,59,  0,59,59,59,59,  0,59,59,59,59,  0,  0,  0)
   }
    
    # Lookup table to convert single button image codes to the double button codes.  There are 8 double button images
    # overlaying single button images 1&2, 3&4, 6&7, 8&9, 11&12, 13&14, 16&17, 18&19. E.g. button images 1 and 2 are
    # overlaid with double button image 21. When a user presses a double button image it will be detected by one or other
    # of the two single buttons it overlays and we will need to re-display the double button image.
    
    doubleButtonImageLookup = (0, 21, 21, 22, 22, 5, 23, 23, 24, 24, 10, 25, 25, 26, 26, 15, 27, 27, 28, 28, 20, 0, 0)
    
    # Get the image index. Use lookup if no keyImage supplied.
    imageIndex = imageLookup[GD.currentMode][keyCode] if keyImage < 0 else keyImage
    
    # Only display an image if index is valid (not -ve).
    if imageIndex >= 0 :
    
        # Check if we need to make correction for double buttons.
        if imageIndex >= 50 :
            imageIndex -= 50
            imageNumber = doubleButtonImageLookup [keyCode]
        else :
            # For single buttons imagenumber is keycode.
            imageNumber = keyCode
            
        # Build the image select message (excluding checksum).
        imageSelectMessage = chr(0x01) + chr(0x1B) + chr(imageNumber) + chr(0x00) + chr(imageIndex)
        # Send to the display module.
        WriteToDisplay (imageSelectMessage)
        
        print 'NUMBER',imageNumber,'INDEX', imageIndex
        
    else :
        imageSelectMessage = ''
    
    return imageSelectMessage

 #           if GD.currentMode  in range (GD.FIRST_SELECT_MODE, GD.LAST_SELECT_MODE+1) :
                # We are in a select mode. If over 20 seconds have elapsed since the last keypress we will revert to run mode.
                # This turns off the display backlight and selects a screen of a single button that will restore the display when it is
                # pressed. We will also clear the boost  flags so that they are back to the initial state for next time.
#                if time.time() > (lastKeypressTime + GD.KEYPRESS_WAIT_TIME) : 
#                    GD.currentMode = GD.MODE_RUN
#                    display.WriteToDisplay (GD.BACKLIGHT_OFF)
#                    display.DisplayForm (GD.BLANK_SCREEN_FORM)
#                    display.DisplayPressToStart ()
#                    display.WriteToDisplay (GD.BACKLIGHT_LOW)
                    
#                    GD.boostPresses = 0
                    # Start a zones check to update any changes to zones.
#                    checkZone = 0
                    

    # If we are in rad or ufh select mode return to waiting select mode.
    if GD.currentMode in (GD.MODE_RAD_ZONE_SELECT,  GD.MODE_UFH_ZONE_SELECT) :
            
        # Say we are back in waiting mode. Use correct select keyboard and prompt for rad or ufh.
        if zone < 14 :
            GD.currentMode = GD.MODE_RAD_WAITING_ZONE_SELECT
            display.DisplaySetString (GD.RAD_SELECT_PROMPT, GD.MAIN_INFO_FIELD)
        else  :
            GD.currentMode = GD.MODE_UFH_WAITING_ZONE_SELECT     
            display.DisplaySetString (GD.UFH_SELECT_PROMPT, GD.MAIN_INFO_FIELD)
            
        # Clear info 1 prompt.
        display.DisplayInfo1Prompt (GD.INFO_1_BLANKED)
    
    else :   
    keyConfig = (
    
        (# Row 1 Key 1 - mode: keyvalue, base address, offset.
         1,
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (1, 1, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (15, 1, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (1, 1, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (15, 1, 7)},
         {GD.MODE_PROG_TIME : (51, 1, 13)},
         {GD.MODE_PROG_ON_AT : (51, 1, 13)},
         {GD.MODE_PROG_OFF_AT : (51, 1, 13)},
         {GD.MODE_PROG_DAY : (60, 1, 14)},
         {GD.MODE_PROG_DAYS_ON : (60, 1, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_SYSTEM_OFF, 21,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_OFFPEAK_TIMES, 21,15)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_HEATING_SOURCES, 21,13)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_T1_TO_HEAT, 21,5)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B21, 21,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_1_ON, 21,9)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_PUMP_1_ON, 21,16)}
        ),
 
        (# Row 1 Key 2 - mode: keyvalue, base address, offset.
         2,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (2, 2, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (16, 2, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (2, 2, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (16, 2, 7)},
         {GD.MODE_PROG_TIME : (52, 2, 13)},
         {GD.MODE_PROG_ON_AT : (52, 2, 13)},
         {GD.MODE_PROG_OFF_AT : (52, 2, 13)},
         {GD.MODE_PROG_DAY : (61, 2, 14)},
         {GD.MODE_PROG_DAYS_ON : (61, 2, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_SYSTEM_OFF, 21,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_OFFPEAK_TIMES, 21,15)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_HEATING_SOURCES, 21,13)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_T1_TO_HEAT, 21,5)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B21, 21,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_1_ON, 21,9)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_PUMP_1_ON, 21,16)}
        ),
    
        (# Row 1 Key 3 - mode: keyvalue, base address, offset.
         3,
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (3, 3, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (17, 3, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (3, 3, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (17, 3, 7)},
         {GD.MODE_PROG_TIME : (53, 3, 13)},
         {GD.MODE_PROG_ON_AT : (53, 3, 13)},
         {GD.MODE_PROG_OFF_AT : (53, 3, 13)},
         {GD.MODE_PROG_DAY : (62, 3, 14)},
         {GD.MODE_PROG_DAYS_ON : (62, 3, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_SYSTEM_OPTIONS, 22,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B22, 22,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_NOT_USED_B22, 22,0)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_OIL_TO_T1, 22,2)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B22, 22,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_1_OFF, 22,6)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_PUMP_1_OFF, 22,10)}
        ),
 
        (# Row 1 Key 4 - mode: keyvalue, base address, offset.
         4,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (4, 4, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (18, 4, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (4, 4, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (18, 4, 7)},
         {GD.MODE_PROG_TIME : (GD.KEYVALUE_ON_AT, 4, 13)},
         {GD.MODE_PROG_ON_AT : (GD.KEYVALUE_ON_AT, 4, 13)},
         {GD.MODE_PROG_OFF_AT : (GD.KEYVALUE_ON_AT, 4, 13)},
         {GD.MODE_PROG_DAY : (GD.KEYVALUE_ON_AT, 4, 14)},
         {GD.MODE_PROG_DAYS_ON : (GD.KEYVALUE_ON_AT, 4, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_SYSTEM_OPTIONS, 22,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B22, 22,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_NOT_USED_B22, 22,0)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_OIL_TO_T1, 22,2)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B22, 22,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_1_OFF, 22,6)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_PUMP_1_OFF, 22,10)}
        ),
 
        (# Row 1 Key 5 - mode: keyvalue, base address, offset.
         5,        
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_RAD, 5,3)},
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (GD.KEYVALUE_RAD, 5,3)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (GD.KEYVALUE_RAD, 5,3)}
        ),
        
        (# Row 2 Key 6 - mode: keyvalue, base address, offset.
         6,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (5, 6, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (19, 6, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (5, 6, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (19, 6, 7)},
         {GD.MODE_PROG_TIME : (54, 6, 13)},
         {GD.MODE_PROG_ON_AT : (54, 6, 13)},
         {GD.MODE_PROG_OFF_AT : (54, 6, 13)},
         {GD.MODE_PROG_DAY : (63, 6, 14)},
         {GD.MODE_PROG_DAYS_ON : (63, 6, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_AUTO_MODE, 23,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_OFFPEAK_TIMES, 23,15)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_WINTER_PERIOD, 23,13)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_T2_TO_HEAT, 23,5)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B23, 23,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_2_ON, 23,9)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_PUMP_2_ON, 23,16)}
        ),
 
        (# Row 2 Key 7 - mode: keyvalue, base address, offset.
         7,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (6, 7, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (20, 7, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (6, 7, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (20, 7, 7)},
         {GD.MODE_PROG_TIME : (55, 7, 13)},
         {GD.MODE_PROG_ON_AT : (55, 7, 13)},
         {GD.MODE_PROG_OFF_AT : (55, 7, 13)},
         {GD.MODE_PROG_DAY : (64, 7, 14)},
         {GD.MODE_PROG_DAYS_ON : (64, 7, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_AUTO_MODE, 23,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_OFFPEAK_TIMES, 23,15)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_T1_SOURCES, 23,13)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_T2_TO_HEAT, 23,5)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B23, 23,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_2_ON, 23,9)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_PUMP_2_ON, 23,16)}
        ),
 
        (# Row 2 Key 8 - mode: keyvalue, base address, offset.
         8,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (7, 8, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (21, 8, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (7, 8, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (21, 8, 7)},
         {GD.MODE_PROG_TIME : (56, 8, 13)},
         {GD.MODE_PROG_ON_AT : (56, 8, 13)},
         {GD.MODE_PROG_OFF_AT : (56, 8, 13)},
         {GD.MODE_PROG_DAY : (67, 8, 14)},
         {GD.MODE_PROG_DAYS_ON : (67, 8, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_AUTO_OPTIONS, 24,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B24, 24,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_NOT_USED_B24, 24,0)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_OIL_TO_T2, 24,2)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B24, 24,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_2_OFF, 24,6)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_PUMP_2_OFF, 24,10)}
        ),
 
        (# Row 2 Key 9 - mode: keyvalue, base address, offset.
         9,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (8, 9, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (22, 9, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (8, 9, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (22, 9, 7)},
         {GD.MODE_PROG_TIME : (GD.KEYVALUE_OFF_AT, 9, 13)},
         {GD.MODE_PROG_ON_AT : (GD.KEYVALUE_OFF_AT, 9, 13)},
         {GD.MODE_PROG_OFF_AT : (GD.KEYVALUE_OFF_AT, 9, 13)},
         {GD.MODE_PROG_DAY : (GD.KEYVALUE_OFF_AT, 9, 14)},
         {GD.MODE_PROG_DAYS_ON : (GD.KEYVALUE_OFF_AT, 9, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_AUTO_OPTIONS, 24,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B24, 24,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_NOT_USED_B24, 24,0)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_OIL_TO_T2, 24,2)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B24, 24,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_2_OFF, 24,6)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_PUMP_2_OFF, 24,10)}
        ),
        
        (# Row 2 Key 10 - mode: keyvalue, base address, offset.
         10,        
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_UFH, 10,4)},
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (GD.KEYVALUE_UFH, 10,4)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (GD.KEYVALUE_UFH, 10,4)}
        ),
        
        (# Row 3 Key 11 - mode: keyvalue, base address, offset.
         11,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (14, 11, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (28, 11, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (14, 11, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (28, 11, 7)},
         {GD.MODE_PROG_TIME : (57, 11, 13)},
         {GD.MODE_PROG_ON_AT : (57, 11, 13)},
         {GD.MODE_PROG_OFF_AT : (57, 11, 13)},
         {GD.MODE_PROG_DAY : (65, 11, 14)},
         {GD.MODE_PROG_DAYS_ON : (65, 11, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_MANUAL_MODE, 25,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B25, 25,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_T2_SOURCES, 25,13)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_OIL_TO_HEAT, 25,5)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B25, 25,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_3_ON, 25,9)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_ALARM, 25,15)}
        ),
 
        (# Row 3 Key 12 - mode: keyvalue, base address, offset.
         12,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (9, 12, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (23, 12, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (9, 12, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (23, 12, 7)},
         {GD.MODE_PROG_TIME : (58, 12, 13)},
         {GD.MODE_PROG_ON_AT : (58, 12, 13)},
         {GD.MODE_PROG_OFF_AT : (58, 12, 13)},
         {GD.MODE_PROG_DAY : (66, 12, 14)},
         {GD.MODE_PROG_DAYS_ON : (66, 12, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_MANUAL_MODE, 25,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B25, 25,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_T2_SOURCES, 25,13)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_OIL_TO_HEAT, 25,5)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B25, 25,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_3_ON, 25,9)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_ALARM, 25,15)}
        ),
 
        (# Row 3 Key 13 - mode: keyvalue, base address, offset.
         13,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (10, 13, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (24, 13, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (10, 13, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (24, 13, 7)},
         {GD.MODE_PROG_TIME : (59, 13, 13)},
         {GD.MODE_PROG_ON_AT : (59, 13, 13)},
         {GD.MODE_PROG_OFF_AT : (59, 13, 13)},
         {GD.MODE_PROG_DAY : (68, 13, 14)},
         {GD.MODE_PROG_DAYS_ON : (68, 13, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_MANUAL_OPTIONS, 26,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B26, 26,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_NOT_USED_B26, 26,0)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_OIL_OFF, 26,2)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B26, 26,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_3_OFF, 26,9)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_NOT_USED_B26, 26,0)}
        ),
 
        (# Row 3 Key 14 - mode: keyvalue, base address, offset.
         14,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (11, 14, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (25, 14, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (11, 14, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (25, 14, 7)},
         {GD.MODE_PROG_TIME : (GD.KEYVALUE_DAY, 14, 13)},
         {GD.MODE_PROG_ON_AT : (GD.KEYVALUE_DAY, 14, 13)},
         {GD.MODE_PROG_OFF_AT : (GD.KEYVALUE_DAY, 14, 13)},
         {GD.MODE_PROG_DAY : (GD.KEYVALUE_DAY, 14, 14)},
         {GD.MODE_PROG_DAYS_ON : (GD.KEYVALUE_DAY, 14, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_MANUAL_OPTIONS, 26,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B26, 26,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_NOT_USED_B26, 26,0)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_OIL_OFF, 26,2)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B26, 26,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_3_OFF, 26,9)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_NOT_USED_B26, 26,0)}
        ),
        
        (# Row 3 Key 15 - mode: keyvalue, base address, offset.
         15,        
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_SYSTEM, 15,5)},
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (GD.KEYVALUE_SYSTEM, 15,5)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (GD.KEYVALUE_SYSTEM, 15,5)}
        ),
 
        (# Row 4 Key 16 - mode: keyvalue, base address, offset.
         16,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (0, 16, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (29, 16, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (0, 16, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (29, 16, 7)},
         {GD.MODE_PROG_TIME : (GD.KEYVALUE_CLEAR, 16, 13)},
         {GD.MODE_PROG_ON_AT : (GD.KEYVALUE_CLEAR, 16, 13)},
         {GD.MODE_PROG_OFF_AT : (GD.KEYVALUE_CLEAR, 16, 13)},
         {GD.MODE_PROG_DAY : (GD.KEYVALUE_CLEAR, 16, 14)},
         {GD.MODE_PROG_DAYS_ON : (GD.KEYVALUE_CLEAR, 16, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_HOLIDAY_MODE, 27,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B27, 27,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_BOILER_PRIORITY, 27,11)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_WOODBURNER_CONTROL, 27,9)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B27, 27,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_4_ON, 27,6)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_NOT_USED_B27, 27,0)}
        ),
 
        (# Row 4 Key 17 - mode: keyvalue, base address, offset.
         17,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (12, 17, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (26, 17, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (12, 17, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (26, 17, 7)},
         {GD.MODE_PROG_TIME : (50, 17, 13)},
         {GD.MODE_PROG_ON_AT : (50, 17, 13)},
         {GD.MODE_PROG_OFF_AT : (50, 17, 13)},
         {GD.MODE_PROG_DAY : (69, 17, 14)},
         {GD.MODE_PROG_DAYS_ON : (69, 17, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_HOLIDAY_MODE, 27,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B27, 27,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_BOILER_PRIORITY, 27,11)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_WOODBURNER_CONTROL, 27,9)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B27, 27,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_4_ON, 27,6)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_NOT_USED_B27, 27,0)}
        ),
 
        (# Row 4 Key 18 - mode: keyvalue, base address, offset.
         18,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (13, 18, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (27, 18, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (13, 18, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (27, 18, 7)},
         {GD.MODE_PROG_TIME : (GD.KEYVALUE_SAVE, 18, 13)},
         {GD.MODE_PROG_ON_AT : (GD.KEYVALUE_SAVE, 18, 13)},
         {GD.MODE_PROG_OFF_AT : (GD.KEYVALUE_SAVE, 18, 13)},
         {GD.MODE_PROG_DAY : (GD.KEYVALUE_SAVE, 18, 14)},
         {GD.MODE_PROG_DAYS_ON : (GD.KEYVALUE_SAVE, 18, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_HOLIDAY_OPTIONS, 28,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B28, 28,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_NOT_USED_B28, 28,0)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_IMMERSION_CONTROL, 28,2)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B28, 28,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_4_OFF, 28,3)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_NOT_USED_B28, 28,0)}
        ),
 
        (# Row 4 Key 19 - mode: keyvalue, base address, offset.
         19,        
         {GD.MODE_RAD_WAITING_ZONE_SELECT : (0, 19, 1)},
         {GD.MODE_UFH_WAITING_ZONE_SELECT : (30, 19, 7)},
         {GD.MODE_RAD_ZONE_SELECT : (0, 19, 1)},
         {GD.MODE_UFH_ZONE_SELECT : (30, 19, 7)},
         {GD.MODE_PROG_TIME : (GD.KEYVALUE_AUTO_MANUAL, 19, 13)},
         {GD.MODE_PROG_ON_AT : (GD.KEYVALUE_AUTO_MANUAL, 19, 13)},
         {GD.MODE_PROG_OFF_AT : (GD.KEYVALUE_AUTO_MANUAL, 19, 13)},
         {GD.MODE_PROG_DAY : (GD.KEYVALUE_ENABLE_DISABLE, 19, 14)},
         {GD.MODE_PROG_DAYS_ON : (GD.KEYVALUE_ENABLE_DISABLE, 19, 14)},
         # Double width keys.
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_HOLIDAY_OPTIONS, 28,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_NOT_USED_B28, 28,0)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_NOT_USED_B28, 28,0)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_IMMERSION_CONTROL, 28,2)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_NOT_USED_B28, 28,0)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMM_4_OFF, 28,3)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_NOT_USED_B28, 28,0)}
        ),
        
        (# Row 4 Key 20 - mode: keyvalue, base address, offset.
         20,        
         {GD.MODE_SYSTEM_SELECT : (GD.KEYVALUE_FINISHED, 20,2)},
         {GD.MODE_MANUAL_OPTIONS : (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)},
         {GD.MODE_AUTO_OPTIONS : (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)},
         {GD.MODE_SYSTEM_OPTIONS : (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)},
         {GD.MODE_HOLIDAY_OPTIONS : (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)},
         {GD.MODE_IMMERSION_CONTROL : (GD.KEYVALUE_IMMERSION_CONTROL_EXIT, 20,1)},
         {GD.MODE_WOODBURNER_CONTROL : (GD.KEYVALUE_WB_CONTROL_EXIT, 20,1)}
        )
    )

    
    
    
             
        {GD.MODE_RAD_ZONE_SELECT : 
            (
                (1, 1, 1),
                (2, 2, 1),
                (3, 3, 1),
                (4, 4, 1),
                (GD.KEYVALUE_PROGRAM, 5, 2),
                (5, 6, 1),
                (6, 7, 1),
                (7, 8, 1),
                (8, 9, 1),
                (GD.KEYVALUE_BOOST, 10, 0), # BOOST WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (14, 11, 1),
                (9, 12, 1),
                (10, 13, 1),
                (11, 14, 1),
                (GD.KEYVALUE_CAN_RES, 15, 0), # CAN/RES WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (0, 16, 1),
                (12, 17, 1),
                (13, 18, 1),
                (0, 19, 1),
                (GD.KEYVALUE_RAD_SELECT_EXIT, 20, 1)        
            )
        },
         
        {GD.MODE_UFH_ZONE_SELECT : 
            (
                (15, 1, 7),
                (16, 2, 7),
                (17, 3, 7),
                (18, 4, 7),
                (GD.KEYVALUE_PROGRAM, 5, 2),
                (19, 6, 7),
                (20, 7, 7),
                (21, 8, 7),
                (22, 9, 7),
                (GD.KEYVALUE_BOOST, 10, 0), # BOOST WORK  SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (28, 11, 7),
                (23, 12, 7),
                (24, 13, 7),
                (25, 14, 7),
                (GD.KEYVALUE_CAN_RES, 15, 0), # CAN/RES WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (29, 16, 7),
                (26, 17, 7),
                (27, 18, 7),
                (30, 19, 7),
                (GD.KEYVALUE_UFH_SELECT_EXIT, 20, 1)        
            )
        },
         
        {GD.MODE_PROG_TIME : 
            (
                (51, 1, 13),
                (52, 2, 13),
                (53, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV, 5, 1),
                (54, 6, 13),
                (55, 7, 13),
                (56, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT, 10, 1),
                (57, 11, 13),
                (58, 12, 13),
                (59, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (50, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, 0), # AUTO/MAN WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EXIT, 20, 1)        
            )
        },
         
        {GD.MODE_PROG_ON_AT : 
            (
                (51, 1, 13),
                (52, 2, 13),
                (53, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV, 5, 1),
                (54, 6, 13),
                (55, 7, 13),
                (56, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT, 10, 1),
                (57, 11, 13),
                (58, 12, 13),
                (59, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (50, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, 0), # AUTO/MAN WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            )
        },
         
        {GD.MODE_PROG_OFF_AT : 
            (
                (51, 1, 13),
                (52, 2, 13),
                (53, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV, 5, 1),
                (54, 6, 13),
                (55, 7, 13),
                (56, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT, 10, 1),
                (57, 11, 13),
                (58, 12, 13),
                (59, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (50, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, 0), # AUTO/MAN WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            )
        },
         
        {GD.MODE_PROG_DAY : 
            (
                (60, 1, 14),
                (61, 2, 14),
                (62, 3, 14),
                (GD.KEYVALUE_ON_AT, 4, 14),
                (GD.KEYVALUE_PREV, 5, 1),
                (63, 6, 14),
                (64, 7, 14),
                (67, 8, 14),
                (GD.KEYVALUE_OFF_AT, 9, 14),
                (GD.KEYVALUE_NEXT, 10, 1),
                (65, 11, 14),
                (66, 12, 14),
                (68, 13, 14),
                (GD.KEYVALUE_DAY, 14, 14),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 14),
                (69, 17, 14),
                (GD.KEYVALUE_SAVE, 18, 14),
                (GD.KEYVALUE_ENABLE_DISABLE, 19, 0), # ENB/DIS WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EXIT, 20, 1)        
            )
        },
         
        {GD.MODE_PROG_DAYS_ON : 
            (
                (60, 1, 14),
                (61, 2, 14),
                (62, 3, 14),
                (GD.KEYVALUE_ON_AT, 4, 14),
                (GD.KEYVALUE_PREV, 5, 1),
                (63, 6, 14),
                (64, 7, 14),
                (67, 8, 14),    
                (GD.KEYVALUE_OFF_AT, 9, 14),
                (GD.KEYVALUE_NEXT, 10, 1),
                (65, 11, 14),
                (66, 12, 14),
                (68, 13, 14),
                (GD.KEYVALUE_DAY, 14, 14),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 14),
                (69, 17, 14),
                (GD.KEYVALUE_SAVE, 18, 14),
                (GD.KEYVALUE_ENABLE_DISABLE, 19, 0), # ENB/DIS WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            )
        },
         
        {GD.MODE_SYSTEM_SELECT : 
            (
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22,1),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22,1),
                (GD.KEYVALUE_RAD, 5, 3),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_AUTO_OPTIONS, 24,1),
                (GD.KEYVALUE_AUTO_OPTIONS, 24,1),
                (GD.KEYVALUE_UFH, 10,4),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_MANUAL_OPTIONS, 26,1),
                (GD.KEYVALUE_MANUAL_OPTIONS, 26,1),
                (GD.KEYVALUE_SYSTEM, 15,5),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_HOLIDAY_OPTIONS, 28,1),
                (GD.KEYVALUE_HOLIDAY_OPTIONS, 28,1),
                (GD.KEYVALUE_FINISHED, 20,2)
            )
        },

        {GD.MODE_SYSTEM_OPTIONS : 
            (
                (GD.KEYVALUE_OFFPEAK_TIMES, 21,15),
                (GD.KEYVALUE_OFFPEAK_TIMES, 21,15),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                ##
                (GD.KEYVALUE_OFFPEAK_TIMES, 23,15),
                (GD.KEYVALUE_OFFPEAK_TIMES, 23,15),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                ##
                (GD.KEYVALUE_NOT_USED_B25, 25,0),
                (GD.KEYVALUE_NOT_USED_B25, 25,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                ##
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)
            )
        },

        {GD.MODE_AUTO_OPTIONS : 
            (
                (GD.KEYVALUE_HEATING_SOURCES, 21,13),
                (GD.KEYVALUE_HEATING_SOURCES, 21,13),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                ##
                (GD.KEYVALUE_WINTER_PERIOD, 23,13),
                (GD.KEYVALUE_T1_SOURCES, 23,13),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                ##
                (GD.KEYVALUE_T2_SOURCES, 25,13),
                (GD.KEYVALUE_T2_SOURCES, 25,13),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                ##
                (GD.KEYVALUE_BOILER_PRIORITY, 27,11),
                (GD.KEYVALUE_BOILER_PRIORITY, 27,11),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)
            )
        },

        {GD.MODE_MANUAL_OPTIONS : 
            (
                (GD.KEYVALUE_T1_TO_HEAT, 21,5),
                (GD.KEYVALUE_T1_TO_HEAT, 21,5),
                (GD.KEYVALUE_OIL_TO_T1, 22,2),
                (GD.KEYVALUE_OIL_TO_T1, 22,2),
                ##
                (GD.KEYVALUE_T2_TO_HEAT, 23,5),
                (GD.KEYVALUE_T2_TO_HEAT, 23,5),
                (GD.KEYVALUE_OIL_TO_T2, 24,2),
                (GD.KEYVALUE_OIL_TO_T2, 24,2),
                ##
                (GD.KEYVALUE_OIL_TO_HEAT, 25,5),
                (GD.KEYVALUE_OIL_TO_HEAT, 25,5),
                (GD.KEYVALUE_OIL_OFF, 26,2),
                (GD.KEYVALUE_OIL_OFF, 26,2),
                ##
                (GD.KEYVALUE_WOODBURNER_CONTROL, 27,9),
                (GD.KEYVALUE_WOODBURNER_CONTROL, 27,9),
                (GD.KEYVALUE_IMMERSION_CONTROL, 28,2),
                (GD.KEYVALUE_IMMERSION_CONTROL, 28,2),
                (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)
            )
        },

        {GD.MODE_HOLIDAY_OPTIONS : 
            (
                (GD.KEYVALUE_NOT_USED_B21, 21,0),
                (GD.KEYVALUE_NOT_USED_B21, 21,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                ##
                (GD.KEYVALUE_NOT_USED_B23, 23,0),
                (GD.KEYVALUE_NOT_USED_B23, 23,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                ##
                (GD.KEYVALUE_NOT_USED_B25, 25,0),
                (GD.KEYVALUE_NOT_USED_B25, 25,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                ##
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)
            )
        },

        {GD.MODE_IMMERSION_CONTROL : 
            (
                (GD.KEYVALUE_IMM_1_ON, 21,9),
                (GD.KEYVALUE_IMM_1_ON, 21,9),
                (GD.KEYVALUE_IMM_1_OFF, 22,6),
                (GD.KEYVALUE_IMM_1_OFF, 22,6),
                ##
                (GD.KEYVALUE_IMM_2_ON, 23,9),
                (GD.KEYVALUE_IMM_2_ON, 23,9),
                (GD.KEYVALUE_IMM_2_OFF, 24,6),
                (GD.KEYVALUE_IMM_2_OFF, 24,6),
                ##
                (GD.KEYVALUE_IMM_3_ON, 25,9),
                (GD.KEYVALUE_IMM_3_ON, 25,9),
                (GD.KEYVALUE_IMM_3_OFF, 26,9),
                (GD.KEYVALUE_IMM_3_OFF, 26,9),
                ##
                (GD.KEYVALUE_IMM_4_ON, 27,6),
                (GD.KEYVALUE_IMM_4_ON, 27,6),
                (GD.KEYVALUE_IMM_4_OFF, 28,3),
                (GD.KEYVALUE_IMM_4_OFF, 28,3),
                (GD.KEYVALUE_IMMERSION_CONTROL_EXIT, 20,1)
            )
        },

        {GD.MODE_WOODBURNER_CONTROL : 
            (
                (GD.KEYVALUE_WB_PUMP_1_ON, 21,16),
                (GD.KEYVALUE_WB_PUMP_1_ON, 21,16),
                (GD.KEYVALUE_WB_PUMP_1_OFF, 22,10),
                (GD.KEYVALUE_WB_PUMP_1_OFF, 22,10),
                ##
                (GD.KEYVALUE_WB_PUMP_2_ON, 23,16),
                (GD.KEYVALUE_WB_PUMP_2_ON, 23,16),
                (GD.KEYVALUE_WB_PUMP_2_OFF, 24,10),
                (GD.KEYVALUE_WB_PUMP_2_OFF, 24,10),
                ##
                (GD.KEYVALUE_WB_ALARM, 25,15),
                (GD.KEYVALUE_WB_ALARM, 25,15),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                ##
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_WB_CONTROL_EXIT, 20,1)
            )
        }
)

################################################################################
##
## Class: visiKey
##
##Methods:
##
## Comments: For each key we will keep it's image address and the offsets used to select the image when it is idle, on, off etc.
## We can then use these to generate the sequence to send to the display for the current key image.
##
################################################################################

class visiKey :

    def __init__ (self, keyNumber) :
    
        # The visi genie button number.
        self.keyNumber = keyNumber
        
        # Create dictionary for this key.
        self.keyData = {}
        
        # Flag to show if key text is idle or active. 0 = idle, 1 = active.
        self.textStatus = 0
        
        # Flag to show last idle status.
        self.textLastStatus = -1
        
        # Flag to show key band1 is on or off. 0 = band off, 2= band on. band1 and band2 are mutually exclusive.
        self.band1Status = 0
        
        # Flag to show last band1 status.
        self.band1LastStatus = -1
        
        # Flag to show key band2 is on or off. 0 = band off, 4= band on. band1 and band2 are mutually exclusive.
        self.band2Status = 0
        
        # Flag to show last band2 status.
        self.band2LastStatus = -1
        
    # Add a new entry for a mode for this key.
    def AddModeEntry (self, entry) :
        self.keyData.update (entry)

    # Get the sequence to send to the display for the current key image.
    def GetKeyImageSequence (self, mode) :
        # Calculate offset = offset of image set + idle status + band1 status + band2 status.
        self.imageOffset = self.keyData [mode][2] + self.textStatus + self.band1Status + self.band2Status
        # Return sequence to caller (excluding checksum).
        return (chr(0x01) + chr(0x1B) + chr(self.keyData [mode][1]) + chr(0x00) + chr(self.imageOffset))
        
    # If the image has changed set last status flags to new status and return the image sequence otherwise return nothing.
    def GetChangedKeyImageSequence (self, mode) :
        if self.textStatus != self.textLastStatus\
          or\
          self.band1Status != self.band1LastStatus\
          or\
          self.band2Status != self.band2LastStatus :
          
            self.textLastStatus = self.textStatus
            self.band1LastStatus = self.band1Status
            self.band2LastStatus = self.band2Status
            return self.GetKeyImageSequence (mode)
        else :
            return ''
            
    def GetKeyValue (self, mode):
        # Make sure this is a valid key / mode combination. If it isn't tell caller.
        if mode in self.keyData :
            return self.keyData [mode][0]
        else :
            return GD.KEYVALUE_NONE
    
    def SetDefaultKeyImage (self) :
        self.textStatus = 0
        self.band1Status = 0
        self.band2Status = 0
        return self.GetKeyImageSequence ()
        
    def SetKeyIdleText (self) :
        self.textStatus = 0
        return self.GetKeyImageSequence ()
        
    def SetKeyActiveText (self) :
        self.textStatus = 1
        return self.GetKeyImageSequence ()
        
    def SetKeyNoBand (self) :
        self.band1Status = 0
        self.band2Status = 0
        return self.GetKeyImageSequence ()
        
    def SetKeyBand1 (self) :
        self.band2Status = 0
        self.band1Status = 2
        return self.GetKeyImageSequence ()
        
    def SetKeyBand2 (self) :
        self.band1Status = 0
        self.band2Status = 4
        return self.GetKeyImageSequence ()
          

          
################################################################################
#
# Function: CalculateKeyValue (keyCode)
#
# Parameters: keyCode - integer - the value of the key (button) pressed from the display module
#
# Returns: keyValue - integer -  the value for the key for the current mode
#
# Globals modified:
#
# Comments: Takes the code of the key pressed and looks up the value to return depening on the mode we are in.
# Each mode has a dictionary entry which is a tuple. Each tuple has the values for the current function of each key (user button)
# on the display. User buttons 1 - 20 are the main keyboard, numbered top left to bottom right, counting left to right.
# The actual values in the tuple are chosen so that we can use them as indices, where possible. If they are not used as indices
# the value is purely arbirtrary and is normally used as a dictionary key to select a function to call for the key.
#
################################################################################

def  CalculateKeyValue (keyCode) :

 #   print 'Keycode :',keyCode, 'Current mode',GD.currentMode
    
    # Lookup table to get unique code for each key depending on which mode we are in. For double width keys there
    # are 2 entries for each key as the double button image covers 2 single buttons.
    keyLookup = {
        GD.MODE_RAD_WAITING_ZONE_SELECT :
            (0,1,2,3,4, GD.KEYVALUE_RAD,
             5,6,7,8, GD.KEYVALUE_UFH,
             14,9,10,11, GD.KEYVALUE_SYSTEM,
             0,12,13,0, GD.KEYVALUE_FINISHED, 0),
              
        GD.MODE_UFH_WAITING_ZONE_SELECT : 
            (0,15,16,17,18, GD.KEYVALUE_RAD,
             19,20,21,22, GD.KEYVALUE_UFH,
             28,23,24,25, GD.KEYVALUE_SYSTEM,
             29,26,27,30, GD.KEYVALUE_FINISHED, 0),
     
        GD.MODE_RAD_ZONE_SELECT :
            (0,1,2,3,4, GD.KEYVALUE_PROGRAM,
             5,6,7,8, GD.KEYVALUE_BOOST,
             14,9,10,11, GD.KEYVALUE_CAN_RES,
             0,12,13,0, GD.KEYVALUE_RAD_SELECT_EXIT, 0),
              
        GD.MODE_UFH_ZONE_SELECT : 
            (0,15,16,17,18,GD.KEYVALUE_PROGRAM,
             19,20,21,22,GD.KEYVALUE_BOOST,
             28,23,24,25,GD.KEYVALUE_CAN_RES,
             29,26,27,30, GD.KEYVALUE_UFH_SELECT_EXIT, 0),
     
        GD.MODE_PROG_TIME : 
            (0,51,52,53,GD.KEYVALUE_ON_AT,GD.KEYVALUE_PREV,
             54,55,56,GD.KEYVALUE_OFF_AT,GD.KEYVALUE_NEXT,
             57,58,59,GD.KEYVALUE_DAY,GD.KEYVALUE_NEW,
             GD.KEYVALUE_CLEAR,50,GD.KEYVALUE_SAVE,GD.KEYVALUE_AUTO_MANUAL,GD.KEYVALUE_EXIT, 0),

        GD.MODE_PROG_ON_AT : 
            (0,51,52,53,GD.KEYVALUE_ON_AT,GD.KEYVALUE_PREV,
             54,55,56,GD.KEYVALUE_OFF_AT,GD.KEYVALUE_NEXT,
             57,58,59,GD.KEYVALUE_DAY,GD.KEYVALUE_NEW,
             GD.KEYVALUE_CLEAR,50,GD.KEYVALUE_SAVE,GD.KEYVALUE_AUTO_MANUAL,GD.KEYVALUE_EDIT_EXIT, 0),

        GD.MODE_PROG_OFF_AT : 
            (0,51,52,53,GD.KEYVALUE_ON_AT,GD.KEYVALUE_PREV,
             54,55,56,GD.KEYVALUE_OFF_AT,GD.KEYVALUE_NEXT,
             57,58,59,GD.KEYVALUE_DAY,GD.KEYVALUE_NEW,
             GD.KEYVALUE_CLEAR,50,GD.KEYVALUE_SAVE,GD.KEYVALUE_AUTO_MANUAL, GD.KEYVALUE_EDIT_EXIT, 0),

        GD.MODE_PROG_DAY : 
            (0,60,61,62,GD.KEYVALUE_ON_AT,GD.KEYVALUE_PREV,
             63,64,67,GD.KEYVALUE_OFF_AT,GD.KEYVALUE_NEXT,
             65,66,68,GD.KEYVALUE_DAY,GD.KEYVALUE_NEW,
             GD.KEYVALUE_CLEAR,69,GD.KEYVALUE_SAVE,GD.KEYVALUE_ENABLE_DISABLE, GD.KEYVALUE_EXIT, 0),
                 
        GD.MODE_PROG_DAYS_ON : 
            (0,60,61,62, GD.KEYVALUE_ON_AT,GD.KEYVALUE_PREV,
             63,64,67, GD.KEYVALUE_OFF_AT,GD.KEYVALUE_NEXT,
             65,66,68, GD.KEYVALUE_DAY,GD.KEYVALUE_NEW,
             GD.KEYVALUE_CLEAR ,69, GD.KEYVALUE_SAVE, GD.KEYVALUE_ENABLE_DISABLE, GD.KEYVALUE_EDIT_EXIT, 0),

        GD.MODE_SYSTEM_SELECT :
            (
            # Unused button 0
            0, 
            # Row 1
            GD.KEYVALUE_SYSTEM_OFF, GD.KEYVALUE_SYSTEM_OFF,
                GD.KEYVALUE_SYSTEM_OPTIONS, GD.KEYVALUE_SYSTEM_OPTIONS, GD.KEYVALUE_RAD,
            # Row 2
            GD.KEYVALUE_AUTO_MODE, GD.KEYVALUE_AUTO_MODE,
                GD.KEYVALUE_AUTO_OPTIONS, GD.KEYVALUE_AUTO_OPTIONS, GD.KEYVALUE_UFH,
            # Row 3 
            GD.KEYVALUE_MANUAL_MODE, GD.KEYVALUE_MANUAL_MODE,
                GD.KEYVALUE_MANUAL_OPTIONS, GD.KEYVALUE_MANUAL_OPTIONS , GD.KEYVALUE_SYSTEM,
            # Row 4
            GD.KEYVALUE_HOLIDAY_MODE, GD.KEYVALUE_HOLIDAY_MODE,
                GD.KEYVALUE_HOLIDAY_OPTIONS, GD.KEYVALUE_HOLIDAY_OPTIONS,  GD.KEYVALUE_FINISHED,
            # Button 21
            0
            ),
            
        GD.MODE_MANUAL_OPTIONS :
            (
            # Unused button 0
            0, 
            # Row 1
            GD.KEYVALUE_T1_TO_HEAT, GD.KEYVALUE_T1_TO_HEAT,
                GD.KEYVALUE_OIL_TO_T1, GD.KEYVALUE_OIL_TO_T1, GD.KEYVALUE_NOT_USED,
            # Row 2
            GD.KEYVALUE_T2_TO_HEAT, GD.KEYVALUE_T2_TO_HEAT,
                GD.KEYVALUE_OIL_TO_T2, GD.KEYVALUE_OIL_TO_T2, GD.KEYVALUE_NOT_USED,
            # Row 3 
            GD.KEYVALUE_OIL_TO_HEAT, GD.KEYVALUE_OIL_TO_HEAT,
                GD.KEYVALUE_OIL_OFF, GD.KEYVALUE_OIL_OFF , GD.KEYVALUE_NOT_USED,
            # Row 4
            GD.KEYVALUE_WOODBURNER_CONTROL, GD.KEYVALUE_WOODBURNER_CONTROL,
                GD.KEYVALUE_IMMERSION_CONTROL, GD.KEYVALUE_IMMERSION_CONTROL, GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT,
            # Button 21
            0
            ),
            
        GD.MODE_AUTO_OPTIONS :
            (
            # Unused button 0
            0, 
            # Row 1
            GD.KEYVALUE_HEATING_SOURCES, GD.KEYVALUE_HEATING_SOURCES,
                GD.KEYVALUE_NOT_USED_B22, GD.KEYVALUE_NOT_USED_B22, GD.KEYVALUE_NOT_USED_B5,
            # Row 2
            GD.KEYVALUE_T1_SOURCES, GD.KEYVALUE_T1_SOURCES,
                GD.KEYVALUE_NOT_USED_B24, GD.KEYVALUE_NOT_USED_B24, GD.KEYVALUE_NOT_USED_B10,
            # Row 3 
            GD.KEYVALUE_T2_SOURCES, GD.KEYVALUE_T2_SOURCES,
                GD.KEYVALUE_NOT_USED_B26, GD.KEYVALUE_NOT_USED_B26, GD.KEYVALUE_NOT_USED_B15,
            # Row 4
            GD.KEYVALUE_BOILER_PRIORITY, GD.KEYVALUE_BOILER_PRIORITY,
                GD.KEYVALUE_NOT_USED_B28, GD.KEYVALUE_NOT_USED_B28, GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT,
            # Button 21
            0
            ),
            
        GD.MODE_SYSTEM_OPTIONS :
            (
            # Unused button 0
            0, 
            # Row 1
            GD.KEYVALUE_OFFPEAK_TIMES, GD.KEYVALUE_OFFPEAK_TIMES,
                GD.KEYVALUE_NOT_USED_B22, GD.KEYVALUE_NOT_USED_B22, GD.KEYVALUE_NOT_USED_B5,
            # Row 2
            GD.KEYVALUE_WINTER_PERIOD, GD.KEYVALUE_WINTER_PERIOD,
                GD.KEYVALUE_NOT_USED_B24, GD.KEYVALUE_NOT_USED_B24, GD.KEYVALUE_NOT_USED_B10,
            # Row 3 
            GD.KEYVALUE_NOT_USED_B25, GD.KEYVALUE_NOT_USED_B25,
                GD.KEYVALUE_NOT_USED_B26, GD.KEYVALUE_NOT_USED_B26, GD.KEYVALUE_NOT_USED_B15,
            # Row 4 
            GD.KEYVALUE_NOT_USED_B27, GD.KEYVALUE_NOT_USED_B27,
                GD.KEYVALUE_NOT_USED_B28, GD.KEYVALUE_NOT_USED_B28, GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT,
            # Button 21
            0
            ),
            
        GD.MODE_HOLIDAY_OPTIONS :
            (
            # Unused button 0
            0, 
            # Row 1
            GD.KEYVALUE_NOT_USED_B21, GD.KEYVALUE_NOT_USED_B21,
                GD.KEYVALUE_NOT_USED_B22, GD.KEYVALUE_NOT_USED_B22, GD.KEYVALUE_NOT_USED_B5,
            # Row 2
            GD.KEYVALUE_NOT_USED_B23, GD.KEYVALUE_NOT_USED_B23,
                GD.KEYVALUE_NOT_USED_B24, GD.KEYVALUE_NOT_USED_B24, GD.KEYVALUE_NOT_USED_B10,
            # Row 3 
            GD.KEYVALUE_NOT_USED_B25, GD.KEYVALUE_NOT_USED_B25,
                GD.KEYVALUE_NOT_USED_B26, GD.KEYVALUE_NOT_USED_B26, GD.KEYVALUE_NOT_USED_B15,
            # Row 4
            GD.KEYVALUE_NOT_USED_B27, GD.KEYVALUE_NOT_USED_B27,
                GD.KEYVALUE_NOT_USED_B28, GD.KEYVALUE_NOT_USED_B28, GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT,
            # Button 21
            0
            ),
            
        GD.MODE_IMMERSION_CONTROL :
            (
            # Unused button 0
            0, 
            # Row 1
            GD.KEYVALUE_IMM_1_ON, GD.KEYVALUE_IMM_1_ON,
                GD.KEYVALUE_IMM_1_OFF, GD.KEYVALUE_IMM_1_OFF, GD.KEYVALUE_NOT_USED_B5,
            # Row 2
            GD.KEYVALUE_IMM_2_ON, GD.KEYVALUE_IMM_2_ON,
                GD.KEYVALUE_IMM_2_OFF, GD.KEYVALUE_IMM_2_OFF, GD.KEYVALUE_NOT_USED_B10,
            # Row 3 
            GD.KEYVALUE_IMM_3_ON, GD.KEYVALUE_IMM_3_ON,
                GD.KEYVALUE_IMM_3_OFF, GD.KEYVALUE_IMM_3_OFF, GD.KEYVALUE_NOT_USED_B15,
            # Row 4 
            GD.KEYVALUE_IMM_4_ON, GD.KEYVALUE_IMM_4_ON,
                GD.KEYVALUE_IMM_4_OFF, GD.KEYVALUE_IMM_4_OFF, GD.KEYVALUE_IMMERSION_CONTROL_EXIT,
            # Button 21
            0
            ),
            
        GD.MODE_WOODBURNER_CONTROL :
            (
            # Unused button 0
            0, 
            # Row 1
            GD.KEYVALUE_WB_PUMP_1_ON,
            GD.KEYVALUE_WB_PUMP_1_ON,
            GD.KEYVALUE_WB_PUMP_1_OFF, 
            GD.KEYVALUE_WB_PUMP_1_OFF,
            GD.KEYVALUE_NOT_USED_B5,
            # Row 2
            GD.KEYVALUE_WB_PUMP_2_ON, GD.KEYVALUE_WB_PUMP_2_ON,
                GD.KEYVALUE_WB_PUMP_2_OFF, GD.KEYVALUE_WB_PUMP_2_OFF, GD.KEYVALUE_NOT_USED_B10,
            # Row 3 
            GD.KEYVALUE_NOT_USED_B25, GD.KEYVALUE_NOT_USED_B25,
                GD.KEYVALUE_NOT_USED_B26, GD.KEYVALUE_NOT_USED_B26, GD.KEYVALUE_NOT_USED_B15,
            # Row 4
            GD.KEYVALUE_NOT_USED_B27, GD.KEYVALUE_NOT_USED_B27,
                GD.KEYVALUE_NOT_USED_B28, GD.KEYVALUE_NOT_USED_B28, GD.KEYVALUE_WB_CONTROL_EXIT,
            # Button 21
            0
            )
            
    }
    # Check for special keys 1st. The 'Press to start' screen button and the system failure screen button.
    if keyCode in (GD.WAKEUP_BUTTON, GD.FAILED_BUTTON) :
        keyValue = GD.KEYVALUE_WAKEUP
    else :
        if GD.currentMode in keyLookup :
            keyValue = keyLookup [GD.currentMode][keyCode]
        else :
            keyValue = GD.KEYVALUE_NONE
    
    return keyValue
################################################################################
##
## Class: keyParameters
##
## Methods:
##
## Comments:
##
################################################################################

class keyParameters :

    def __init__ (self, dataConfig) :
        # Load the parameters for all the keys. These are the key values and image address.
        self.data = dataConfig
        
        # Initialise a dictionary to hold the idle and band status for each key value.
        keyImageStatus = {}
        # Scan through each mode.
        for mode in self.data :
            # Scan through each key value used in this mode and initialise status values. Duplicate key values will simply
            # overwrite the previous so that we only end up with 1 entry for each key value. For each keyvalue we hold a staus to
            # show if the key is idle/active and a status for each of 2 different band colours to show if they are on/off.
            # index 0 = idle/active (0/1), index 1 = band 1 on/off (0/2), index 2 = band 2 on/off (0/4).
            for index in range (0, 20) :
                keyImageStatus [self.data [mode] [index][0]] = [0, 0, 0]
                   
    # Get the key value for the supplied visi key. Each mode will have a different keyboard layout over the same 20 visi keys.
    def GetKeyValue (self, visiKey, mode) :
		# Check if key is normal keyboard key (1-20) and if it is adjust so that key 1 is index 0 etc for array lookup.
        if visiKey in range (1, 21) :
            visiKey -= 1
            keyValue = self.data [mode][visiKey][0]
        # If not a normal keyboard key is it one of the wakeup keys?
        elif visiKey in (GD.WAKEUP_BUTTON, GD.FAILED_BUTTON) :
            keyValue = GD.KEYVALUE_WAKEUP
        # Must be non valid key.
        else :
            keyValue = GD.KEYVALUE_NONE
    
        return keyValue

	
key = keyParameters (
    
        # mode.
        {GD.MODE_RAD_WAITING_ZONE_SELECT : 
            (# keyvalue, base address, offset.
                (1, 1, 1),                                               #1
                (2, 2, 1),                                               #2
                (3, 3, 1),                                               #3
                (4, 4, 1),                                               #4
                (GD.KEYVALUE_RAD, 5, 3),                     #5
                (5, 6, 1),                                               #6
                (6, 7, 1),                                               #7
                (7, 8, 1),                                               #8
                (8, 9, 1),                                               #9
                (GD.KEYVALUE_UFH, 10, 4),                   #10
                (14, 11, 1),                                           #11
                (9, 12, 1),                                             #12
                (10, 13, 1),                                           #13
                (11, 14, 1),                                           #14
                (GD.KEYVALUE_SYSTEM, 15, 5),             #15
                (0, 16, 1),                                             #16
                (12, 17, 1),                                           #17
                (13, 18, 1),                                           #18
                (0, 19, 1),                                             #19
                (GD.KEYVALUE_FINISHED, 20, 2)            #20
            ),
         
         GD.MODE_UFH_WAITING_ZONE_SELECT : 
            (
                (15, 1, 7),    
                (16, 2, 7),    
                (17, 3, 7),    
                (18, 4, 7),    
                (GD.KEYVALUE_RAD, 5, 3),              
                (19, 6, 7),    
                (20, 7, 7),    
                (21, 8, 7),    
                (22, 9, 7),    
                (GD.KEYVALUE_UFH, 10, 4),            
                (28, 11, 7),  
                (23, 12, 7),  
                (24, 13, 7),  
                (25, 14, 7),  
                (GD.KEYVALUE_SYSTEM, 15, 5),              
                (29, 16, 7),  
                (26, 17, 7),  
                (27, 18, 7),  
                (30, 19, 7),  
                (GD.KEYVALUE_FINISHED, 20, 2)              
            ),
        
         GD.MODE_RAD_ZONE_SELECT : 
            (
                (1, 1, 1),
                (2, 2, 1),
                (3, 3, 1),
                (4, 4, 1),
                (GD.KEYVALUE_PROGRAM, 5, 2),
                (5, 6, 1),
                (6, 7, 1),
                (7, 8, 1),
                (8, 9, 1),
                (GD.KEYVALUE_BOOST, 10, 0), # BOOST WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (14, 11, 1),
                (9, 12, 1),
                (10, 13, 1),
                (11, 14, 1),
                (GD.KEYVALUE_CAN_RES, 15, 0), # CAN/RES WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (0, 16, 1),
                (12, 17, 1),
                (13, 18, 1),
                (0, 19, 1),
                (GD.KEYVALUE_RAD_SELECT_EXIT, 20, 1)        
            ),
            
         GD.MODE_UFH_ZONE_SELECT : 
            (
                (15, 1, 7),
                (16, 2, 7),
                (17, 3, 7),
                (18, 4, 7),
                (GD.KEYVALUE_PROGRAM, 5, 2),
                (19, 6, 7),
                (20, 7, 7),
                (21, 8, 7),
                (22, 9, 7),
                (GD.KEYVALUE_BOOST, 10, 0), # BOOST WORK  SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (28, 11, 7),
                (23, 12, 7),
                (24, 13, 7),
                (25, 14, 7),
                (GD.KEYVALUE_CAN_RES, 15, 0), # CAN/RES WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (29, 16, 7),
                (26, 17, 7),
                (27, 18, 7),
                (30, 19, 7),
                (GD.KEYVALUE_UFH_SELECT_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_TIME : 
            (
                (51, 1, 13),
                (52, 2, 13),
                (53, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV, 5, 1),
                (54, 6, 13),
                (55, 7, 13),
                (56, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT, 10, 1),
                (57, 11, 13),
                (58, 12, 13),
                (59, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (50, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, 0), # AUTO/MAN WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_ON_AT : 
            (
                (51, 1, 13),
                (52, 2, 13),
                (53, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV, 5, 1),
                (54, 6, 13),
                (55, 7, 13),
                (56, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT, 10, 1),
                (57, 11, 13),
                (58, 12, 13),
                (59, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (50, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, 0), # AUTO/MAN WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_OFF_AT : 
            (
                (51, 1, 13),
                (52, 2, 13),
                (53, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV, 5, 1),
                (54, 6, 13),
                (55, 7, 13),
                (56, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT, 10, 1),
                (57, 11, 13),
                (58, 12, 13),
                (59, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (50, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, 0), # AUTO/MAN WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_DAY : 
            (
                (60, 1, 14),
                (61, 2, 14),
                (62, 3, 14),
                (GD.KEYVALUE_ON_AT, 4, 14),
                (GD.KEYVALUE_PREV, 5, 1),
                (63, 6, 14),
                (64, 7, 14),
                (67, 8, 14),
                (GD.KEYVALUE_OFF_AT, 9, 14),
                (GD.KEYVALUE_NEXT, 10, 1),
                (65, 11, 14),
                (66, 12, 14),
                (68, 13, 14),
                (GD.KEYVALUE_DAY, 14, 14),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 14),
                (69, 17, 14),
                (GD.KEYVALUE_SAVE, 18, 14),
                (GD.KEYVALUE_ENABLE_DISABLE, 19, 0), # ENB/DIS WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_DAYS_ON : 
            (
                (60, 1, 14),
                (61, 2, 14),
                (62, 3, 14),
                (GD.KEYVALUE_ON_AT, 4, 14),
                (GD.KEYVALUE_PREV, 5, 1),
                (63, 6, 14),
                (64, 7, 14),
                (67, 8, 14),    
                (GD.KEYVALUE_OFF_AT, 9, 14),
                (GD.KEYVALUE_NEXT, 10, 1),
                (65, 11, 14),
                (66, 12, 14),
                (68, 13, 14),
                (GD.KEYVALUE_DAY, 14, 14),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 14),
                (69, 17, 14),
                (GD.KEYVALUE_SAVE, 18, 14),
                (GD.KEYVALUE_ENABLE_DISABLE, 19, 0), # ENB/DIS WORK SHOW BLANK FOR NOW - COULD MAKE BASE 0 FOR NO OUTPUT
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            ),
         
         GD.MODE_SYSTEM_SELECT : 
            (
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22,1),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22,1),
                (GD.KEYVALUE_RAD, 5, 3),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_AUTO_OPTIONS, 24,1),
                (GD.KEYVALUE_AUTO_OPTIONS, 24,1),
                (GD.KEYVALUE_UFH, 10,4),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_MANUAL_OPTIONS, 26,1),
                (GD.KEYVALUE_MANUAL_OPTIONS, 26,1),
                (GD.KEYVALUE_SYSTEM, 15,5),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_HOLIDAY_OPTIONS, 28,1),
                (GD.KEYVALUE_HOLIDAY_OPTIONS, 28,1),
                (GD.KEYVALUE_FINISHED, 20,2)
            ),

         GD.MODE_SYSTEM_OPTIONS : 
            (
                (GD.KEYVALUE_OFFPEAK_TIMES, 21,15),
                (GD.KEYVALUE_OFFPEAK_TIMES, 21,15),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_OFFPEAK_TIMES, 23,15),
                (GD.KEYVALUE_OFFPEAK_TIMES, 23,15),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_NOT_USED_B25, 25,0),
                (GD.KEYVALUE_NOT_USED_B25, 25,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)
            ),

         GD.MODE_AUTO_OPTIONS : 
            (
                (GD.KEYVALUE_HEATING_SOURCES, 21,13),
                (GD.KEYVALUE_HEATING_SOURCES, 21,13),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_WINTER_PERIOD, 23,13),
                (GD.KEYVALUE_T1_SOURCES, 23,13),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_T2_SOURCES, 25,13),
                (GD.KEYVALUE_T2_SOURCES, 25,13),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_BOILER_PRIORITY, 27,11),
                (GD.KEYVALUE_BOILER_PRIORITY, 27,11),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)
            ),

         GD.MODE_MANUAL_OPTIONS : 
            (
                (GD.KEYVALUE_T1_TO_HEAT, 21,5),
                (GD.KEYVALUE_T1_TO_HEAT, 21,5),
                (GD.KEYVALUE_OIL_TO_T1, 22,2),
                (GD.KEYVALUE_OIL_TO_T1, 22,2),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_T2_TO_HEAT, 23,5),
                (GD.KEYVALUE_T2_TO_HEAT, 23,5),
                (GD.KEYVALUE_OIL_TO_T2, 24,2),
                (GD.KEYVALUE_OIL_TO_T2, 24,2),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_OIL_TO_HEAT, 25,5),
                (GD.KEYVALUE_OIL_TO_HEAT, 25,5),
                (GD.KEYVALUE_OIL_OFF, 26,2),
                (GD.KEYVALUE_OIL_OFF, 26,2),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_WOODBURNER_CONTROL, 27,9),
                (GD.KEYVALUE_WOODBURNER_CONTROL, 27,9),
                (GD.KEYVALUE_IMMERSION_CONTROL, 28,2),
                (GD.KEYVALUE_IMMERSION_CONTROL, 28,2),
                (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)
            ),

         GD.MODE_HOLIDAY_OPTIONS : 
            (
                (GD.KEYVALUE_NOT_USED_B21, 21,0),
                (GD.KEYVALUE_NOT_USED_B21, 21,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_NOT_USED_B23, 23,0),
                (GD.KEYVALUE_NOT_USED_B23, 23,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_NOT_USED_B25, 25,0),
                (GD.KEYVALUE_NOT_USED_B25, 25,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20,1)
            ),

         GD.MODE_IMMERSION_CONTROL : 
            (
                (GD.KEYVALUE_IMM_1_ON, 21,9),
                (GD.KEYVALUE_IMM_1_ON, 21,9),
                (GD.KEYVALUE_IMM_1_OFF, 22,6),
                (GD.KEYVALUE_IMM_1_OFF, 22,6),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_IMM_2_ON, 23,9),
                (GD.KEYVALUE_IMM_2_ON, 23,9),
                (GD.KEYVALUE_IMM_2_OFF, 24,6),
                (GD.KEYVALUE_IMM_2_OFF, 24,6),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_IMM_3_ON, 25,9),
                (GD.KEYVALUE_IMM_3_ON, 25,9),
                (GD.KEYVALUE_IMM_3_OFF, 26,9),
                (GD.KEYVALUE_IMM_3_OFF, 26,9),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_IMM_4_ON, 27,6),
                (GD.KEYVALUE_IMM_4_ON, 27,6),
                (GD.KEYVALUE_IMM_4_OFF, 28,3),
                (GD.KEYVALUE_IMM_4_OFF, 28,3),
                (GD.KEYVALUE_IMMERSION_CONTROL_EXIT, 20,1)
            ),

         GD.MODE_WOODBURNER_CONTROL : 
            (
                (GD.KEYVALUE_WB_PUMP_1_ON, 21, 16),
                (GD.KEYVALUE_WB_PUMP_1_ON, 21,16),
                (GD.KEYVALUE_WB_PUMP_1_OFF, 22,10),
                (GD.KEYVALUE_WB_PUMP_1_OFF, 22,10),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_WB_PUMP_2_ON, 23,16),
                (GD.KEYVALUE_WB_PUMP_2_ON, 23,16),
                (GD.KEYVALUE_WB_PUMP_2_OFF, 24,10),
                (GD.KEYVALUE_WB_PUMP_2_OFF, 24,10),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_WB_ALARM, 25,15),
                (GD.KEYVALUE_WB_ALARM, 25,15),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_WB_CONTROL_EXIT, 20,1)
            )
        }
)
    def GetKeyImageSequence (self) :
        # This returns the sequence to send to the display for the current key image (excluding checksum).
#        print 'Number',self.imageAddress,'Index', self.imageOffsets[self.textStatus][self.bandStatus]
        return (chr(0x01) + chr(0x1B) + chr(self.imageAddress) + chr(0x00) + chr(self.imageOffsets[self.textStatus][self.bandStatus]))
       
    def SetDefaultKeyImage (self) :
        self.textStatus = 0
        self.bandStatus = 0
        return self.GetKeyImageSequence ()
        
    def SetKeyIdleText (self) :
        self.textStatus = 0
        return self.GetKeyImageSequence ()
        
    def SetKeyActiveText (self) :
        self.textStatus = 1
        return self.GetKeyImageSequence ()
        
    def CheckIfNoBand (self) :
        return self.bandStatus == 0
        
    def SetKeyNoBand (self) :
        self.bandStatus = 0
        return self.GetKeyImageSequence ()
        
    def SetKeyGreenBand (self) :
        self.bandStatus = 1
        return self.GetKeyImageSequence ()
        
    def SetKeyRedBand (self) :
        self.bandStatus = 2
        return self.GetKeyImageSequence ()
        
    def GetChangedKeyImageSequence (self) :
        # If the image has changed set last status flags to new status and return the image sequence otherwise return nothing.
        if self.textStatus != self.textLastStatus or self.bandStatus != self.bandLastStatus :
            self.textLastStatus = self.textStatus
            self.bandLastStatus = self.bandStatus
            return self.GetKeyImageSequence ()
        else :
            return ''
################################################################################
#
# Function: InitialiseKeys () 
#
# Parameters:
#
# Returns:
#
# Globals modified:
#
# Comments: Create a dictionary for all the system keys and initialise to default values.
#
################################################################################

def InitialiseKeys () :

    global keyImageStatus

    # Define dictionary for key image objects
    keyImageStatus = {}

    # Startup configuration values for the image data for the keys. For each key value we keep the image base address and the
    # offsets for each of the key image states (e.g. idle, selected, on, off etc). Note that key value refers to the key value we 
    # have assigned to each visi-genie button for the particular keyboard we are displaying. Each button has a set of visi-genie 
    # images overlaying it. These images have a base address and then an offset to select a particular image.
    # Each key can have up to 6 images. These are idle (white text), selected (yellow text) plus each of these can have a
    # green outline (indicates on), red outline (indicates off) or no outline. Not all keys use every image type and any unused
    # images will be a blank key which is always the image at offset 0. 
    # Offsets are stored as a matrix as follows: idle & no band [0][0], idle & green band [0][1], idle & red band [0][2],
    # active & no band [1][0], active & green band [1][1], active & red band [1][2]
    
    keyImageStatusConfig = (
    
        # Images for system select keyboard.
        (GD.KEYVALUE_SYSTEM_OFF, 21, ((1,0,3), (2,0,4))),
        (GD.KEYVALUE_AUTO_MODE, 23, ((1,3,0), (2,4,0))),
        (GD.KEYVALUE_MANUAL_MODE, 25, ((1,3,0), (2,4,0))),
        (GD.KEYVALUE_HOLIDAY_MODE, 27, ((1,3,0), (2,4,0))),   
        (GD.KEYVALUE_SYSTEM_OPTIONS, 22, ((1,0,0), (0,0,0))),
        (GD.KEYVALUE_AUTO_OPTIONS, 24, ((1,0,0), (0,0,0))),
        (GD.KEYVALUE_MANUAL_OPTIONS, 26, ((1,0,0), (0,0,0))),
        (GD.KEYVALUE_HOLIDAY_OPTIONS, 28, ((1,0,0), (0,0,0))),

        # Images for auto options keyboard.
        (GD.KEYVALUE_HEATING_SOURCES, 21, ((13,0,0), (0,0,0))),    
        (GD.KEYVALUE_T1_SOURCES, 23, ((13,0,0), (0,0,0))),    
        (GD.KEYVALUE_T2_SOURCES, 25, ((13,0,0), (0,0,0))),    
        (GD.KEYVALUE_BOILER_PRIORITY, 27, ((11,0,0), (0,0,0))),    

        # Images for manual options keyboard.
        (GD.KEYVALUE_T1_TO_HEAT, 21, ((5,7,0), (6,8,0))),    
        (GD.KEYVALUE_T2_TO_HEAT, 23, ((5,7,0), (6,8,0))),    
        (GD.KEYVALUE_OIL_TO_HEAT, 25, ((5,7,0), (6,8,0))),    
        (GD.KEYVALUE_WOODBURNER_CONTROL, 27, ((9,0,0), (0,0,0))),   
        (GD.KEYVALUE_OIL_TO_T1, 22, ((2,4,0), (3,5,0))),    
        (GD.KEYVALUE_OIL_TO_T2, 24, ((2,4,0), (3,5,0))),    
        (GD.KEYVALUE_OIL_OFF, 26, ((2,0,4), (3,0,5))),    
        (GD.KEYVALUE_IMMERSION_CONTROL, 28, ((2,0,0), (0,0,0))) ,

        # Images for system options keyboard.
        (GD.KEYVALUE_OFFPEAK_TIMES, 21, ((15,0,0), (0,0,0))),    
        (GD.KEYVALUE_WINTER_PERIOD, 23, ((15,0,0), (0,0,0))),    
      
        # Images for immersion maual control keyboard.
        (GD.KEYVALUE_IMM_1_ON, 21, ((9,11,0), (10,12,0))),    
        (GD.KEYVALUE_IMM_2_ON, 23, ((9,11,0), (10,12,0))), 
        (GD.KEYVALUE_IMM_3_ON, 25, ((9,11,0), (10,12,0))), 
        (GD.KEYVALUE_IMM_4_ON, 27, ((5,7,0), (6,8,0))), 
        (GD.KEYVALUE_IMM_1_OFF, 22, ((6,0,8), (7,0,9))),    
        (GD.KEYVALUE_IMM_2_OFF, 24, ((6,0,8), (7,0,9))),    
        (GD.KEYVALUE_IMM_3_OFF, 26, ((6,0,8), (7,0,9))),    
        (GD.KEYVALUE_IMM_4_OFF, 28, ((3,0,5), (4,0,6))),    
        (GD.KEYVALUE_IMMERSION_CONTROL_EXIT, 20, ((1,0,0), (0,0,0))),   

        # Images for woodburner manual control keyboard.
        (GD.KEYVALUE_WB_PUMP_1_ON, 21, ((16,18,0), (17,19,0))),    
        (GD.KEYVALUE_WB_PUMP_2_ON, 23, ((16,18,0), (17,19,0))),    
        (GD.KEYVALUE_WB_PUMP_1_OFF, 22, ((10,0,12), (11,0,13))),    
        (GD.KEYVALUE_WB_PUMP_2_OFF, 24, ((10,0,12), (11,0,13))),    
        (GD.KEYVALUE_WB_ALARM, 25, ((15,0,0), (16,0,0))),    
        (GD.KEYVALUE_WB_CONTROL_EXIT, 20, ((1,0,0), (0,0,0))),    

        # Images for any unused buttons on a keyboard.
        (GD.KEYVALUE_NOT_USED_B5, 5, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B10, 10, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B15, 15, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B20, 20, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B21, 21, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B22, 22, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B23, 23, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B24, 24, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B25, 25, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B26, 26, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B27, 27, ((0,0,0), (0,0,0))),    
        (GD.KEYVALUE_NOT_USED_B28, 28, ((0,0,0), (0,0,0))),

        # Images for rad, ufh & system  keys.
        (GD.KEYVALUE_RAD, 5, ((3,0,0), (4,0,0))),
        (GD.KEYVALUE_UFH, 10, ((4,0,0), (5,0,0))),
        (GD.KEYVALUE_SYSTEM, 15, ((5,0,0), (6,0,0))),

        # Images for finished and exit keys on system keyboards.
        (GD.KEYVALUE_FINISHED, 20, ((2,0,0), (0,0,0))),
        (GD.KEYVALUE_SYSTEMS_OPTIONS_EXIT, 20, ((1,0,0), (0,0,0))),
        (GD.KEYVALUE_RAD_SELECT_EXIT, 20, ((1,0,0), (0,0,0))),
        (GD.KEYVALUE_UFH_SELECT_EXIT, 20, ((1,0,0), (0,0,0))),
        (GD.KEYVALUE_EDIT_EXIT, 20, ((1,0,0), (0,0,0)))

    )
 
    # Load dictionary with keyInfo objects.
    for key, address, offsets in keyImageStatusConfig :
        keyImageStatus [key] = keyInfo (address, offsets)
        
################################################################################
#
# Class: keyInfo
#
# Methods:
#
# Comments: For each key we will keep it's image address and the offsets used to select the image when it is idle, on, off etc.
# We can then use these to generate the sequence to send to the display for the current key image.
#
################################################################################

class keyInfo :

    def __init__ (self, address, offsets) :
        # Base address for the images for this key.
        self.imageAddress = address
        # Matrix of 6 offsets for the various key images - see below for image descriptions.
        self.imageOffsets =  offsets
        # Flag to show if key text is idle (white) = 0, or selected (yellow) = 1.
        self.textStatus = 0
        # Flag to show last idle status.
        self.textLastStatus = -1
        # Flag to show key band colour: key colour = 0, 1 = green band,  2 = red band.
        self.bandStatus = 0
        # Flag to show last band status.
        self.bandLastStatus = -1
        
################################################################################
#
# Function: DisplayKeyImage (keyCode, keyImage = -1) 
#
# Parameters: keyCode - integer - this selects the set of images to use for each button.
#                     keyImage - integer - a non -ve value supplied will be used in place of the lookup value.
#
# Returns: imageSelectMessage - string- the message we sent to display the key
#
# Globals modified:
#
# Comments: Displays the required key image. Each key has a set of pre-programmed images. These match the keys
# displayed when a keyboard image is displayed. We have to re-display a key after it is pressed as the image of the key
# is lost when it is pressed as it is replaced by the key's up/down image. If only keyCode is supplied the current mode is used
# with keyCode to lookup the image to use. If a keyImage value is supplied this will replace the lookup value in order that
# a specific image can be selected. An index value of -1 is used to disable writing an image. We do this for keys where the
# actual key image depends on a status value (e.g. boost status) and we will display the image elsewhere in the code.
#
################################################################################

def DisplayKeyImage (keyCode,  keyImage = -1) :

    # Lookup table  to select the correct key image for the mode we are in and the button pressed.
    
                                                                          #                     User image index for button numbers
    imageLookup = {                                           # 0   1   2   3   4   5   6   7   8   9  10 11 12 13 14 15 16 17 18 19 20 21 22
        GD.MODE_RAD_WAITING_ZONE_SELECT:    (0,  1,  1,  1,  1,  0,  1,  1,  1,  1,  0,  1,  1,  1,  1,  0,  1,  1,  1,  1,  0,  0,  0),
        GD.MODE_UFH_WAITING_ZONE_SELECT:    (0,  2,  2,  2,  2,  0,  2,  2,  2,  2,  0,  2,  2,  2,  2,  0,  2,  2,  2,  2,  0,  0,  0),
        GD.MODE_RAD_ZONE_SELECT:                    (0,  1,  1,  1,  1,  2,  1,  1,  1,  1, -1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1,  0,  0),
        GD.MODE_UFH_ZONE_SELECT:                    (0,  2,  2,  2,  2,  2,  2,  2,  2,  2, -1,  2,  2,  2,  2, -1,  2,  2,  2,  2,  1,  0,  0),
        GD.MODE_PROG_TIME:                                 (0,13,13,13,13,  1,13,13,13,13,  1,13,13,13,13,  1,13,13,13, -1,  1,  0,  0),
        GD.MODE_PROG_ON_AT:                              (0,13,13,13,13,  1,13,13,13,13,  1,13,13,13,13,  1,13,13,13, -1,  1,  0,  0),
        GD.MODE_PROG_OFF_AT:                             (0,13,13,13,13,  1,13,13,13,13,  1,13,13,13,13,  1,13,13,13, -1,  1,  0,  0),
        GD.MODE_PROG_DAY:                                   (0,14,14,14,14,  1,14,14,14,14,  1,14,14,14,14,  2,14,14,14, -1,  1,  0,  0),
        GD.MODE_PROG_DAYS_ON:                          (0,14,14,14,14,  1,14,14,14,14,  1,14,14,14,14,  2,14,14,14,  -1, 1,  0,  0),
        GD.MODE_NONE:                                           (0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
        GD.MODE_RUN:                                             (0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0)
   }
    
    # Get the image index. Use lookup if no keyImage supplied.
    imageIndex = imageLookup[GD.currentMode][keyCode] if keyImage < 0 else keyImage
    
    # Only display an image if index is valid (not -ve).
    if imageIndex >= 0 :
    
        # Build the image select message (excluding checksum) and send to display module.
        imageSelectMessage = chr(0x01) + chr(0x1B) + chr(keyCode) + chr(0x00) + chr(imageIndex)
        WriteToDisplay (imageSelectMessage)
        
        print 'NUMBER',keyCode,'INDEX', imageIndex
        
    else :
        imageSelectMessage = ''
    
    return imageSelectMessage

            
    def GetZoneSelectCurrentImage (self) :
        return  self.keyStatus[self.zoneCode][3]
        
    def GetKeyOffStatus (self) :
        return  self.keyStatus[self.zoneCode][2]
        
    def GetKeyOnStatus (self) :
        return  self.keyStatus[self.zoneCode][1]
        
    def UpdateKeyStatus (self) :
        # Are we on rad or ufh?
        if self.zoneCode < 14 :
            # On rad. 
            offIndex = onIndex = 1
        else :
            # On ufh.
            offIndex = onIndex = 2
        # Are we selected?
        if self.keyStatus [self.zoneCode][0] >= 0 :
            # Move to selected image.
            offIndex += 2
            onIndex += 2
            
        if self.CheckIfZoneStatusChanged () == True :
            if self.CheckIfZoneOnRequested () == True :
                onIndex += 4
            else :
                onIndex += 8
        elif self.CheckIfZoneOn () == True :
                offIndex += 4
                onIndex += 4

        self.keyStatus[self.zoneCode][1:3] = offIndex, onIndex
        
    # Changed keyboard so clear zone select saved key images
    zones.zoneData [0].SetZoneSelectCurrentImage (-1)

    def SetZoneSelectCurrentImage (self, currentImage) :
        # We keep the currently displayed select key image. This enables us to check if we can avoid resending an image so
        # that we can minimise serial data sent to the display. Setting currentImage to -ve will clear all the images. We will
        # need to do this if we change keyboards so that all the keys are refreshed when we return to a select keyboard.
        if currentImage >= 0 :
            self.keyStatus [self.zoneCode][3] = currentImage
        else :
            for zone in range (30) :
                self.keyStatus [zone][3] = -1

    def SetZoneSelectStatus (self, selectStatus) :
        # If selectStatus is >= 0 the zone is the currently selected one. As only 1 zone can be selected we will de-select
        # any existing selected zone. If selectStatus is -1 the zone is de-selected.
        # Clear any selected zone first.
        for zone in range (30) :
            if self.keyStatus [zone][0] >= 0 :
                self.keyStatus [zone][0] = -1
                self.keyStatus [zone][1] -=2
                self.keyStatus [zone][2] -=2
        # Set this zone to required status.
        self.keyStatus [self.zoneCode][0] = selectStatus
 ##       self.UpdateKeyStatus ()
        
    # We will keep the key status for each zone here. The key status holds the index for the images that we display for the
    # different states (normal, selected, on, off etc).  The index values must match the image order as defined in visi-genie.
    # When a zone is on we show a solid green band. When a zone is off we show a normal key. When a zone is
    # changing, off to on or on to off, we flash the green or red band. If a zone is selected we change to yellow text. So that
    # we can do the flash we keep an index for both flash states. A constant indication will have both indices the same.
    # The index values for each image are as follows:
    # 0 - blank key
    # 1 - rad normal turned off - grey text
    # 2 - ufh normal turned off - orange text
    # 3 - rad selected - yellow text
    # 4 - ufh selected - yellow text
    # 5 - rad on or turning on - grey text and green band or green band flashing
    # 6 - ufh on or turning on - orange text and green band or green band flashing
    # 7 - rad selected and on or turning on - yellow text and green band or green band flashing
    # 8 - ufh selected and on or turning on - yellow text and green band or green band flashing
    # 9 - rad turning off - grey text and red band flashing
    # 10 - ufh turning off - orange text and red band flashing
    # 11 - rad selected and turning off - yellow text and red band flashing
    # 12 - ufh selected and turning off - yellow text and red band flashing
   
    # Define a 4 x 30  list. Locations 0-13 are for the rad select keys and 14-29 are for the ufh select keys. 
    # List entry 0 is the zone selected flag, List  entry1 is the off flash image, List entry 2 is the on flash image, List entry 3 is the  
    # last image sent - we keep this so that we can check if we have all ready sent the image to avoid sending it again to minimise
    # the amount of serial data that we send to the display.
    keyStatus = [[0,0,0,0] for i in range(30)]
    
        # Load selected flag and index for a normal key image (both images the same). Adjust index for rad or ufh.
        self.keyStatus[self.zoneCode][0:4] = [-1,1,1,-1] if self.zoneCode < 14 else [-1,2,2,-1]
        

   

    else :
    
        if keyValue == GD.KEYVALUE_IMM_1_ON :  
            # Clear any active text on off key.
            keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, GD.KEYVALUE_IMM_1_OFF)        
            # Attempt to set bit high. If we do make key text active.
            if system.systemControl [GD.SYSTEM_IMM_1].SetOverrideBitHigh () == True :
                keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_IMM_1_ON)

        elif keyValue == GD.KEYVALUE_IMM_1_OFF : 
            # Clear any active text on on key.
            keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, GD.KEYVALUE_IMM_1_ON)    
             # Attempt to set bit low. If we do make key text active.
            if system.systemControl [GD.SYSTEM_IMM_1].SetOverrideBitLow () == True :       
                keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_IMM_1_OFF)
                
        elif keyValue == GD.KEYVALUE_IMM_2_ON :
            # Clear any active text on off key.
            keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, GD.KEYVALUE_IMM_2_OFF)       
            # Attempt to set bit high. If we do make key text active.
            if system.systemControl [GD.SYSTEM_IMM_2].SetOverrideBitHigh () == True :
                keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_IMM_2_ON)
                
        elif keyValue == GD.KEYVALUE_IMM_2_OFF :
            # Clear any active text on on key.
            keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, GD.KEYVALUE_IMM_2_ON)    
             # Attempt to set bit low. If we do make key text active.
            if system.systemControl [GD.SYSTEM_IMM_2].SetOverrideBitLow () == True :       
                keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_IMM_2_OFF)
                
        # At present imm3 and imm4 work together so we will operate both as a pair.
        elif keyValue == GD.KEYVALUE_IMM_3_ON :
            # Clear any active text on off key.
            keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, GD.KEYVALUE_IMM_3_OFF)       
            # Attempt to set bit high. If we do make key text active.
            if system.systemControl [GD.SYSTEM_IMM_3].SetOverrideBitHigh () == True :
                keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_IMM_3_ON)

        elif keyValue == GD.KEYVALUE_IMM_3_OFF :
            # Clear any active text on on key.
            keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, GD.KEYVALUE_IMM_3_ON)   
             # Attempt to set bit low. If we do make key text active.
            if system.systemControl [GD.SYSTEM_IMM_3].SetOverrideBitLow () == True :       
                keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_IMM_3_OFF)
                
        # At present imm3 and imm4 work together so we will operate both as a pair.
        elif keyValue == GD.KEYVALUE_IMM_4_ON :
            # Clear any active text on off key.
            keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, GD.KEYVALUE_IMM_4_OFF)       
            # Attempt to set bit high. If we do make key text active.
            if system.systemControl [GD.SYSTEM_IMM_4].SetOverrideBitHigh () == True :
                keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_IMM_4_ON)

        elif keyValue == GD.KEYVALUE_IMM_4_OFF :
            # Clear any active text on on key.
            keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, GD.KEYVALUE_IMM_4_ON)   
             # Attempt to set bit low. If we do make key text active.
            if system.systemControl [GD.SYSTEM_IMM_4].SetOverrideBitLow () == True :       
                keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_IMM_4_OFF)
                
                # If we are in a mode where the select keys are active display any highlighting.
                if GD.currentMode in (GD.MODE_RAD_WAITING_ZONE_SELECT, GD.MODE_RAD_ZONE_SELECT,
                                                  GD.MODE_UFH_WAITING_ZONE_SELECT, GD.MODE_UFH_ZONE_SELECT,
                                                  GD.MODE_IMMERSION_CONTROL) :
                    pass
################################################################################
##
## Function: ProcessImmersionControlKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The Immersion Control key takes you to the screen where the immersions can be manually controlled.
##
################################################################################

def ProcessImmersionControlKey (keyValue) :

    # Move to immersion control select mode and display keyboard.
    GD.currentMode = GD.MODE_IMMERSION_MANUAL_CONTROL
    display.DisplayKeyboardImage (useMode = GD.currentMode)

    # Set the immersion control key bands according to the system configuration data bits.
    keyData.SetSystemConfigBandStatus (GD.IMMERSION_CONTROL_GROUP, GD.KEY_GROUP_IMM_ON, GD.KEY_GROUP_IMM_OFF)
    
    # Display the updated key images.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_ALL_IMM, GD.UPDATE_ALL)
    
    # Prompt user for action.
    display.DisplaySetString (GD.IMMERSION_SELECT_PROMPT, GD.MAIN_INFO_FIELD)
   
    return 1
        
################################################################################
##
## Function: ProcessWoodburnerControlKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The Woodburner Control key takes you to the screen where the W/B pumps can be manually controlled.
##
################################################################################

def ProcessWoodburnerControlKey (keyValue) :

    # Move to woodburner control select mode and display keyboard.
    GD.currentMode = GD.MODE_WOODBURNER_MANUAL_CONTROL
    display.DisplayKeyboardImage (useMode = GD.currentMode)

    # Set the woodburner control key bands according to the system configuration data bits.
    keyData.SetSystemConfigBandStatus (GD.WOODBURNER_CONTROL_GROUP, GD.KEY_GROUP_WB_ON, GD.KEY_GROUP_WB_OFF)
    
    # Display the updated key images.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_ALL_WB, GD.UPDATE_ALL)
    
    # Prompt user for action.
    display.DisplaySetString (GD.WB_PUMP_SELECT_PROMPT, GD.MAIN_INFO_FIELD)
   
    return 1
    ################################################################################
##
## Function: ProcessWoodburnerOnOffKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments: Turn a woodburner pump on or off.
##
################################################################################

def ProcessWoodburnerOnOffKey (keyValue) :

    parameters = {
    
       GD.KEYVALUE_WB_PUMP_1_ON :  (GD.KEYVALUE_WB_PUMP_1_OFF, GD.SYSTEM_WOODBURNER_PUMP_1),
       GD.KEYVALUE_WB_PUMP_2_ON :  (GD.KEYVALUE_WB_PUMP_2_OFF, GD.SYSTEM_WOODBURNER_PUMP_2),
       GD.KEYVALUE_WB_PUMP_1_OFF :  (GD.KEYVALUE_WB_PUMP_1_ON, GD.SYSTEM_WOODBURNER_PUMP_1),
       GD.KEYVALUE_WB_PUMP_2_OFF :  (GD.KEYVALUE_WB_PUMP_2_ON, GD.SYSTEM_WOODBURNER_PUMP_2)
    }

    if keyValue in parameters :
        # Clear any active text on the opposite key.
        keyData.UpdateSelectKeyGroupText (GD.KEYVALUE_NONE, parameters [keyValue][0])        
        
        # Are we doing an on operation?
        if keyValue in (GD.KEY_GROUP_WB_ON) :
            # Attempt to set bit high. If bit is in override low this will cancel the override.
            result = system.systemControl [parameters [keyValue][1]].SetOverrideBitHigh ()
        else :
            # Attempt to set bit low. If bit is in override high this will cancel the override.
            result = system.systemControl [parameters [keyValue][1]].SetOverrideBitLow ()
            
        # If we did a high or low operation make text active. An override cancel will return false.
        if result == True :
            keyData.UpdateSelectKeyGroupText (keyValue)

        # Set the woodburner control key bands according to the system configuration data bits.
        keyData.SetSystemConfigBandStatus (GD.WOODBURNER_CONTROL_GROUP, GD.KEY_GROUP_WB_ON, GD.KEY_GROUP_WB_OFF)
        
        # Display the updated key images.
        display.UpdateSelectKeyImages (GD.KEY_GROUP_ALL_WB, GD.UPDATE_ALL)
           
    return 1
    
        GD.KEYVALUE_IMM_1_ON : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_IMM_2_ON : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_IMM_3_ON : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_IMM_4_ON : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_IMM_1_OFF : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_IMM_2_OFF : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_IMM_3_OFF : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_IMM_4_OFF : keysSystem.ProcessManualControlOnOffKey,

        GD.KEYVALUE_WB_PUMP_1_ON : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_WB_PUMP_2_ON : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_WB_PUMP_1_OFF : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_WB_PUMP_2_OFF : keysSystem.ProcessManualControlOnOffKey,

        GD.KEYVALUE_TANK_1_PUMP_ON : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_TANK_1_PUMP_OFF : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_V1_EXT_TO_T1 : keysSystem.ProcessManualControlOnOffKey,
        GD.KEYVALUE_V1_EXT_TO_HEATING : keysSystem.ProcessManualControlOnOffKey,
#http://homesex18.com/p/ft124.jpg

#    if (keyData.CheckIfNoBand (GD.KEYVALUE_OIL_TO_HEAT) == False 
 #       or 
  #      keyData.CheckIfNoBand (GD.KEYVALUE_OIL_TO_T1) == False) :
        
   #     keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_OIL_OFF, GD.KEY_GROUP_BOILER_MODE)

    # Clear any other active system keys and make this one active and with on (green) band to indicate that this is the key
    # just pressed and that Tank 1 is feeding the heating circuits.
   # keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_T2_TO_HEAT, GD.KEY_GROUP_HEATING_MODE)
    
    
    # Clear any other active system keys and make this one active and with on (green) band to indicate that this is the key
    # just pressed and that Tank 1 is feeding the heating circuits.
    # If oil to heating is active we need to make it idle and set boiler to off.
    if keyData.CheckIfNoBand (GD.KEYVALUE_OIL_TO_HEAT) == False :

        keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_OIL_OFF, GD.KEY_GROUP_BOILER_MODE)

    keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_T1_TO_HEAT, GD.KEY_GROUP_HEATING_MODE)
    # Clear any other active system keys and make this one active and with on (green) band to indicate that this is the key
    # just pressed and that oil boiler is feeding the heating circuits.
    # We will update the key in 2 groups - as the oil to heating key is in the heating group and the boiler group.   
##    keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_OIL_TO_HEAT, GD.KEY_GROUP_HEATING_MODE+GD.KEY_GROUP_BOILER_MODE)
   
    # If oil or T2 to heating is active we need to make it idle and set T1 to heating.
    if (keyData.CheckIfNoBand (GD.KEYVALUE_OIL_TO_HEAT) == False 
        or 
        keyData.CheckIfNoBand (GD.KEYVALUE_T2_TO_HEAT) == False) :
        
        keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_T1_TO_HEAT, GD.KEY_GROUP_HEATING_MODE)

    # Clear any other active system keys and make this one active and with on (green) band to indicate that this is the key
    # just pressed and that oil boiler is feeding tank 1.
    keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_OIL_TO_T1, GD.KEY_GROUP_BOILER_MODE)
   


    # If oil to heating is active we need to make it idle and set T1 to heating.
    if keyData.CheckIfNoBand (GD.KEYVALUE_OIL_TO_HEAT) == False :
        keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_T1_TO_HEAT, GD.KEY_GROUP_HEATING_MODE)

    # Clear any other active system keys and make this one active and with on (green) band to indicate that this is the key
    # just pressed and that oil boiler is feeding tank 2.
    keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_OIL_TO_T2, GD.KEY_GROUP_BOILER_MODE)
    # If oil to heating is active we need to make it idle and set T1 to heating.
    if keyData.CheckIfNoBand (GD.KEYVALUE_OIL_TO_HEAT) == False :
        keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_T1_TO_HEAT, GD.KEY_GROUP_HEATING_MODE)

    # Clear any other active system keys and make this one active and with off (red) band to indicate that this is the key
    # just pressed and that oil boiler is off.
    keyData.SetSelectKeyActiveWithBandOn (GD.KEYVALUE_OIL_OFF, GD.KEY_GROUP_BOILER_MODE)
   

################################################################################
##
## Function: ProcessSystemAutoModeKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The System Auto mode key will set the system to auto. The key will show as active and the on band will be
## set on. The Off, Manual and Holiday mode keys will be set to their idle state.
##
################################################################################

def ProcessSystemAutoModeKey (keyValue) :

    # Move to required mode.
    GD.currentMode = GD.MODE_AUTO_MODE_SELECT
    
    # Display keyboard for this mode
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    
    # Set the System Auto config bit and make System Auto key text active.
    system.UpdateSystemStatusBits (bitsHigh = GD.SYSTEM_AUTO_MODE, bitsLow = GD.SYSTEM_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_AUTO_MODE, textIdle = GD.KEY_GROUP_SYSTEM_MODE)
    
    # Read the config bits and update the bands on all the system control keys. 
    keyData.SetControlBandStatus (GD.SYSTEM_CONTROL_GROUP, GD.KEY_GROUP_SYSTEM_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_SYSTEM_MODE, GD.UPDATE_ALL)

    return 1
    
################################################################################
##
## Function: ProcessSystemManualModeKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The System Manual mode key will set the system to manual. The key will show as active and the on band will be
## set on. The Off, Auto and Holiday mode keys will be set to their idle state.
##
################################################################################

def ProcessSystemManualModeKey (keyValue) :

    # Move to required mode.
    GD.currentMode = GD.MODE_MANUAL_MODE_SELECT
    
    # Display keyboard for this mode
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    
    # Set the System Manual config bit and make System Manual key text active.
    system.UpdateSystemStatusBits (bitsHigh = GD.SYSTEM_MANUAL_MODE, bitsLow = GD.SYSTEM_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_MANUAL_MODE, textIdle = GD.KEY_GROUP_SYSTEM_MODE)
    
    # Read the config bits and update the bands on all the system control keys. 
    keyData.SetControlBandStatus (GD.SYSTEM_CONTROL_GROUP, GD.KEY_GROUP_SYSTEM_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_SYSTEM_MODE, GD.UPDATE_ALL)
   
    return 1
    
################################################################################
##
## Function: ProcessSystemHolidayModeKey (keyValue)
##
## Parameters: keyValue - integer - the current key value
##
## Returns:
##
## Globals modified:
##
## Comments:The System Holiday mode key will set the system to holiday. The key will show as active and the on band will be
## set on. The Off, Auto and Manual mode keys will be set to their idle state.
##
################################################################################

def ProcessSystemHolidayModeKey (keyValue) :

    # Move to required mode.
    GD.currentMode = GD.MODE_HOLIDAY_MODE_SELECT
    
    # Display keyboard for this mode
    display.DisplayKeyboardImage (useMode = GD.currentMode)
    
    # Set the System Holiday config bit and make System Holiday key text active.
    system.UpdateSystemStatusBits (bitsHigh = GD.SYSTEM_HOLIDAY_MODE, bitsLow = GD.SYSTEM_CONTROL_GROUP)
    keyData.UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_HOLIDAY_MODE, textIdle = GD.KEY_GROUP_SYSTEM_MODE)
    
    # Read the config bits and update the bands on all the system control keys. 
    keyData.SetControlBandStatus (GD.SYSTEM_CONTROL_GROUP, GD.KEY_GROUP_SYSTEM_MODE)
    
    # Display all the control keys with their new band status.
    display.UpdateSelectKeyImages (GD.KEY_GROUP_SYSTEM_MODE, GD.UPDATE_ALL)

    return 1
    
