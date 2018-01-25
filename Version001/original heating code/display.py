print 'Loaded display module'
import serial
import GD
import zones 
import string
import time
from random import randint
import keys
import keysSystem
import keyData
import system

# When we initialise the serial port we wii keep te serial port object here.
RS232Port = 0

# A message id that we found looking for ACK/NAK will go in this global so that we can pick it up next time we
# check for a button message.
savedMessageId = 0

# When we are in normal operation the screen displays 'Press to start' in random locations. This global holds the
# location we last used. The location is a random number we generate between 0 and 9.
pressToStartLocation = 0

class message :

    def __init__ (self) :
        # We will build the message here.
        self.messageString = ''
        # Flag to show if we have a message to display that we have built. If we have not built a message then a
        # call to DisplayMessage will just display the message supplied.
        self.messagePending = False
        
    def StartMessage (self, startString) :
        self.messageString = startString
        self.messagePending = True
        
    def AddToMessage (self, addString) :
        # Make sure a message has been started, if not start a new one.
        if self.messagePending :
            self.messageString += addString
        else :
            self.messageString = addString
            
        self.messagePending = True
        
    def DisplayMessage (self, addString) :
        # If a message has been started add to it and display, if not display what has just been sent.
        if self.messagePending :
            self.messageString += addString
        else :
            self.messageString = addString
            
        self.messagePending = False

################################################################################
#
# Function: InitialiseDisplayKeyboardModule ()
#
# Parameters: None
#
# Returns: serial port object - this is the port to the display module
#
# Globals modified:
#
# Comments: Opens the port to the display module.
#
################################################################################

def InitialiseDisplayKeyboardModule () :

    # Use serial port for communication
    serialPort = serial.Serial ("/dev/ttyAMA0", baudrate=9600, bytesize=8,parity='N',stopbits=1)
   
    # When we initialise the serial port the display module receives a spurious character so we feed it nulls
    # until it sends us back a NAK or data to get it back in sync.

    # Set a reasonable timeout for sending the nulls (the ser.read will cause the wait).
    serialPort.timeout = 0.5

    # Now wait for the display module to send the NAK (we do not check if it is a NAK) or data
    while (serialPort.read () =='') :
        serialPort.write (chr (0))

    # Discard any data that is returned.
    while (serialPort.read () !='') :
        print 'Discard'

    # Now set no timeout so we do not wait when looking for received data in the main loop.
    serialPort.timeout=0

    # Pass serial port object back to caller.
    return serialPort

################################################################################
#
# Function: CheckForSerialInput (buttonOrAck)
#
# Parameters: buttonOrAck - boolean - flag to indicate if we are looking for an ACK or a button (true = button)
#
# Returns: messageId - integer - the id of the button pressed (zero if none)
#
# Globals modified:
#
# Comments:
#
# TODO: SORT OUT ACK NAK RESPONSE TO MESSAGE
#
################################################################################

def CheckForSerialInput (buttonOrAck) :

    # A message id that we found looking for ACK/NAK will go in this global so that we can pick it up next time we
    # check for a button message.
    global savedMessageId
    
    checksum = 0
    messageId = 0
    
    # Try and find an ACK/NAK or a button message.
    while True :
               
        # Are we checking for an ACK/NAK?
        if buttonOrAck == GD.CHECK_FOR_ACK :
        
            # Set timeout so we wait for it.
            RS232Port.timeout = 2
            
            # Try and get byte and then restore timeout to zero.
            messageId = RS232Port.read (1)
            RS232Port.timeout = 0
        
            # If we have got an ACK/NAK pass it to caller or it could be the id byte of a button message. We will check below.
            if messageId in (chr(0x06), chr(0x15)) :
                messageId = ord (messageId)
                break
                
        else :
            # We must be checking for a button message. If we have one return the id. It may have been found previously
            # whilst we were checking for an ACK/NAK.
            if savedMessageId != 0 :
                
                # Keep the id while we clear the global. Then return the id.
                messageId = savedMessageId
                savedMessageId = 0
                break
                
            # We do not have a message so look for id byte in the buffer. No timeout as there may not be a byte.
            messageId = RS232Port.read (1)
             
        # Get here with or without a byte if we are looking for a button message or get here with a byte that was not an
        # ACK/NAK whilst looking for an ACK/NAK. If it is not a button message start id just leave.
        if messageId != chr (0x07) :
            messageId = 0
            break
     
        # We have got a button message id so clear a buffer to build message in.
        messageBuffer = []
        # Put Id at start of the buffer.
        messageBuffer.append (messageId)
        # Now try and read the rest of the button message into the buffer. Use timeout as message may still be arriving.
        RS232Port.timeout = 2
        messageBuffer.extend (RS232Port.read (5))
        RS232Port.timeout = 0
        
        # Did we get all the message?
        if len (messageBuffer) >= 6 :
        
            # Turn the bytes to ints and calculate the checksum.
            for messageIndex in range (6) :
                messageByte = ord (messageBuffer[messageIndex])
                messageBuffer[messageIndex] = messageByte
                checksum ^= messageByte
                #print hex (messageByte),
###################################fix for android testing
                checksum = 0
###################################
            if checksum == 0 :              
                # Work out button type?
                if messageBuffer[1] == GD.USERBUTTON_MESSAGE :
                    # It is a Userbutton - pass code back.
                    savedMessageId = messageBuffer[2] 
                   
            else :
                # Bad checksum so send NAK to display module. TODO
                print 'nak'
                #RS232Port.write (chr (0x15))

    # endwhile 
    # Pass messageId back to caller, it will be zero if we do not have a valid message.
    return messageId

################################################################################
#
# Function: WriteToDisplay (sequence)
#
# Parameters: sequence - string - this contains the bytes to send to the display, excluding the checksum
#                      
# Returns: Nothing
#
# Globals modified:
#
# Comments: Simply sends the string of bytes to the serial port and adds the checksum to the end
#
# TODO: SORT OUT RESPONSE TO ACK NAK
#
################################################################################

def WriteToDisplay (sequence) :

    checksum = 0
    
    # Only send the sequence if there is one.
    if sequence != '' :
    
        # Send all the message except the checksum. Calculate checksum as we go.
        for messageByte in sequence:
            RS232Port.write (messageByte)
            checksum ^= ord (messageByte)

        # Now send the checksum.
        RS232Port.write (chr (checksum))
        
        # Wait for ACK/NAK (TODO)
        CheckForSerialInput(GD.CHECK_FOR_ACK)
    
    return

################################################################################
##
## Function: GenerateSound (sound)
##
## Parameters: sound - integer - the sound required
##
## Returns:
##
## Globals modified:
##
## Comments: Used to generate a sound on the display module.
##
################################################################################
    
def GenerateSound (sound) :
    # Build the form select message (excluding checksum).
    beep = chr (0x01) + chr (0x16) + chr (0x00) + chr (0x00) + sound
    # Send to the display module.
    WriteToDisplay (beep)
    
################################################################################
##
## Function: AdjustVolume (level)
##
## Parameters: level - integer - the volume level required
##
## Returns:
##
## Globals modified:
##
## Comments: Used to adjust the volume on the display module.
##
################################################################################

def AdjustVolume (level) :
    # Build the form select message (excluding checksum).
    volume = chr (0x01) + chr (0x16) + chr (0x01) + chr (0x00) + level
    # Send to the display module.
    WriteToDisplay (volume)
       
################################################################################
#
# Function: DisplayForm (form)
#
# Parameters: form - integer - the form required
#
# Returns:
#
# Globals modified:
#
# Comments: Displays the required form on the display module
#
################################################################################

def DisplayForm (form) :
    # Build the form select message (excluding checksum).
    formSelectMessage = chr (0x01) + chr (0x0a) + chr (form) + chr (0x00) + chr (0x00)
    # Send to the display module.
    WriteToDisplay (formSelectMessage)

################################################################################
#
# Function: DisplayKeyboardImage (keyboardImage = 0, useMode = GD.MODE_NONE)  
#
# Parameters: keyboardImage - integer - the index of the keyboard image we want to display
#                     OR 
#                     useMode - integer - the current mode so we can look up keyboard image
#
# Returns:
#
# Globals modified:
#
# Comments: Displays the required image. Each keyboard has a pre-programmed image. We can select which one
# either by supplying the actual index to the image or the current mode. For the latter we look up the image index.
#
################################################################################

def DisplayKeyboardImage (keyboardImage = 0, useMode = GD.MODE_NONE) :

    # Lookup table of current mode to image index.
    keyboardData = {
                               GD.MODE_NONE : 0,
                               GD.MODE_RAD_WAITING_ZONE_SELECT : GD.RAD_WAITING_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_UFH_WAITING_ZONE_SELECT : GD.UFH_WAITING_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_RAD_ZONE_SELECT : GD.RAD_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_UFH_ZONE_SELECT : GD.UFH_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_PROG_TIME : GD.TIME_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_PROG_DAY : GD.DAY_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_OFF_MODE_SELECT : GD.SYSTEM_OFF_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_SYSTEM_OPTIONS : GD.SYSTEM_OPTIONS_KEYBOARD_IMAGE,
                               GD.MODE_AUTO_OPTIONS : GD.AUTO_OPTIONS_KEYBOARD_IMAGE,
                               GD.MODE_MANUAL_OPTIONS : GD.MANUAL_OPTIONS_KEYBOARD_IMAGE,
                               GD.MODE_HOLIDAY_OPTIONS : GD.HOLIDAY_OPTIONS_KEYBOARD_IMAGE,
                               GD.MODE_IMMERSION_MANUAL_CONTROL : GD.IMMERSION_CONTROL_KEYBOARD_IMAGE,
                               GD.MODE_WOODBURNER_MANUAL_CONTROL : GD.WOODBURNER_CONTROL_KEYBOARD_IMAGE,
                               GD.MODE_MANUAL_OVERRIDE_MAIN_MENU : GD.MANUAL_CONTROL_KEYBOARD_IMAGE,
                               GD.MODE_TANK_1_MANUAL_CONTROL : GD.TANK_1_CONTROL_KEYBOARD_IMAGE,
                               GD.MODE_TANK_2_MANUAL_CONTROL : GD.TANK_2_CONTROL_KEYBOARD_IMAGE,
                               GD.MODE_BOILER_MANUAL_CONTROL : GD.BOILER_CONTROL_KEYBOARD_IMAGE,
                               GD.MODE_HEATING_MANUAL_CONTROL : GD.HEATING_CONTROL_KEYBOARD_IMAGE,
                               GD.MODE_IMMERSION_WAITING_SELECT : GD.IMMERSION_WAITING_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_IMMERSION_SELECT : GD.IMMERSION_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_AUTO_MODE_SELECT : GD.AUTO_MODE_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_MANUAL_MODE_SELECT : GD.MANUAL_MODE_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_HOLIDAY_MODE_SELECT : GD.HOLIDAY_MODE_SELECT_KEYBOARD_IMAGE,
                               GD.MODE_DISPLAY_STATUS : GD.SYSTEM_STATUS_SELECT_KEYBOARD_IMAGE
                              }

    # If a mode is supplied we will use the lookup value (assumes no keyboardImage supplied).
    keyboardImage += keyboardData [useMode]
   
    # Build the image select message (excluding checksum) and send to the display module.
    imageSelectMessage = chr(0x01) + chr(0x1B) + chr(0x00)  + chr(0x00) + chr (keyboardImage)
    WriteToDisplay (imageSelectMessage)

################################################################################
##
## Function: IlluminateKeys (flashOn)
##
## Parameters: flashOn - boolean - indicates whether to use the on or off image.
##
## Returns:
##
## Globals modified:
##
## Comments: Scans all the zones for the current 'select' keyboard and illuminates the keys of on and changed zones. An
## on zone is shown green, off to on is flashing green and on to off is flashing red. If a zone is selected the text is set yellow.
##
################################################################################

def IlluminateKeys (flashOn) :

    # Scan each room select key and get the keyvalue. We scan through keyCodes rather than keyValues as by looking up
    # keyValue it will select the correct keyValue for rad or ufh because the current mode is used in the lookup.
    for keyCode in (1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19) :
        keyValue = keyData.GetKeyValue (keyCode)
        
        # If this is a displayable key display the key image. 
        if keyValue > 0 :
            # If this key is flashing we need to display either the flash off or flash on image.
            if keyData.CheckIfFlashRequired (keyValue) == True :
                # Is it time for on or off image?
                if flashOn :
                    imageSequence = keyData.GetKeyImageSequence (keyValue)
                else :
                    imageSequence = keyData.GetKeyImageSequence (keyValue, lastStatus = True)
                
                WriteToDisplay (imageSequence)
            # Not flashing so just display the image if it has changed. This saves us sending redundant data to the display.
            else :
                imageSequence = keyData.GetChangedKeyImageSequence (keyValue)
                WriteToDisplay (imageSequence)
               
################################################################################
##
## Function: DisplayPressToStart () 
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: Each call to this function will display 'Press To Start.' at one of ten locations on the blank screen. The ten
## locations are visi-genie set strings. We use a random int to decide which to use. 
##
################################################################################

def  DisplayPressToStart () :

    # Current location used is held here.
    global pressToStartLocation

    # Clear the current location used.
    WriteToDisplay (chr(0x01) + chr(0x11) + chr(pressToStartLocation) + chr(0x00) + chr(0x00))
        
    # Remember current location while we get a new location.
    currentLocation = pressToStartLocation

    # Get a new location, must be different from current one.
    while (currentLocation == pressToStartLocation) :
        pressToStartLocation = randint (0, 9)

    # Send to the new location.
    WriteToDisplay (chr(0x01) + chr(0x11) + chr(pressToStartLocation) + chr(0x00) + chr(0x01))
    
    
################################################################################
##
## Function: DisplayKeyImageSequence (keyValue, image = -1)
##
## Parameters: keyValue - integer - key value of the sequence to display
##                   image - integer - if an image value is supplied it will used instead of the offset lookup value.
##
## Returns: The sequence of bytes that were sent to the display module (excluding checksum). 
##
## Globals modified:
##
## Comments: If the image parameter is omitted then the keyValue is used to lookup both the base address and the offset
## of the required image. If the image parameter is supplied then keyValue is used to lookup the base address, but the value
## of image is used as the offset to the image.
##
################################################################################

def DisplayKeyImageSequence (keyValue, image = -1) :
    imageSequence = keyData.GetKeyImageSequence (keyValue, image)
    WriteToDisplay (imageSequence)
    return imageSequence
        
################################################################################
##
## Function: UpdateSelectKeyImages (updateGroup, updateType = GD.UPDATE_ALL)
##
## Parameters: updateGroup - tuple - the keyvalues to update
##                      updateType - integer - select  images to update: all = 0,  only those changed = 1
##
## Returns:
##
## Globals modified:
##
## Comments: Check select keys and update all the images or any that have changed (depends on updateType).
##
################################################################################

def UpdateSelectKeyImages (updateGroup, updateType = GD.UPDATE_ALL) :

    for keyValue in (updateGroup) :

        if updateType == GD.UPDATE_ALL :
            WriteToDisplay (keyData.GetKeyImageSequence (keyValue))
        else :
            WriteToDisplay (keyData.GetChangedKeyImageSequence (keyValue))
   
################################################################################
#
# Function: DisplayAutoEnableKeyImage (zone)
#
# Parameters: zone - integer - the zone selected
#
# Returns: imageSelectMessage - string- the message we sent to display the key
#
# Globals modified:
#
# Comments: The image on the auto/manual/enable/disable key changes depending on the mode we are in and the state
# of auto/manual and enable/disable.
#
################################################################################

def DisplayAutoEnableKeyImage (zone) :

    # We use a single button to control Auto/Manual and Disable/Enable. If we are in a time programming mode
    # the user can switch between Auto and Manual modes. In day programming modes the user can switch
    # between Disable and Enable.
    # Are we in a time programming mode?
    if GD.currentMode in (GD.MODE_PROG_TIME, GD.MODE_PROG_ON_AT, GD.MODE_PROG_OFF_AT) :
        # Are we in Auto mode?
        if zones.zoneTimes.CheckIfAutoMode () == True :
            imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_AUTO_MANUAL, GD.KEY_IMAGE_MANUAL)
        
        else :
            imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_AUTO_MANUAL, GD.KEY_IMAGE_AUTO)
            
    else :
         # We are in day programming mode. Are we disabled?
        if zones.zoneTimes.CheckIfDisabled (GD.DAYS_INDEX) == True :
            imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_AUTO_MANUAL, GD.KEY_IMAGE_ENABLE)
            
        else :
            imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_AUTO_MANUAL, GD.KEY_IMAGE_DISABLE)

    return imageSelectMessage
 
################################################################################
#
# Function: DisplayCancelResumeKeyImage (zone)
#
# Parameters: zone - integer - the zone selected
#
# Returns: imageSelectMessage - string- the message we sent to display the key
#
# Globals modified:
#
# Comments: The image on the cancel/resume key changes depending on whether the zone is auto on or cancelled.
#
################################################################################

def DisplayCancelResumeKeyImage (zone) :

    # If a zone is active and cancelled we display the resume key. If a zone is active and on we will display the cancel key.
    # For other cases we leave the key blank. The key is also blanked if boost is active as we do not allow cancel / resume
    # when boost is on.
    if  zones.zoneData[zone].CheckIfZoneBoostOn () == True :
        imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_CAN_RES, GD.KEY_IMAGE_BLANK)
        
    elif zones.zoneData[zone].CheckIfZoneTimedIsCancelled () == True :
        imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_CAN_RES, GD.KEY_IMAGE_RESUME)
        
    elif zones.zoneData[zone].CheckIfZoneOnRequested () == True :
        imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_CAN_RES, GD.KEY_IMAGE_CANCEL)
        
    else :
        imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_CAN_RES, GD.KEY_IMAGE_BLANK)

    return imageSelectMessage
 
################################################################################
#
# Function: DisplayBoostKeyImage (zone)
#
# Parameters: zone - integer - the zone selected
#
# Returns: imageSelectMessage - string- the message we sent to display the key
#
# Globals modified:
#
# Comments: The image on the boost key changes depending on whether the next press will turn boost on or off.
#
################################################################################

def DisplayBoostKeyImage (zone) :

    # If boost is on and boostPresses != 1  this means that this is a prior boost or the user has pressed
    # boost twice. We shall therefore display the 'Boost Off' key, for other cases it is 'Boost On'.
    if  zones.zoneData[zone].CheckIfZoneBoostOn () == True and GD.boostPresses != 1 :
        imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_BOOST, GD.KEY_IMAGE_BOOST_OFF)
    else :
        imageSelectMessage = DisplayKeyImageSequence (GD.KEYVALUE_BOOST, GD.KEY_IMAGE_BOOST)
 
    return imageSelectMessage
 
################################################################################
#
# Function: DisplayString (sequence, field)  
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

def DisplayString (sequence, field) :

    # Add the header to string to output
    sequence = field + chr (len (sequence)) + sequence

    WriteToDisplay (sequence)

################################################################################
##
## Function: DisplayZoneMode (zone = -1)
##
## Parameters: zone - integer - the zone selected - if no zone supplied blank the field
##
## Returns:
##
## Globals modified: 
##                             
## Comments:
##                   
################################################################################

def DisplayZoneMode (zone = -1) :

    modeMessage = ''
    # Check if zone supplied and valid.
    if zone in range (0, 34) :
        # Is it RAD, UFH or Immersion zone? rad is 0-13, ufh is 14-29, immersion is 30-33. Start message with Rad or Ufh as required. 
        if zone in range (0, 14) :
            modeMessage = 'Rad '
        elif zone in range (14, 30) :
            modeMessage = 'Ufh '

        # Add name part of message.
        modeMessage += zones.zoneData[zone].GetZoneName() + ' in '
        
        # Are we in auto mode or manual mode?
        if zones.zoneTimes.CheckIfAutoMode () == True :
            modeMessage += 'Auto mode'
        else :
            modeMessage += 'Manual mode'
        
    # Display the current zone mode. Will be blank if no zone.
    DisplayString (modeMessage, GD.TOP_LEFT_INFO_FIELD)

################################################################################
##
## Function: DisplayZoneStatus (zone, zoneStatus)
##
## Parameters: zone - integer - the zone selected
## zoneStatus - 4 integer tuple - (status from 0-5, day from 0-6, hour from 0-23, minute from 0-59)
## Values for status are:
##               0=zone not active - time is next on time.
##               1=zone active - time is off time
##               2=manual mode - day is set to -1
##               3=boost mode - time is off time
##               4=zone active, but cancelled - time is off time
##               5=error in zone time file - day set to -1
##
## Returns:
##
## Globals modified: 
##                             
## Comments:
##                   
################################################################################

def DisplayZoneStatus (zone, zoneStatus) :

    dayNameLookup = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    messageLookup = {GD.STATUS_ZONE_NOT_ACTIVE : ' Off',
                                    GD.STATUS_ZONE_ACTIVE : ' On',
                                    GD.STATUS_BOOST_MODE : ' On Boost',
                                    GD.STATUS_ZONE_CANCELLED : ' Cancelled',
                                    GD.STATUS_PROGRAM_FILE_ERROR : ' No Programmed Times',
                                    GD.STATUS_MANUAL_MODE : ' Off'}

    statusMessage = 'Current status: '

    if zoneStatus[0] in messageLookup :
        statusMessage += messageLookup[zoneStatus[0]]
        
    # Add the time and day to message if required.
    if zoneStatus[0] in (GD.STATUS_ZONE_NOT_ACTIVE, GD.STATUS_ZONE_ACTIVE,
                                        GD.STATUS_BOOST_MODE, GD.STATUS_ZONE_CANCELLED) :
        statusMessage = statusMessage +' Until ' +\
                                     str (zoneStatus[2]).zfill(2) + ':' + str (zoneStatus[3]).zfill(2) + ' ' +\
                                     dayNameLookup[zoneStatus[1]]

    # Display the current zone status.
    DisplayString (statusMessage, GD.MIDDLE_LEFT_INFO_FIELD)

################################################################################
##
## Function: DisplayStatus (keyValue, index = 0)
##
## Parameters: keyValue - integer - the current key value of the status data group to display
##                    index - integer - the status field to display, if zero do not display just return number of fields
##
## Returns: numberOfStatus - integer - the number of fields for this group.
##
## Globals modified:
##
## Comments:Displays the status selected. The keyvalue selects the group of status to display and the index selects which
## status from the group to display. E.g. for an immersion we have 2 statuses: On / Off and Max / Heating so in this
## case keyvalue selects the immersion and index will select on / off or max / not max status to display.
##
################################################################################

def DisplayStatus (keyValue, index = 0) :

    # Lookup table for each of our status groups. For each group we hold the following:
    # The number of status options in the group, the text for the group, then sets of 3 elements for each option, which are :
    # the system control code, the text for the on state, the text for the off state for this control code. If the control code is
    # for an analog input then the 1st text is used before the analog value and the 2nd text is used after it.
    statusLookup = {
        GD.KEYVALUE_IMM_1_STATUS : (2, 'Immersion 1 is ',
                                                       GD.SYSTEM_IMM_1, 'On', 'Off',
                                                       GD.SYSTEM_IMM_1_MAX, 'at Max', 'not at Max'),

        GD.KEYVALUE_IMM_2_STATUS : (2, 'Immersion 2 is ',
                                                       GD.SYSTEM_IMM_2, 'On', 'Off',
                                                       GD.SYSTEM_IMM_2_MAX, 'at Max', 'not at Max'),

        GD.KEYVALUE_IMM_3_STATUS : (2, 'Immersion 3 is ',
                                                       GD.SYSTEM_IMM_3, 'On', 'Off',
                                                       GD.SYSTEM_IMM_3_MAX, 'at Max', 'not at Max'),

        GD.KEYVALUE_IMM_4_STATUS : (2, 'Immersion 4 is ',
                                                       GD.SYSTEM_IMM_4, 'On', 'Off',
                                                       GD.SYSTEM_IMM_4_MAX, 'at Max', 'not at Max'),

        GD.KEYVALUE_WOODBURNER_STATUS : (3, 'Woodburner ',
                                                       GD.SYSTEM_WOODBURNER_PUMP_1, 'pump 1 is On', 'pump 1 is Off',
                                                       GD.SYSTEM_WOODBURNER_PUMP_2, 'pump 2 is On', 'pump 2 is Off',
                                                       GD.SYSTEM_WOODBURNER_FLOW_DETECT, 'flow detected', 'no flow detected'),
##                                                       GD.SYSTEM_WOODBURNER_SENSOR_CONNECTED, 'sensor found', 'sensor not found'),

        GD.KEYVALUE_BOILER_STATUS : (2, 'Boiler ',
                                                       GD.SYSTEM_BOILER_ON, 'is On', 'is Off',
                                                       GD.SYSTEM_V3_BOILER_TO_INT, 'feeds tank 1 or heating', 'feeds tank 2'),

        GD.KEYVALUE_TANK_1_STATUS : (2, 'Tank 1 ',
                                                       GD.SYSTEM_TANK_1_PUMP,  'pump is On', 'pump is Off',
                                                       GD.SYSTEM_V1_EXT_TO_TANK_1, 'is fed from boiler or tank 2', 'is not fed from boiler or tank 2'),
##                                                       GD.SYSTEM_TANK_1_SENSOR_CONNECTED, 'sensor found', 'sensor not found'),

        GD.KEYVALUE_TANK_2_STATUS : (2, 'Tank 2 ',
                                                       GD.SYSTEM_TANK_2_PUMP,  'pump is On', 'pump is Off',
                                                       GD.SYSTEM_EXT_TO_INT, 'or boiler feeds tank 1 or heating', 'is in circulation mode'),

        GD.KEYVALUE_RADS_STATUS : (2, 'Rad ',
                                                       GD.SYSTEM_RAD_PUMP,  'pump is On', 'pump is Off',
                                                       GD.SYSTEM_RAD_DEMAND, 'demand', 'no demand'),

        GD.KEYVALUE_UFH_STATUS : (2, 'Ufh ',
                                                       GD.SYSTEM_UFH_PUMP,  'pump is On', 'pump is Off',
                                                       GD.SYSTEM_UFH_DEMAND, 'demand', 'no demand'),
    
        GD.KEYVALUE_HW_STATUS : (2, 'Hot water ',
                                                       GD.SYSTEM_TANK_1_PUMP,  'pump is On', 'pump is Off',
                                                       GD.SYSTEM_HW_DEMAND, 'demand', 'no demand'),
    
        GD.KEYVALUE_SYSTEM_STATUS : (1, 'System ',
                                                       GD.SYSTEM_MAINS_FAIL,  'mains failed', 'mains OK'),
    
        GD.KEYVALUE_BATH_1_STATUS : (1, 'Bathroom 1 ',
                                                       GD.SYSTEM_BATH_1_SHOWER_ACTIVE,  'shower in use', 'shower not in use'),
    
        GD.KEYVALUE_BATH_2_STATUS : (1, 'Bathroom 2 ',
                                                       GD.SYSTEM_BATH_2_SHOWER_ACTIVE,  'shower in use', 'shower not in use'),
    
        GD.KEYVALUE_BATH_3_4_STATUS : (1, 'Bathroom 3/4 ',
                                                       GD.SYSTEM_BATH_3_4_SHOWER_ACTIVE,  'shower in use', 'shower not in use')}
    
    # Make sure keyValue request is valid.
    if keyValue in statusLookup :
    
        # Get the number of statuses available.
        numberOfStatus = statusLookup [keyValue] [0]
        
        # If no index supplied then just return the number of statuses.
        if index < 1 :
            return numberOfStatus
        
        # If we get here we have an index so make sure index is valid.
        if index <= numberOfStatus :
        
            # Create the text for the X of N entries field and display it.
            entries = '(' + str (index) + ' of ' + str (numberOfStatus) + ')'
            DisplayString (entries, GD.MIDDLE_RIGHT_INFO_FIELD)

            # Convert index to value required to access correct statusLookup elements.
            index -= 1
            index *= 3
            index += 2
            
            # Get the elements for this status.
            controlBit, onText, offText = statusLookup [keyValue] [index : index+3]
        
            # Build string according to state of status. Start with the name of the status group.
            statusString = statusLookup [keyValue][1]
            
            #Check state of status and add text according to value
            if system.systemControl [controlBit].CheckIfBitHigh () == True :
                statusString += onText
            else :
                statusString += offText

            # Show user the status.
            DisplayString (statusString, GD.MIDDLE_LEFT_INFO_FIELD)
        
            # Tell caller how many statuses available.
            return numberOfStatus
            
    # If we get here keyValue or index was out of range so return a zero,
    return 0
 
################################################################################
##
## Function: TopRightInfoPrompt (promptIndex = -1)
##
## Parameters: promptIndex - integer - if supplied, it is the index of a prompt to display
##
## Returns:
##
## Globals modified: 
##                             
## Comments: The clock is displayed at the top right when we are in a programming mode.
##                   
################################################################################

def TopRightInfoPrompt (promptIndex = -1) :

    promptLookup = ('',)
    
    # Do we display the clock?
    if promptIndex < 0 :
        # Get the time now and build a string of hour:minute:second, day.
        timenow = time.asctime (time.localtime (time.time ()))
        DisplayString ((timenow [11:19]+' '+timenow [0:3]), GD.TOP_RIGHT_INFO_FIELD)
    
    # Not the clock so display a prompt. Make sure index is in range.
    elif promptIndex in range (0, len (promptLookup)) :
        DisplayString (promptLookup [promptIndex], GD.TOP_RIGHT_INFO_FIELD)
            
################################################################################
##
## Function: DisplayProgOnTime (promptIndex = -1)
##
## Parameters: promptIndex - integer - if supplied, it is the index of a prompt to display
##
## Returns:
##
## Globals modified: 
##                             
## Comments: Displays: 'Set: On At XX:XX', where XX:XX is the current on time. If a promptIndex is supplied this will
## be displayed instead.
##                   
################################################################################

def DisplayProgOnTime (promptIndex = -1) :

    promptLookup = ('',)
    
    # Do we display the on time?
    if promptIndex < 0 :
        # Create and display the on half of the program entry. This is: 'Programmed: On At XX:XX'
        DisplayString ('Set: On At ' + 
                             zones.zoneTimes.GetTime (GD.ON_TIME_INDEX), GD.ZONE_ON_PROGRAM_FIELD)

    # Not the on time so display a prompt. Make sure index is in range.
    elif promptIndex in range (0, len (promptLookup)) :
        DisplayString (promptLookup [promptIndex], GD.ZONE_ON_PROGRAM_FIELD)
                             
################################################################################
##
## Function: DisplayProgOffTimeAndDays (promptIndex = -1)
##
## Parameters: promptIndex - integer - if supplied, it is the index of a prompt to display
##
## Returns:
##
## Globals modified: 
##                             
## Comments: Displays: 'Off At XX:XX Days MTWTFSS', where XX:XX is the current off time. M..S are the current days.
## If a promptIndex is supplied this will be displayed instead.
##                   
################################################################################

def DisplayProgOffTimeAndDays (promptIndex = -1) :

    promptLookup = ('',)
    
    # Do we display the off time?
    if promptIndex < 0 :
        # Create and display the off half of the program entry. This is: 'Off At XX:XX MTWTFSS'
        DisplayString ('Off At ' + zones.zoneTimes.GetTime (GD.OFF_TIME_INDEX) + '  Days ' +
                             zones.zoneTimes.GetDays (GD.DAYS_INDEX), GD.ZONE_OFF_PROGRAM_FIELD)
            
    # Not the off time so display a prompt. Make sure index is in range.
    elif promptIndex in range (0, len (promptLookup)) :
        DisplayString (promptLookup [promptIndex], GD.ZONE_OFF_PROGRAM_FIELD)

################################################################################
##
## Function: DisplayEntries (entryNumber, numberOfEntries = -1)
##
## Parameters: entryNumber - integer - the current entry number or the prompt index if numberOfEntries not supplied.
##                    numberOfEntries - integer - if supplied, the total number of entries
##
## Returns:
##
## Globals modified: 
##                             
## Comments: Displays (X of N) where X is entryNumber and N is numberOfEntries.
##                   
################################################################################

def DisplayEntries (entryNumber, numberOfEntries = -1) :

    promptLookup = ('',)
    promptIndex = entryNumber
    
    # Do we display the entries information?
    if numberOfEntries > 0 :
            # Create and display the text for the X of N entries field.
            DisplayString ( '(' + str (entryNumber) + ' of ' + str (numberOfEntries) + ')', GD.MIDDLE_RIGHT_INFO_FIELD)

    # Not the entries so display a prompt. Make sure index is in range.
    elif promptIndex in range (0, len (promptLookup)) :
        DisplayString (promptLookup [promptIndex], GD.MIDDLE_RIGHT_INFO_FIELD)


################################################################################
##
## Function: DisplayProgEntry (zone, zoneData, entryNumber)
##
## Parameters: entryNumber - integer - the entry number to display (-1 = prev, 0 = current, +ve = actual, 99 = next)
##
## Returns: - integer - the actual entry displayed (0 if no entries)
##
## Globals modified:
##
## Comments: 
##
################################################################################

def DisplayProgEntry (entryNumber, forceUpdate = False) :

    # Find number of entries.
    numberOfEntries = zones.zoneTimes.GetNumberOfProgramEntries ()

    # Only carry on if there are entries.
    if numberOfEntries > 0 :

        # Get number of last entry accessed so we can check if new entry is the same and therefore do not need to update.
        lastProgramEntry = zones.zoneTimes.GetLastEntryNumberAccessed ()

        # Select the entry. Now last entry number is updated with the actual entry number of the active entry.
        zones.zoneTimes.SelectProgramEntry (entryNumber)

        # Get the number of this entry.
        currentProgramEntry = zones.zoneTimes.GetLastEntryNumberAccessed ()
       
        # Only update if we have a new entry or we must update.
        if lastProgramEntry != currentProgramEntry or forceUpdate == True :
           
            # Show the on, off times and entries. These are all on the middle line.
            DisplayProgOnTime ()
            DisplayProgOffTimeAndDays ()
            DisplayEntries (currentProgramEntry, numberOfEntries)

    # No entries so tell caller.
    else :
        currentProgramEntry = 0

    # Tell caller which entry was displayed. We may have displayed nothing or an entry lower than requested.
    return currentProgramEntry

################################################################################
##
## Function: DisplayMiddleLeftInfoPrompt (promptIndex)
##
## Parameters: promptIndex - integer - is the index of the prompt to display
##
## Returns:
##
## Globals modified:
##
## Comments: 
##
################################################################################

def DisplayMiddleLeftInfoPrompt (promptIndex) :

    promptLookup = ( '', 
                                'Select room Rad or move to Ufh or System.',
                                'Select room Ufh or move to Rad or System.',
                                'Select System function or move to Rad or Ufh.',
                                'Select System Option.',
                                'Select Auto Option.',
                                'Select Manual Option.',
                                'Select Holiday Option.',
                                'Select Immersion On or Off.',
                                'Select W/B Pump On or Off.',
                                'Select Manual Override Option.',
                                'Select Tank 1 Manual Override Option.',
                                'Select Tank 2 Manual Override Option.',
                                'Select Boiler Manual Override Option.',
                                'Select Heating Manual Override Option.',
                                'Options Disabled while Override in Operation.',
                                'Select Immersion.',
                                'Select Status to View.',
                                'Press any key to Start.'
                             )

    DisplayString (promptLookup [promptIndex], GD.MIDDLE_LEFT_INFO_FIELD)     

################################################################################
##
## Function: DisplayBottomRightInfoPrompt (promptIndex = -1)
##
## Parameters: promptIndex - integer- if supplied, it is the index of the prompt to display 
##
## Returns:
##
## Globals modified:
##
## Comments: In programming mode we use this location to indicate if an entry is valid. If promptIndex
## is supplied we use it as the index. If it is omitted we calculate promptIndex by testing status flags.
##
################################################################################

def DisplayBottomRightInfoPrompt (promptIndex = -1) :

    promptLookup = ('', 'Not Valid', 'Disabled')
    
    if promptIndex < 0 :
        dataValid = zones.zoneTimes.GetTime (GD.ON_TIME_INDEX) < zones.zoneTimes.GetTime (GD.OFF_TIME_INDEX) and\
                           zones.zoneTimes.GetDays (GD.DAYS_INDEX) != '_______'
        
        if dataValid == False :
            promptIndex = GD.NOT_VALID_PROMPT
        elif zones.zoneTimes.CheckIfDisabled (GD.DAYS_INDEX) == True :
            promptIndex = GD.DISABLED_PROMPT
        else :
            promptIndex = GD.BLANK_PROMPT

    DisplayString (promptLookup [promptIndex], GD.BOTTOM_RIGHT_INFO_FIELD)     

################################################################################
##
## Function: DisplayBottomLeftInfoPrompt (promptIndex = -1)
##
## Parameters: promptIndex - integer- if supplied, it is the index of the prompt to display
##
## Returns:
##
## Globals modified:
##
## Comments: In programming mode we use this location to indicate if an entry needs to be saved. If promptIndex
## is supplied we use it as the index. If it is omitted we calculate promptIndex by testing status flags.
##
################################################################################

def DisplayBottomLeftInfoPrompt (promptIndex = -1) :

    promptLookup = ('', 'Not Saved', 'Save or Exit?', 'Clear To Confirm')
    
    if promptIndex < 0 :
        if GD.clearPending == True :
            promptIndex = GD.INFO_1_CLEAR_TO_CONFIRM
        elif GD.exitPending == True :
            promptIndex = GD.SAVE_OR_EXIT_PROMPT
        elif zones.zoneTimes.CheckIfDataChanged () == True :
            promptIndex = GD.NOT_SAVED_PROMPT
        else :
            promptIndex = GD.BLANK_PROMPT

    DisplayString (promptLookup [promptIndex], GD.BOTTOM_LEFT_INFO_FIELD)     
    

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


debugMessage = message ()


