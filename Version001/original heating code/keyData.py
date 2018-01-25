import GD
import display
import zones
import system

# Key values are held in dictionary. Each entry is a mode holding a list of key values for each visi key. The screen has 20 visi 
# keys. We overlay each of these visi keys with images for the keyboard layout required for the mode we are in. For each mode a
# visi key will need to return a unique code. This dictionary allows us to lookup a value for each mode / visi key combination.
keyValueLookup = {}

# Key image addresses/status held in a dictionary. Each entry is a keyvalue holding a list of the image addresses and status
# values. For each keyvalue we hold the image base address (index 0), offset (index 1), status flags to show if key has text
# idle/active (index 2, value 0/1 or 6/7 for override) and if bands 1 or 2 are off/on (indexes 3 and 4, values 0/2 and 0/4) . 
# For each of the statuses we also keep a copy of the last status values so we can determine if any have changed.
# The base address is the visi genie Userimage number. The offset is the position in the list of Userimage images for the
# 1st image of the images that are used for a particular keyvalue. The values of the text and a band status flag are added to
# this offset to get the unique image required. Depending on the use of a keyvalue we only keep the minimum nuber of images
# required to display all the combinations required. Images are always ordered as follows: 0=idle, 1=active, 2=band1 idle,
# 3=band1 active, 4=band2 idle, 5=band2 active, 6=band3 idle, 7=band3 active.
# A keyvalue that only shows only idle and active would need 2 images, whereas a key with idle, active and 3 possible 
# bands would need 8 images (idle and active for no band and idle/active with each of the 3 bands on).
# Note the bands are mutually exclusive with only 1 band  on at once. When a key has to indicate override we flash band3
# with a yellow band. If the key is also indicating an on or off we will flash alternate yellow / red or green bands. 
# Some keyvalues have no images. This occurs when a key simply takes the user to a new keyboard and the key image
# required is provided by the keyboard layout image.
keyImageLookup = {}

# Define some 'constants' for indices to make code more readable.
BASE_ADDRESS_INDEX = 0
OFFSET_INDEX = 1
TEXT_CURRENT_STATUS_INDEX = 2
BAND_1_CURRENT_STATUS_INDEX = 3
BAND_2_CURRENT_STATUS_INDEX = 4
BAND_3_CURRENT_STATUS_INDEX = 5
TEXT_LAST_STATUS_INDEX = 6
BAND_1_LAST_STATUS_INDEX = 7
BAND_2_LAST_STATUS_INDEX = 8
BAND_3_LAST_STATUS_INDEX = 9
BAND_FLASHING_INDEX = 10

################################################################################
##
## Function: GetKeyValue (visiKey, mode = -1)
##
## Parameters: visiKey - integer - the value of the visi key
##                    mode - integer - the mode we are in. If none supplied we will use current mode.
##
## Returns: the keyvalue for the supplied visikey and mode
##
## Globals modified:
##
## Comments: Each mode has a different keyboard overlaid over the 20 visi keys. This function looks up the keyvalue for
## the visi key in the supplied (or current) mode.
##
################################################################################

def GetKeyValue (visiKey, mode = -1) :

    # If no mode supplied use the current mode.
    mode = mode if mode >= 0 else GD.currentMode
    # Check if key is normal keyboard key (1-20). Because the display has an issue with processing input and output together
    # there is a possibility that a key bounce may result in a key bounce message arriving after we have switched to run mode.
    # We will, therefore, ignore any normal key if it arrives in run mode.
    if visiKey in range (1, 21) and  GD.currentMode != GD.MODE_RUN :
        keyValue = keyValueLookup [mode][visiKey]
    # If not a normal keyboard key is it one of the wakeup keys? For Android display we use normal keys.
    elif visiKey in (GD.WAKEUP_BUTTON, GD.FAILED_BUTTON) or visiKey in range (1, 21) :
        keyValue = GD.KEYVALUE_WAKEUP
    # Must be non valid key.
    else :
        keyValue = GD.KEYVALUE_NONE

    return keyValue
               
################################################################################
##
## Function: GetKeyImageSequence (keyValue, imagesOffset = -1, lastStatus = False)
##
## Parameters: keyValue - integer - key value for the sequence required
##                   imagesOffset - integer - if an image value is supplied it will used instead of the offset lookup value.
##                   lastStatus - boolean - flag to define if current or last status to be used - true for last status.
##
## Returns: The sequence of bytes to send to the display module to show the required image (excluding checksum).
##
## Globals modified:
##
## Comments: Uses either the current or last status values to lookup the sequence to display the required image.
##
################################################################################

def GetKeyImageSequence (keyValue,  imagesOffset = -1, lastStatus = False) :

    # If an image offset is supplied use it rather than lookup value. 
    if imagesOffset < 0 :
        imagesOffset = keyImageLookup [keyValue] [OFFSET_INDEX]
        
    # If the offset is not valid it means do not display, so return nothing,
    if imagesOffset < 0 :
        return ''
    
    # Get base address for this key.
    baseAddress = keyImageLookup [keyValue] [BASE_ADDRESS_INDEX]
       
    # Check if we are to use the current status or the last status values to select the image. We can use last status when we are
    # flashing a key. One image will use the current status values and the other image the last status values. We can then use
    # these 2 images alternately to produce a flashing key image.
    start = TEXT_LAST_STATUS_INDEX if lastStatus == True else TEXT_CURRENT_STATUS_INDEX
        
    # Get the text, band1, band2 and band3 status values. Note we put band1 status straight into the status variable.
    textStatus, status, band2Status, band3Status =  keyImageLookup [keyValue] [start : start+4]
    
    # If there is no band1 status get band2 status. If there is no band2 status get band3 status.
    if status == 0 :
        status = band2Status
        if status == 0 :
            status = band3Status
        
    # Now add band and text status to the offset of where the images start.
    imagesOffset += (status + textStatus)
        
    # Return sequence to caller (excluding checksum).
    return (chr (0x01) + chr (0x1B) + chr (baseAddress) + chr (0x00) + chr (imagesOffset))
    
################################################################################
##
## Function: GetChangedKeyImageSequence (keyValue)
##
## Parameters: keyValue - integer - key value of the sequence required
##
## Returns: The sequence of bytes to send to the display module to show the required image (excluding checksum).
##
## Globals modified:
##
## Comments: If the image has changed the new image sequence is returned. If the image is unchanged a null string is returned.
## We update 'last status' to be the 'current status' so if the image is not changed the next call will return a null string.
##
################################################################################

def GetChangedKeyImageSequence (keyValue) :
    # If the image has changed set last status flags to new status and return the image sequence otherwise return null string.
    if keyImageLookup [keyValue] [TEXT_CURRENT_STATUS_INDEX] != keyImageLookup [keyValue] [TEXT_LAST_STATUS_INDEX]\
      or\
      keyImageLookup [keyValue] [BAND_1_CURRENT_STATUS_INDEX] != keyImageLookup [keyValue] [BAND_1_LAST_STATUS_INDEX]\
      or\
      keyImageLookup [keyValue] [BAND_2_CURRENT_STATUS_INDEX] != keyImageLookup [keyValue] [BAND_2_LAST_STATUS_INDEX]\
      or\
      keyImageLookup [keyValue] [BAND_3_CURRENT_STATUS_INDEX] != keyImageLookup [keyValue] [BAND_3_LAST_STATUS_INDEX] :
      
        keyImageLookup [keyValue] [TEXT_LAST_STATUS_INDEX] = keyImageLookup [keyValue] [TEXT_CURRENT_STATUS_INDEX]
        keyImageLookup [keyValue] [BAND_1_LAST_STATUS_INDEX] = keyImageLookup [keyValue] [BAND_1_CURRENT_STATUS_INDEX]
        keyImageLookup [keyValue] [BAND_2_LAST_STATUS_INDEX] = keyImageLookup [keyValue] [BAND_2_CURRENT_STATUS_INDEX]
        keyImageLookup [keyValue] [BAND_3_LAST_STATUS_INDEX] = keyImageLookup [keyValue] [BAND_3_CURRENT_STATUS_INDEX]
        return GetKeyImageSequence (keyValue)
    else :
        return ''
        
################################################################################
##
## Functions: SetDefaultKeyImage, SetKeyIdleText, SetKeyActiveText, SetKeyNoBand, SetKeyBand1, SetKeyBand2,
##                 SetKeyBand3, SetFlashActive, SetFlashInactive, CheckIfFlashRequired
##
## Parameters: keyValue - integer
##
## Returns:
##
## Globals modified:
##
## Comments: A set of functions for setting and checking the text and band status values. These status values are used
## to create the correct offset for the image to be displayed.
##
## WARNING : Selecting a key band requires that the image has beed defined in Visi Genie.
##
################################################################################

def SetDefaultKeyImage (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyIdleText (keyValue)
    SetKeyNoBand (keyValue)
    return GetKeyImageSequence (keyValue)
    
def SetKeyIdleText (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    keyImageLookup [keyValue] [TEXT_CURRENT_STATUS_INDEX]  = 0
    return GetKeyImageSequence (keyValue)
    
def SetKeyActiveText (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    keyImageLookup [keyValue] [TEXT_CURRENT_STATUS_INDEX]  = 1
    return GetKeyImageSequence (keyValue)

def SetKeyNoBand (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    keyImageLookup [keyValue] [BAND_1_CURRENT_STATUS_INDEX]  = 0
    keyImageLookup [keyValue] [BAND_2_CURRENT_STATUS_INDEX]  = 0
    keyImageLookup [keyValue] [BAND_3_CURRENT_STATUS_INDEX]  = 0
    keyImageLookup [keyValue] [BAND_FLASHING_INDEX]  = 0
    return GetKeyImageSequence (keyValue)
    
def SetKeyBand1 (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyNoBand (keyValue)
    keyImageLookup [keyValue] [BAND_1_CURRENT_STATUS_INDEX]  = 2
    return GetKeyImageSequence (keyValue)

def SetKeyBand2 (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyNoBand (keyValue)
    keyImageLookup [keyValue] [BAND_2_CURRENT_STATUS_INDEX]  = 4
    return GetKeyImageSequence (keyValue)
    
def SetKeyBand3 (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyNoBand (keyValue)
    keyImageLookup [keyValue] [BAND_3_CURRENT_STATUS_INDEX]  = 6
    return GetKeyImageSequence (keyValue)
    
def SetKeyBand1Flashing (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyBand1 (keyValue)
    SetFlashActive (keyValue)
    return GetKeyImageSequence (keyValue)
    
def SetKeyBand2Flashing (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyBand2 (keyValue)
    SetFlashActive (keyValue)
    return GetKeyImageSequence (keyValue)
    
def SetKeyBand3Flashing (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyBand3 (keyValue)
    SetFlashActive (keyValue)
    return GetKeyImageSequence (keyValue)
    
def SetKeyBand1AndBand2Flashing (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyBand1 (keyValue)
    SetFlashActive (keyValue)
    # Set last band status so other flash is band2.
    keyImageLookup [keyValue] [BAND_1_LAST_STATUS_INDEX] = 4
    return GetKeyImageSequence (keyValue)
    
def SetKeyBand1AndBand3Flashing (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyBand1 (keyValue)
    SetFlashActive (keyValue)
    # Set last band status so other flash is band3.
    keyImageLookup [keyValue] [BAND_1_LAST_STATUS_INDEX] = 6
    return GetKeyImageSequence (keyValue)
    
def SetKeyBand2AndBand3Flashing (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    SetKeyBand2 (keyValue)
    SetFlashActive (keyValue)
    # Set last band status so other flash is band3.
    keyImageLookup [keyValue] [BAND_2_LAST_STATUS_INDEX] = 6
    return GetKeyImageSequence (keyValue)
    
def SetFlashActive (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    # Make sure text stays the same during flash by making last text status = current text status.
    keyImageLookup [keyValue] [TEXT_LAST_STATUS_INDEX]  = keyImageLookup [keyValue] [TEXT_CURRENT_STATUS_INDEX]
    # Clear last band status so other flash is no band.
    keyImageLookup [keyValue] [BAND_1_LAST_STATUS_INDEX] = 0
    keyImageLookup [keyValue] [BAND_2_LAST_STATUS_INDEX] = 0
    keyImageLookup [keyValue] [BAND_3_LAST_STATUS_INDEX] = 0
    # Set to flash.
    keyImageLookup [keyValue] [BAND_FLASHING_INDEX]  = 1
    return GetKeyImageSequence (keyValue)
    
def SetFlashInactive (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return ''
    keyImageLookup [keyValue] [BAND_FLASHING_INDEX]  = 0
    return GetKeyImageSequence (keyValue)
    
def CheckIfFlashRequired (keyValue) :
    if keyValue == GD.KEYVALUE_NONE : return False
    return keyImageLookup [keyValue] [BAND_FLASHING_INDEX] != 0
    
################################################################################
##
## Function: SetControlBandStatus (configBitList, keyList = GD.KEYVALUE_NONE, checkIfHigh = True)
##
## Parameters: configBit - integer or tuple - the config bit(s) we are getting status from
##                   keyList - integer or tuple - the key value(s) to set 
##                   checkIfHigh - boolean - True if we want to check for high, False to check for low
##
## Returns:
##
## Globals modified:
##
## Comments: Checks the current status of config bit(s) and updates the band status of the manual keys used to 
## control the config bit(s). The usual use is a green band for on and a red band for off. If the config bit is in override mode then 
## the flash flag for the band will be set. Note: Manual control keys have a dedicated on or off function and so they will have either
## red or green band image as band 1. This is different to zone keys which have green band on band 1 and red band on band 2.
##
################################################################################

def SetControlBandStatus (configBitList, keyList = GD.KEYVALUE_NONE, checkIfHigh = True) :

    # Check if single or multiple keys (single = int, multiple = tuple) and covert to tuple if int.
    configBitList = (configBitList,) if type (configBitList) is int else configBitList
    keyList = (keyList,) if type (keyList) is int else keyList
    
    # Scan through the bits that need the key bands to be updated. If the key list is shorter than the config list 
    # use the no key value. This will occur if no parameter is supplied and the default parameter is used.
    for index in range (0, len (configBitList)) :
        
        # Get the values from lists.
        configBit = configBitList [index]
        key = keyList [index] if len (keyList) == len (configBitList) else GD.KEYVALUE_NONE
        
        # Clear any existing bands.
        SetKeyNoBand (key)
        
        # Is the bit the level that we are testing for? If it is set band on and flash if override active.
        if system.systemControl [configBit].CheckIfBitHigh () == checkIfHigh :
            if system.systemControl [configBit].CheckIfOverrideActive () == True :
                SetKeyBand1Flashing (key)
            else :
                SetKeyBand1 (key)
            
################################################################################
##
## Function: SetZoneSelectBandStatus (zone)
##
## Parameters: zone - integer - the zone of the image to set.
##
## Returns:
##
## Globals modified:
##
## Comments: Checks the current status of a zone  and updates the image band status as required. Band 1 is green to 
## indicate on and band 2 is red to indicate off. If the zone status has changed we will set the flash flag so that we pulse the
## band on and off to indicate to the user that the zone is going to change state. Note we only show the red band band when
## we are actually turning off (flashing). The green band always shows when the zone is on or turning on (flashing).
## If the zone is in override mode we will flash alternate yellow then the state of the override (on=green, red=off).
##
################################################################################

def SetZoneSelectBandStatus (zone) :

    # Zones start at 0, keyvalues start at 1.
    keyValue = zone + 1

    # If  the zone has changed status we will set flash status and check if new state is off or on. We will use the last status flags
    # to hold the 'flash off status' and the normal status flag to hold the 'flash on status'.
    if zones.zoneData [zone].CheckIfZoneStatusChanged () == True :
    
        # If we have an on then set green band for on flash.
        if zones.zoneData [zone].CheckIfZoneOnRequested () == True :
            SetKeyBand1Flashing (keyValue)
            
        # Must be an off so set red band for off flash.
        else :
            SetKeyBand2Flashing (keyValue)
         
     # Not changed. If it is on set green band. If it is off set no band. Clear any existing flash flag.
    elif zones.zoneData [zone].CheckIfZoneOn () == True :
        SetKeyBand1 (keyValue)
        SetFlashInactive (keyValue)
    else :
        SetKeyNoBand (keyValue)
        SetFlashInactive (keyValue) 

    # Check if this zone is an immersion. If it is get control bit from lookup. 
    if keyValue in GD.KEY_GROUP_IMMERSIONS :
        controlBit = GD.KEY_TO_CONTROL_BIT_LOOKUP [keyValue]
        
        # Are we in override? If we are set override flash on. Green/yellow for on and red/yellow for off.
        if system.systemControl [controlBit].CheckIfOverrideActive () == True :
            if system.systemControl [controlBit].CheckIfBitHigh () == True :
                SetKeyBand1AndBand3Flashing (keyValue) 
            else :
                SetKeyBand2AndBand3Flashing (keyValue) 

 ################################################################################
##
## Function: UpdateSelectKeyGroupBand (band_1 = GD.KEYVALUE_NONE, band_2 = GD.KEYVALUE_NONE,
##                                                               bandNone = GD.KEYVALUE_NONE)
##
## Parameters: bandXXX -  integer or tuple - the key value(s) to set green, red or none
##
## Returns:
##
## Globals modified:
##
## Comments: Used to update the bands on a group of select keys. Normally this is used to set a single key band and all
## the other keys in a group to no band for a group of mutually exclusive keys. Note that the key to set a band should be in
## the no band list so that we can use the same list whenever we set a key band in a particular group.
##
################################################################################

def UpdateSelectKeyGroupBand (band_1 = GD.KEYVALUE_NONE, band_2 = GD.KEYVALUE_NONE,
                                                    bandNone = GD.KEYVALUE_NONE) :

    # Check if single or multiple keys (single = int, multiple = tuple) and covert to tuple if int.
    bandNone = (bandNone,) if type (bandNone) is int else bandNone
    band_1 = (band_1,) if type (band_1) is int else band_1
    band_2 = (band_2,) if type (band_2) is int else band_2

    # Do no band first.
    for keyValue in (bandNone) :
        SetKeyNoBand (keyValue)

    for keyValue in (band_1) :
        SetKeyBand1 (keyValue)
        
    for keyValue in (band_2) :
        SetKeyBand2 (keyValue)
        
################################################################################
##
## Function: UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_NONE, textIdle = GD.KEYVALUE_NONE)
##
## Parameters: textXXX - integer or tuple - the key value(s) to set active or idle
##
## Returns:
##
## Globals modified:
##
## Comments: Used to update the text on a group of select keys. Normally this is used to set a single key active and all
## the other keys idle for a group of mutually exclusive keys. Note that the key to make active should be in
## the idle list so that we can use the same list whenever we make a key active in a particular group.
##
################################################################################

def UpdateSelectKeyGroupText (textActive = GD.KEYVALUE_NONE, textIdle = GD.KEYVALUE_NONE) :

    # Check if single or multiple keys (single = int, multiple = tuple) and covert to tuple if int.
    textIdle = (textIdle,) if type (textIdle) is int else textIdle
    textActive = (textActive,) if type (textActive) is int else textActive
    
    # Do idle first.
    for key in (textIdle) :
        SetKeyIdleText (key)
    
    for key in (textActive) :
        SetKeyActiveText (key)

################################################################################
##
## Function: InitialiseKeyDataLookups ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: Initialise our keyboard lookup tables. 
##
################################################################################

def InitialiseKeyDataLookups () :
        
    # Table of parameters for every mode / visikey combination. These are the keyvalue, the base address of the key's images
    # and the offset to the key image for this key value.
    keyParameters = (
    
        # mode:
        {
         GD.MODE_RAD_WAITING_ZONE_SELECT : 
            (# (keyvalue, base address, offset)
                (GD.KEYVALUE_RAD_BED_1, 1, 1),
                (GD.KEYVALUE_RAD_BED_2, 2, 1),                                               
                (GD.KEYVALUE_RAD_BED_3, 3, 1),                
                (GD.KEYVALUE_RAD_BED_4, 4, 1),            
                (GD.KEYVALUE_NOT_USED_B5, 5, 0),      
                (GD.KEYVALUE_RAD_BED_5, 6, 1),             
                (GD.KEYVALUE_RAD_BATH_1, 7, 1),                          
                (GD.KEYVALUE_RAD_BATH_2, 8, 1),        
                (GD.KEYVALUE_RAD_BATH_3_4, 9, 1),    
                (GD.KEYVALUE_UFH, 10, 4),                  
                (GD.KEYVALUE_RAD_HALL_UP, 11, 1),                
                (GD.KEYVALUE_RAD_KITCHEN, 12, 1),                              
                (GD.KEYVALUE_RAD_DINING, 13, 1),                                
                (GD.KEYVALUE_RAD_LIBRARY, 14, 1),                            
                (GD.KEYVALUE_SYSTEM, 15, 5),            
                (0, 16, 1),                                         
                (GD.KEYVALUE_RAD_CLOAK, 17, 1),                                      
                (GD.KEYVALUE_RAD_SITTING, 18, 1),                                         
                (0, 19, 1),                                           
                (GD.KEYVALUE_FINISHED, 20, 2)         
            ),
         
         GD.MODE_UFH_WAITING_ZONE_SELECT : 
            (
                (GD.KEYVALUE_UFH_BED_1, 1, 7),    
                (GD.KEYVALUE_UFH_BED_2, 2, 7),    
                (GD.KEYVALUE_UFH_BED_3, 3, 7),    
                (GD.KEYVALUE_UFH_BED_4, 4, 7),    
                (GD.KEYVALUE_RAD, 5, 3),              
                (GD.KEYVALUE_UFH_BED_5, 6, 7),    
                (GD.KEYVALUE_UFH_BATH_1, 7, 7),    
                (GD.KEYVALUE_UFH_BATH_2, 8, 7),    
                (GD.KEYVALUE_UFH_BATH_3_4, 9, 7),    
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),            
                (GD.KEYVALUE_UFH_HALL_UP, 11, 7),  
                (GD.KEYVALUE_UFH_KITCHEN, 12, 7),  
                (GD.KEYVALUE_UFH_DINING, 13, 7),  
                (GD.KEYVALUE_UFH_LIBRARY, 14, 7),  
                (GD.KEYVALUE_SYSTEM, 15, 5),              
                (GD.KEYVALUE_UFH_HALL_DOWN, 16, 7),  
                (GD.KEYVALUE_UFH_CLOAK, 17, 7),  
                (GD.KEYVALUE_UFH_SITTING, 18, 7),  
                (GD.KEYVALUE_UFH_HALL_SITTINGX, 19, 7),  
                (GD.KEYVALUE_FINISHED, 20, 2)              
            ),
        
         GD.MODE_RAD_ZONE_SELECT : 
            (
                (GD.KEYVALUE_RAD_BED_1, 1, 1),
                (GD.KEYVALUE_RAD_BED_2, 2, 1),
                (GD.KEYVALUE_RAD_BED_3, 3, 1),
                (GD.KEYVALUE_RAD_BED_4, 4, 1),
                (GD.KEYVALUE_PROGRAM, 5, 2),
                (GD.KEYVALUE_RAD_BED_5, 6, 1),
                (GD.KEYVALUE_RAD_BATH_1, 7, 1),
                (GD.KEYVALUE_RAD_BATH_2, 8, 1),
                (GD.KEYVALUE_RAD_BATH_3_4, 9, 1),
                (GD.KEYVALUE_BOOST, 10, -1), # Boost key has variable text - displayed elsewhere.
                (GD.KEYVALUE_RAD_HALL_UP, 11, 1),
                (GD.KEYVALUE_RAD_KITCHEN, 12, 1),
                (GD.KEYVALUE_RAD_DINING, 13, 1),
                (GD.KEYVALUE_RAD_LIBRARY, 14, 1),
                (GD.KEYVALUE_CAN_RES, 15, -1), # Cancel / Reset key has variable text - displayed elsewhere.
                (0, 16, 1),
                (GD.KEYVALUE_RAD_CLOAK, 17, 1),
                (GD.KEYVALUE_RAD_SITTING, 18, 1),
                (0, 19, 1),
                (GD.KEYVALUE_RAD_SELECT_EXIT, 20, 1)        
            ),
            
         GD.MODE_UFH_ZONE_SELECT : 
            (
                (GD.KEYVALUE_UFH_BED_1, 1, 7),
                (GD.KEYVALUE_UFH_BED_2, 2, 7),
                (GD.KEYVALUE_UFH_BED_3, 3, 7),
                (GD.KEYVALUE_UFH_BED_4, 4, 7),
                (GD.KEYVALUE_PROGRAM, 5, 2),
                (GD.KEYVALUE_UFH_BED_5, 6, 7),
                (GD.KEYVALUE_UFH_BATH_1, 7, 7),
                (GD.KEYVALUE_UFH_BATH_2, 8, 7),
                (GD.KEYVALUE_UFH_BATH_3_4, 9, 7),
                (GD.KEYVALUE_BOOST, 10, -1), # Boost key has variable text - displayed elsewhere.
                (GD.KEYVALUE_UFH_HALL_UP, 11, 7),
                (GD.KEYVALUE_UFH_KITCHEN, 12, 7),
                (GD.KEYVALUE_UFH_DINING, 13, 7),
                (GD.KEYVALUE_UFH_LIBRARY, 14, 7),
                (GD.KEYVALUE_CAN_RES, 15, -1), # Cancel / Reset key has variable text - displayed elsewhere.
                (GD.KEYVALUE_UFH_HALL_DOWN, 16, 7),
                (GD.KEYVALUE_UFH_CLOAK, 17, 7),
                (GD.KEYVALUE_UFH_SITTING, 18, 7),
                (GD.KEYVALUE_UFH_HALL_SITTINGX, 19, 7),
                (GD.KEYVALUE_UFH_SELECT_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_TIME : 
            (
                (GD.KEYVALUE_NUMERIC_1, 1, 13),
                (GD.KEYVALUE_NUMERIC_2, 2, 13),
                (GD.KEYVALUE_NUMERIC_3, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV_PROGRAM_ENTRY, 5, 1),
                (GD.KEYVALUE_NUMERIC_4, 6, 13),
                (GD.KEYVALUE_NUMERIC_5, 7, 13),
                (GD.KEYVALUE_NUMERIC_6, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT_PROGRAM_ENTRY, 10, 1),
                (GD.KEYVALUE_NUMERIC_7, 11, 13),
                (GD.KEYVALUE_NUMERIC_8, 12, 13),
                (GD.KEYVALUE_NUMERIC_9, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (GD.KEYVALUE_NUMERIC_0, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, -1), # Auto / Manual key has variable text - displayed elsewhere.
                (GD.KEYVALUE_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_ON_AT : 
            (
                (GD.KEYVALUE_NUMERIC_1, 1, 13),
                (GD.KEYVALUE_NUMERIC_2, 2, 13),
                (GD.KEYVALUE_NUMERIC_3, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV_PROGRAM_ENTRY, 5, 1),
                (GD.KEYVALUE_NUMERIC_4, 6, 13),
                (GD.KEYVALUE_NUMERIC_5, 7, 13),
                (GD.KEYVALUE_NUMERIC_6, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT_PROGRAM_ENTRY, 10, 1),
                (GD.KEYVALUE_NUMERIC_7, 11, 13),
                (GD.KEYVALUE_NUMERIC_8, 12, 13),
                (GD.KEYVALUE_NUMERIC_9, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (GD.KEYVALUE_NUMERIC_0, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, -1), # Auto / Manual key has variable text - displayed elsewhere.
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_OFF_AT : 
            (
                (GD.KEYVALUE_NUMERIC_1, 1, 13),
                (GD.KEYVALUE_NUMERIC_2, 2, 13),
                (GD.KEYVALUE_NUMERIC_3, 3, 13),
                (GD.KEYVALUE_ON_AT, 4, 13),
                (GD.KEYVALUE_PREV_PROGRAM_ENTRY, 5, 1),
                (GD.KEYVALUE_NUMERIC_4, 6, 13),
                (GD.KEYVALUE_NUMERIC_5, 7, 13),
                (GD.KEYVALUE_NUMERIC_6, 8, 13),
                (GD.KEYVALUE_OFF_AT, 9, 13),
                (GD.KEYVALUE_NEXT_PROGRAM_ENTRY, 10, 1),
                (GD.KEYVALUE_NUMERIC_7, 11, 13),
                (GD.KEYVALUE_NUMERIC_8, 12, 13),
                (GD.KEYVALUE_NUMERIC_9, 13, 13),
                (GD.KEYVALUE_DAY, 14, 13),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 13),
                (GD.KEYVALUE_NUMERIC_0, 17, 13),
                (GD.KEYVALUE_SAVE, 18, 13),
                (GD.KEYVALUE_AUTO_MANUAL, 19, -1), # Auto / Manual key has variable text - displayed elsewhere.
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_DAY : 
            (
                (GD.KEYVALUE_DAY_MONDAY, 1, 14),
                (GD.KEYVALUE_DAY_TUESDAY, 2, 14),
                (GD.KEYVALUE_DAY_WEDNESDAY, 3, 14),
                (GD.KEYVALUE_ON_AT, 4, 14),
                (GD.KEYVALUE_PREV_PROGRAM_ENTRY, 5, 1),
                (GD.KEYVALUE_DAY_THURSDAY, 6, 14),
                (GD.KEYVALUE_DAY_FRIDAY, 7, 14),
                (GD.KEYVALUE_DAY_MON_FRI, 8, 14),
                (GD.KEYVALUE_OFF_AT, 9, 14),
                (GD.KEYVALUE_NEXT_PROGRAM_ENTRY, 10, 1),
                (GD.KEYVALUE_DAY_SATURDAY, 11, 14),
                (GD.KEYVALUE_DAY_SUNDAY, 12, 14),
                (GD.KEYVALUE_DAY_SAT_SUN, 13, 14),
                (GD.KEYVALUE_DAY, 14, 14),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 14),
                (GD.KEYVALUE_DAY_EVERY, 17, 14),
                (GD.KEYVALUE_SAVE, 18, 14),
                (GD.KEYVALUE_ENABLE_DISABLE, 19, -1),  # Enable / Disable key has variable text - displayed elsewhere.
                (GD.KEYVALUE_EXIT, 20, 1)        
            ),
         
         GD.MODE_PROG_DAYS_ON : 
            (
                (GD.KEYVALUE_DAY_MONDAY, 1, 14),
                (GD.KEYVALUE_DAY_TUESDAY, 2, 14),
                (GD.KEYVALUE_DAY_WEDNESDAY, 3, 14),
                (GD.KEYVALUE_ON_AT, 4, 14),
                (GD.KEYVALUE_PREV_PROGRAM_ENTRY, 5, 1),
                (GD.KEYVALUE_DAY_THURSDAY, 6, 14),
                (GD.KEYVALUE_DAY_FRIDAY, 7, 14),
                (GD.KEYVALUE_DAY_MON_FRI, 8, 14),
                (GD.KEYVALUE_OFF_AT, 9, 14),
                (GD.KEYVALUE_NEXT_PROGRAM_ENTRY, 10, 1),
                (GD.KEYVALUE_DAY_SATURDAY, 11, 14),
                (GD.KEYVALUE_DAY_SUNDAY, 12, 14),
                (GD.KEYVALUE_DAY_SAT_SUN, 13, 14),
                (GD.KEYVALUE_DAY, 14, 14),
                (GD.KEYVALUE_NEW, 15, 1),
                (GD.KEYVALUE_CLEAR, 16, 14),
                (GD.KEYVALUE_DAY_EVERY, 17, 14),
                (GD.KEYVALUE_SAVE, 18, 14),
                (GD.KEYVALUE_ENABLE_DISABLE, 19, -1),  # Enable / Disable key has variable text - displayed elsewhere.
                (GD.KEYVALUE_EDIT_EXIT, 20, 1)        
            ),
         
         GD.MODE_OFF_MODE_SELECT : 
            (
                (GD.KEYVALUE_SYSTEM_OFF, 21, 1),
                (GD.KEYVALUE_SYSTEM_OFF, 21, 1),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22, 0),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22, 0),
                (GD.KEYVALUE_NOT_USED_B5, 5, 0),
                (GD.KEYVALUE_AUTO_MODE, 23, 1),
                (GD.KEYVALUE_AUTO_MODE, 23, 1),
                (GD.KEYVALUE_NOT_USED_B24, 24, 0),
                (GD.KEYVALUE_NOT_USED_B24, 24, 0),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_MANUAL_MODE, 25, 1),
                (GD.KEYVALUE_MANUAL_MODE, 25, 1),
                (GD.KEYVALUE_NOT_USED_B26, 26, 0),
                (GD.KEYVALUE_NOT_USED_B26, 26, 0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_HOLIDAY_MODE, 27, 1),
                (GD.KEYVALUE_HOLIDAY_MODE, 27, 1),
                (GD.KEYVALUE_NOT_USED_B28, 28, 0),
                (GD.KEYVALUE_NOT_USED_B28, 28, 0),
                (GD.KEYVALUE_FINISHED, 20, 2)
            ),

         GD.MODE_AUTO_MODE_SELECT : 
            (
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22, 0),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22, 0),
                (GD.KEYVALUE_RAD, 5, 3),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_AUTO_OPTIONS, 24, 0),
                (GD.KEYVALUE_AUTO_OPTIONS, 24, 0),
                (GD.KEYVALUE_UFH, 10,4),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_FINISHED, 20,2)
            ),

         GD.MODE_MANUAL_MODE_SELECT : 
            (
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22, 0),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22, 0),
                (GD.KEYVALUE_RAD, 5, 3),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_UFH, 10,4),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_MANUAL_OPTIONS, 26, 0),
                (GD.KEYVALUE_MANUAL_OPTIONS, 26, 0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_FINISHED, 20,2)
            ),

         GD.MODE_HOLIDAY_MODE_SELECT : 
            (
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OFF, 21,1),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22, 0),
                (GD.KEYVALUE_SYSTEM_OPTIONS, 22, 0),
                (GD.KEYVALUE_RAD, 5, 3),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_AUTO_MODE, 23,1),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_UFH, 10,4),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_MANUAL_MODE, 25,1),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_HOLIDAY_MODE, 27,1),
                (GD.KEYVALUE_HOLIDAY_OPTIONS, 28, 0),
                (GD.KEYVALUE_HOLIDAY_OPTIONS, 28, 0),
                (GD.KEYVALUE_FINISHED, 20,2)
            ),

         GD.MODE_SYSTEM_OPTIONS : 
            (
                (GD.KEYVALUE_IMMERSION_TIMES, 21, 0),
                (GD.KEYVALUE_IMMERSION_TIMES, 21, 0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_WINTER_PERIOD, 23, 0),
                (GD.KEYVALUE_WINTER_PERIOD, 23, 0),
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
                (GD.KEYVALUE_RETURN_TO_SYSTEM_EXIT, 20,1)
            ),

         GD.MODE_IMMERSION_WAITING_SELECT : 
            (
                (GD.KEYVALUE_IMM_1_TIME, 21, 37),
                (GD.KEYVALUE_IMM_1_TIME, 21, 37),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_IMM_2_TIME, 23, 37),
                (GD.KEYVALUE_IMM_2_TIME, 23, 37),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_IMM_3_TIME, 25, 18),
                (GD.KEYVALUE_IMM_3_TIME, 25, 18),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_IMM_4_TIME, 27, 13),
                (GD.KEYVALUE_IMM_4_TIME, 27, 13),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_RETURN_TO_SYSTEM_EXIT, 20,1)
            ),

         GD.MODE_IMMERSION_SELECT : 
            (
                (GD.KEYVALUE_IMM_1_TIME, 21, 37),
                (GD.KEYVALUE_IMM_1_TIME, 21, 37),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_PROGRAM, 5, 2),
                (GD.KEYVALUE_IMM_2_TIME, 23, 37),
                (GD.KEYVALUE_IMM_2_TIME, 23, 37),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_BOOST, 10, -1), # Boost key has variable text - displayed elsewhere.
                (GD.KEYVALUE_IMM_3_TIME, 25, 18),
                (GD.KEYVALUE_IMM_3_TIME, 25, 18),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_CAN_RES, 15, -1), # Cancel / Reset key has variable text - displayed elsewhere.
                (GD.KEYVALUE_IMM_4_TIME, 27, 13),
                (GD.KEYVALUE_IMM_4_TIME, 27, 13),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_RETURN_TO_SYSTEM_OPTIONS_EXIT, 20,1)
            ),

         GD.MODE_AUTO_OPTIONS : 
            (
                (GD.KEYVALUE_HEATING_SOURCES, 21, 0),
                (GD.KEYVALUE_HEATING_SOURCES, 21, 0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B22, 22,0),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_WINTER_PERIOD, 23, 0),
                (GD.KEYVALUE_T1_SOURCES, 23, 0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B24, 24,0),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_T2_SOURCES, 25, 0),
                (GD.KEYVALUE_T2_SOURCES, 25, 0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_BOILER_PRIORITY, 27, 0),
                (GD.KEYVALUE_BOILER_PRIORITY, 27, 0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_RETURN_TO_SYSTEM_EXIT, 20,1)
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
                (GD.KEYVALUE_RETURN_TO_SYSTEM_EXIT, 20,1)
            ),

         GD.MODE_MANUAL_OPTIONS : 
            (
                (GD.KEYVALUE_T1_TO_HEAT, 21, 5),
                (GD.KEYVALUE_T1_TO_HEAT, 21, 5),
                (GD.KEYVALUE_OIL_TO_T1, 22, 1),
                (GD.KEYVALUE_OIL_TO_T1, 22, 1),
                (GD.KEYVALUE_NOT_USED_B5, 5, 0),
                (GD.KEYVALUE_T2_TO_HEAT, 23, 5),
                (GD.KEYVALUE_T2_TO_HEAT, 23, 5),
                (GD.KEYVALUE_OIL_TO_T2, 24, 1),
                (GD.KEYVALUE_OIL_TO_T2, 24, 1),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_OIL_TO_HEAT, 25, 5),
                (GD.KEYVALUE_OIL_TO_HEAT, 25, 5),
                (GD.KEYVALUE_OIL_OFF, 26, 1),
                (GD.KEYVALUE_OIL_OFF, 26, 1),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_MANUAL_OVERRIDE, 27, 9),
                (GD.KEYVALUE_MANUAL_OVERRIDE, 27, 9),
                (GD.KEYVALUE_DISPLAY_STATUS, 28, 5),
                (GD.KEYVALUE_DISPLAY_STATUS, 28, 5),
                (GD.KEYVALUE_RETURN_TO_SYSTEM_EXIT, 20,1)
            ),

         GD.MODE_MANUAL_OPTIONS_DISABLED : 
            (
                (GD.KEYVALUE_T1_TO_HEAT, 21, 5),
                (GD.KEYVALUE_T1_TO_HEAT, 21, 5),
                (GD.KEYVALUE_OIL_TO_T1, 22, 1),
                (GD.KEYVALUE_OIL_TO_T1, 22, 1),
                (GD.KEYVALUE_NOT_USED_B5, 5, 0),
                (GD.KEYVALUE_T2_TO_HEAT, 23, 5),
                (GD.KEYVALUE_T2_TO_HEAT, 23, 5),
                (GD.KEYVALUE_OIL_TO_T2, 24, 1),
                (GD.KEYVALUE_OIL_TO_T2, 24, 1),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_OIL_TO_HEAT, 25, 5),
                (GD.KEYVALUE_OIL_TO_HEAT, 25, 5),
                (GD.KEYVALUE_OIL_OFF, 26, 1),
                (GD.KEYVALUE_OIL_OFF, 26, 1),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_MANUAL_OVERRIDE, 27, 9),
                (GD.KEYVALUE_MANUAL_OVERRIDE, 27, 9),
                (GD.KEYVALUE_DISPLAY_STATUS, 28, 5),
                (GD.KEYVALUE_DISPLAY_STATUS, 28, 5),
                (GD.KEYVALUE_RETURN_TO_SYSTEM_EXIT, 20,1)
            ),

         GD.MODE_DISPLAY_STATUS : 
            (
                (GD.KEYVALUE_IMM_1_STATUS, 1, 15),
                (GD.KEYVALUE_WOODBURNER_STATUS, 2, 15),
                (GD.KEYVALUE_RADS_STATUS, 3, 15),
                (GD.KEYVALUE_BATH_1_STATUS, 4, 15),
                (GD.KEYVALUE_PREV_STATUS_ENTRY, 5, -1),      # Previous is displayed elsewhere depending on number of status
                (GD.KEYVALUE_IMM_2_STATUS, 6, 15),
                (GD.KEYVALUE_BOILER_STATUS, 7, 15),
                (GD.KEYVALUE_UFH_STATUS, 8, 15),
                (GD.KEYVALUE_BATH_2_STATUS, 9, 15),
                (GD.KEYVALUE_NEXT_STATUS_ENTRY, 10, -1),      # Next is displayed elsewhere depending on number of status
                (GD.KEYVALUE_IMM_3_STATUS, 11, 15),
                (GD.KEYVALUE_TANK_1_STATUS, 12, 15),
                (GD.KEYVALUE_HW_STATUS, 13, 15),
                (GD.KEYVALUE_BATH_3_4_STATUS, 14, 15),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_IMM_4_STATUS, 16, 15),
                (GD.KEYVALUE_TANK_2_STATUS, 17, 15),
                (GD.KEYVALUE_SYSTEM_STATUS, 18, 15),
                (GD.KEYVALUE_NOT_USED_B19, 19,0),
                (GD.KEYVALUE_MANUAL_CONTROL_MAIN_MENU_EXIT, 20,1)
            ),

         GD.MODE_MANUAL_OVERRIDE_MAIN_MENU : 
            (
                (GD.KEYVALUE_WOODBURNER_CONTROL, 21, 33),
                (GD.KEYVALUE_WOODBURNER_CONTROL, 21, 33),
                (GD.KEYVALUE_IMMERSION_CONTROL, 22, 29),
                (GD.KEYVALUE_IMMERSION_CONTROL, 22, 29),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_HEATING_CONTROL, 23, 33),
                (GD.KEYVALUE_HEATING_CONTROL, 23, 33),
                (GD.KEYVALUE_TANK_1_CONTROL, 24, 29),
                (GD.KEYVALUE_TANK_1_CONTROL, 24, 29),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_BOILER_CONTROL, 25, 14),
                (GD.KEYVALUE_BOILER_CONTROL, 25, 14),
                (GD.KEYVALUE_TANK_2_CONTROL, 26, 9),
                (GD.KEYVALUE_TANK_2_CONTROL, 26, 9),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_MANUAL_CONTROL_MAIN_MENU_EXIT, 20,1)
            ),

         GD.MODE_IMMERSION_MANUAL_CONTROL : 
            (
                (GD.KEYVALUE_IMM_1_ON, 21,9),
                (GD.KEYVALUE_IMM_1_ON, 21,9),
                (GD.KEYVALUE_IMM_1_OFF, 22, 5),
                (GD.KEYVALUE_IMM_1_OFF, 22, 5),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_IMM_2_ON, 23,9),
                (GD.KEYVALUE_IMM_2_ON, 23,9),
                (GD.KEYVALUE_IMM_2_OFF, 24, 5),
                (GD.KEYVALUE_IMM_2_OFF, 24, 5),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_IMM_3_ON, 25,9),
                (GD.KEYVALUE_IMM_3_ON, 25,9),
                (GD.KEYVALUE_IMM_3_OFF, 26, 5),
                (GD.KEYVALUE_IMM_3_OFF, 26, 5),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_IMM_4_ON, 27,5),
                (GD.KEYVALUE_IMM_4_ON, 27,5),
                (GD.KEYVALUE_IMM_4_OFF, 28, 1),
                (GD.KEYVALUE_IMM_4_OFF, 28, 1),
                (GD.KEYVALUE_MANUAL_CONTROL_OPTION_EXIT, 20,1)
            ),

         GD.MODE_WOODBURNER_MANUAL_CONTROL : 
            (
                (GD.KEYVALUE_WB_PUMP_1_ON, 21, 13),
                (GD.KEYVALUE_WB_PUMP_1_ON, 21,13),
                (GD.KEYVALUE_WB_PUMP_1_OFF, 22, 9),
                (GD.KEYVALUE_WB_PUMP_1_OFF, 22, 9),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_WB_PUMP_2_ON, 23, 13),
                (GD.KEYVALUE_WB_PUMP_2_ON, 23, 13),
                (GD.KEYVALUE_WB_PUMP_2_OFF, 24, 9),
                (GD.KEYVALUE_WB_PUMP_2_OFF, 24, 9),
                (GD.KEYVALUE_NOT_USED_B10, 10, 0),
                (GD.KEYVALUE_WB_ALARM, 25, 13),
                (GD.KEYVALUE_WB_ALARM, 25, 13),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B26, 26,0),
                (GD.KEYVALUE_NOT_USED_B15, 15, 0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B27, 27,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_NOT_USED_B28, 28,0),
                (GD.KEYVALUE_MANUAL_CONTROL_OPTION_EXIT, 20,1)
            ),
            
         GD.MODE_TANK_1_MANUAL_CONTROL : 
            (
                (GD.KEYVALUE_TANK_1_PUMP_ON, 21, 17),
                (GD.KEYVALUE_TANK_1_PUMP_ON, 21, 17),
                (GD.KEYVALUE_TANK_1_PUMP_OFF, 22, 13),
                (GD.KEYVALUE_TANK_1_PUMP_OFF, 22, 13),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_V1_EXT_TO_T1, 23, 17),
                (GD.KEYVALUE_V1_EXT_TO_T1, 23, 17),
                (GD.KEYVALUE_V1_EXT_TO_HEATING, 24, 13),
                (GD.KEYVALUE_V1_EXT_TO_HEATING, 24, 13),
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
                (GD.KEYVALUE_MANUAL_CONTROL_OPTION_EXIT, 20,1)
            ),
            
         GD.MODE_TANK_2_MANUAL_CONTROL : 
            (
                (GD.KEYVALUE_TANK_2_PUMP_ON, 21, 21),
                (GD.KEYVALUE_TANK_2_PUMP_ON, 21,21),
                (GD.KEYVALUE_TANK_2_PUMP_OFF, 22, 17),
                (GD.KEYVALUE_TANK_2_PUMP_OFF, 22, 17),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_V2_T2_TO_INT, 23, 21),
                (GD.KEYVALUE_V2_T2_TO_INT, 23, 21),
                (GD.KEYVALUE_V2_T2_RECYCLE, 24, 17),
                (GD.KEYVALUE_V2_T2_RECYCLE, 24, 17),
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
                (GD.KEYVALUE_MANUAL_CONTROL_OPTION_EXIT, 20,1)
            ),
            
         GD.MODE_BOILER_MANUAL_CONTROL : 
            (
                (GD.KEYVALUE_BOILER_ON, 21, 25),
                (GD.KEYVALUE_BOILER_ON, 21, 25),
                (GD.KEYVALUE_BOILER_OFF, 22, 21),
                (GD.KEYVALUE_BOILER_OFF, 22, 21),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_V3_BOILER_TO_T2, 23, 25),
                (GD.KEYVALUE_V3_BOILER_TO_T2, 23, 25),
                (GD.KEYVALUE_V3_BOILER_TO_INT, 24, 21),
                (GD.KEYVALUE_V3_BOILER_TO_INT, 24, 21),
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
                (GD.KEYVALUE_MANUAL_CONTROL_OPTION_EXIT, 20,1)
            ),
            
         GD.MODE_HEATING_MANUAL_CONTROL : 
            (
                (GD.KEYVALUE_RAD_PUMP_ON, 21, 29),
                (GD.KEYVALUE_RAD_PUMP_ON, 21, 29),
                (GD.KEYVALUE_RAD_PUMP_OFF, 22, 25),
                (GD.KEYVALUE_RAD_PUMP_OFF, 22, 25),
                (GD.KEYVALUE_NOT_USED_B5, 5,0),
                (GD.KEYVALUE_UFH_PUMP_ON, 23, 29),
                (GD.KEYVALUE_UFH_PUMP_ON, 23, 29),
                (GD.KEYVALUE_UFH_PUMP_OFF, 24, 25),
                (GD.KEYVALUE_UFH_PUMP_OFF, 24, 25),
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
                (GD.KEYVALUE_MANUAL_CONTROL_OPTION_EXIT, 20,1)
            )
        }
    )
    # Scan through each mode in our parameters table. For each mode we will create a list of the keyvalues for each
    # visi key. This will allow us to look up the keyvalue for each mode / visi key combination. For each keyvalue we will also
    # create a list holding the status of the image for each keyvalue. (idle/active, band1/band2/band3, flashing band)
    for mode in keyParameters :
        # Start list for this mode with the unused visi key 0
        keyValueLookup [mode] = [0]
        
        # Scan through each visi key used in this mode to get matching keyvalue for the visi key.
        for index in range (0, 20) :
            keyValue, baseAddress, offset = keyParameters [mode] [index]
            # Put each keyvalue in list -  mode : [keyValue1, keyValue2, etc]
            keyValueLookup [mode].append (keyValue)
            # Now put addresses and status in 2nd list -  keyValue : [baseAddress, offset, activeStatus, band1Status, band2Status,
            # lastActiveStatus, lastBand1Status, lastBand2Status, flashing, override].
            # Note duplicates will simply overwrite so we will only have one entry per keyvalue.
            keyImageLookup [keyValue] = [baseAddress, offset, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            
    # Add special keys to image list - wakeup has no image to display.
    keyImageLookup [GD.KEYVALUE_WAKEUP] = [0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            
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



InitialiseKeyDataLookups ()


