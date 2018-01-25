
################################################################################
##
## Function: CheckForTimedGateOperation (timeNow)
##
## Parameters: timeNow - time structure - the current time
##
## Returns:
##
## Globals modified:
##
## Comments: We call this function every minute to check for a timed open or close of the gates. We have a file of
## open and close times 'gatetimes.txt. Each line of the file has an open and close time and the days to operate on.
## Note: the lines must be arranged in time order. If no limes are present in the file no operation will take place.
## The 1st line of the file is used to indicate if timer operation is ON or OFF and this is set via the TIMED ON/OFF
## commands.
##   
################################################################################

def CheckForTimedGateOperation (timeNow) :

    # Start with no  action.
    action = 'NO ACTION'
     
    # Get gatetimes.txt into a list. If there are no lines the list will be empty.
    f = open ('/home/pi/Testing/gatetimes.txt', 'r')
    gateProgrammedTimes = f.readlines ()
    f.close ()

    # Exit if there are no open and close times or indicator is NOT 'ON'. The 1st line is the on or off indicator.
    if len (gateProgrammedTimes) < 2 or gateProgrammedTimes [0].upper ().find ('ON') < 0 :
        return action
        
    # Remove on off indictor from list
    del gateProgrammedTimes [0]
    
    # Create a lookup for each day letter, Monday = index 0, same as tm_wday. 
    dayLetter = ('M', 'T', 'W', 'T', 'F', 'S', 'S')

    # Work through each line.
    for gateOnOffTime in gateProgrammedTimes :

        # Get all the fields for this programmed on-off time into a list.
        onOffTime = gateOnOffTime.split ()
        
        # Make sure the time and day fields are the correct length first. Exit if any error.
        if len (onOffTime [1]) != 5 or len (onOffTime [3]) != 5 or len (onOffTime [4]) != 7 :
            return action
            
        # Have we got a day match? Convert any lower case letters in gatetimes days to upper case.
        if dayLetter [timeNow.tm_wday] == onOffTime [4][timeNow.tm_wday].upper () :
            
            # Convert the open, close and current time to tuples so we can compare them.
            # Do it as strings so we will not get errors if the file had invalid time entries.
            gateOpenTime = (onOffTime [1][0:2], onOffTime [1][3:5])
            gateCloseTime = (onOffTime [3][0:2], onOffTime [3][3:5])
            currentTime = (str (timeNow.tm_hour).zfill (2), str (timeNow.tm_min).zfill (2))
            
            # Have we reached the open time for this entry?
            if currentTime >= gateOpenTime :
                
                # Have we reached the close time for this entry?
                if currentTime >= gateCloseTime :
                    # We wil flag to close the gates. A later line in gatetimes.txt may override this to open.
                    action = 'CLOSE GATES'

                # Must be in open time.
                else:
                    action = 'OPEN GATES'
                    
    # Tell caller what to do.
    return action
    
