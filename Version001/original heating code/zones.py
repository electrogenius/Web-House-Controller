print 'Loaded zones module'
import bisect
import time
import GD
import string
import display
import system

#import prog

# Index to fields of on off times and days in a line of the following structure
# On HH:MM Off HH:MM MTWTFSS
#   0     1       2      3           4

ON_TIME_INDEX = 1
OFF_TIME_INDEX = 3
DAYS_INDEX = 4

# Index to hour and minute parts of time field HH:MM.
#                                                                       0   3
HOUR_INDEX = 0
MINUTE_INDEX = 3

################################################################################
#
# Function: CreateFileName (zone)
#
# Parameters: zone - integer - the zone we want a filename for
#
# Returns: string - the filename
#
# Globals modified:
#
# Comments: 
#
################################################################################

def CreateFileName (zone) :

    # Start filename according to zone in RAD, UFH or SYS range.
    if zone < 14 :
        zoneFileName = 'Rad '
    elif zone < 30 :
        zoneFileName = 'Ufh '
    else :
        zoneFileName = 'Sys '

    # Now create the full filename.
    zoneFileName = zoneFileName + zoneData[zone].GetZoneName() + '.txt'

    return zoneFileName

################################################################################
#
# Class: daysField
#
# Parameters: 
#
# Methods:
#
# Globals modified:
#
# Comments: 
#
################################################################################

class daysField :

    daysLookup = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    noDaysLookup = ['_', '_', '_', '_', '_', '_', '_']
    # Create a lookup table for the range of days for each day code.
    dayRange=((0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (0,5), (5,7), (0,7))

    def __init__ (self, days) :
        self.days = list (days)

    def GetDaysEntry (self) :
        return "".join (self.days)

    def __ModifyDays (self, start, finish) :
        # If all the days in range are not set then set them else unset them
        if self.days[start:finish] == self.noDaysLookup[start:finish] :
            self.days[start:finish] = self.daysLookup[start:finish]
        else :
            self.days[start:finish] = self.noDaysLookup[start:finish]

    def SetDay (self, day) :
        # Check for disable/enable 1st.
        if day == GD.DAYS_DISABLED:
            for index in range(0, len (self.days)) :
                self.days[index] = self.days[index].swapcase ()
        # Normal day operation so make sure day code is valid.
        elif day in range (0,10) :
            self.__ModifyDays (self.dayRange[day][0], self.dayRange[day][1],)

    def ClearDaysEntry (self) :
        self.days[:] = self.noDaysLookup[:]

    def CheckIfDayDisabled (self) :
        for letter in self.days :
            # If we find a lowercase letter we are disabled so return true.
            if letter in ('m', 't', 'w', 'f', 's') :
                return True
        # Get here if not disabled
        return False

################################################################################
#
# Class: timesField
#
# Parameters: 
#
# Methods:
#
# Globals modified:
#
# Comments: 
#
################################################################################

class timesField :

    def __init__ (self, time) :
        # Initialise a list with the current programmed time, discarding the colon between the hour and minute.
        self.time = list (time[0:2] + time[3:5])
        # Keep a copy so if we abort an edit we can restore the original
        self.timeCopy = self.time
        # Index to the active digit when editing. Start at tens of hours position.
        self.digitIndex = 0

    def RecoverTime (self) :
        self.time = self.timeCopy
        self.digitIndex = 0

    def GetEditTime (self) :
        # Convert list back to string. We need to put the colon back between hour and minute.
        return self.time[0] + self.time[1] + ':' + self.time[2] + self.time[3]

    def GetDigitIndex (self) :
        return self.digitIndex

    def ClearTimeEntry (self) :
        self.time = ['~','~','~','~']
        self.digitIndex = 0

    def SetDigit (self, digit) :
        # Try and set a digit in a time field. If we fail return zero else return the previous character (the cursor).
        # When we have set the last digit return -ve so caller knows to exit setting mode.
        # No tens of hours above 2.
        if  self.digitIndex == 0 and digit > '2' :
            return 0
        # No tens of minutes above 5.
        if  self.digitIndex == 2 and digit > '5' :
            return 0
        # Do not allow entry of hours above 3 if tens of hours is 2.
        if self.time [0] == '2' and self.digitIndex == 1 and digit > '3' :
            return 0

        #  Get here with a valid digit so recover existing character.
        existingCharacter = self.time [self.digitIndex]
        # Now put the digit in and bump the index.
        self.time [self.digitIndex] = digit
        # if this is the last digit then set return -ve so caller knows to exit setting mode.
        self.digitIndex += 1
        if  self.digitIndex > 3 :
            self.digitIndex = 0
            return -1
        else :    
            # Return the existing character so caller knows we had success and are not finished.
            return existingCharacter

    def SetCharacter (self, character) :
        self.time [self.digitIndex] = character
    
################################################################################
#
# Class: times
#
# Parameters: 
#
# Methods:
#
# Globals modified:
#
# Comments: 
#
################################################################################

class times :

    def __init__ (self, zone) :
        self.zone = zone
        self.zoneFileName = CreateFileName (self.zone)
        self.dataChanged = False

        # Keep the number of the last and current entry here.
        self.lastProgramEntryNumber = 0
        self.currentProgramEntryNumber = 1

        # Get all the program lines for this zone from the file into a list.
        f = open (self.zoneFileName, 'r')
        self.allProgramLines = f.readlines ()
        f.close ()

        # Keep number of entries. 1st line is auto / man mode line so we exclude from number of entries.
        self.numberOfEntries = len (self.allProgramLines) - 1

        # Get all the fields for each line into a list of lists and replace time and day text strings with objects.
        # The 1st line is the auto/man mode line so there are no on or off times to extract. We will scan this line
        # to determine which mode we are in.
        self.allProgramFields = []
        for line in range (0, len (self.allProgramLines)) :
            self.allProgramFields.append (self.allProgramLines [line].split ())
            if line == 0 :
                # Check each word in the 1st line to see if it is auto or man then save the word and index.
                for index in range (0, len (self.allProgramFields [0])) :
                    if self.allProgramFields [0][index].upper() in ('AUTO','MAN') :
                        self.autoManMode = [self.allProgramFields [0][index].upper(), index]

            else :
                self.allProgramFields [line][GD.ON_TIME_INDEX] = timesField (self.allProgramFields [line][GD.ON_TIME_INDEX])
                self.allProgramFields [line][GD.OFF_TIME_INDEX] = timesField (self.allProgramFields [line][GD.OFF_TIME_INDEX])
                self.allProgramFields [line][GD.DAYS_INDEX] = daysField (self.allProgramFields [line][GD.DAYS_INDEX])            
                
    def AddNewEntry (self) :
        self. blankEntry = ['On', timesField ('00:00'), 'Off', timesField ('00:00'), daysField ('_______')]
        # If we are at last entry append new entry else insert it after current entry.
        if self.currentProgramEntryNumber == self.numberOfEntries :
            # Create new fields for entry and add it on to end of list.
            self.allProgramFields.append (self.blankEntry)
            self.currentProgramEntryNumber = self.numberOfEntries + 1
        else :
            # We always add entry after the current one.
            self.currentProgramEntryNumber +=1
            # Create new fields for entry and insert it in the list.
            self.allProgramFields.insert (self.currentProgramEntryNumber, self.blankEntry)
            
        # Update number of entries as we have added one and tell caller the number.
        self.numberOfEntries += 1       
        self.dataChanged = True
        return self.currentProgramEntryNumber

    def GetZoneNumber (self) :
        return self.zone
    
    def GetNumberOfProgramEntries (self) :
        return self.numberOfEntries

    def GetLastEntryNumberAccessed (self) :
        return self.lastProgramEntryNumber

    def GetAllProgramLines (self) :
        # Return a list of all the lines, including the auto man mode line.
        return self.allProgramLines

    def SelectProgramEntry (self, entryNumber) :
        # Calculate the actual entry number.
        if entryNumber >= 99 :
            self.currentProgramEntryNumber += 1
        elif entryNumber > 0 :
            self.currentProgramEntryNumber = entryNumber
        elif entryNumber < 0 :
            self.currentProgramEntryNumber -= 1
    
        # Make sure entry is in valid range. (1 to number of entries)
        if self.currentProgramEntryNumber < 1 :
            self.currentProgramEntryNumber = 1
        if self.currentProgramEntryNumber > self.numberOfEntries :
            self.currentProgramEntryNumber = self.numberOfEntries

        # Keep this entry number so we can check if we have already selected this entry.
        self.lastProgramEntryNumber = self.currentProgramEntryNumber

    def GetActiveZoneName (self) :
        # Is it RAD, UFH or SYS zone? rad is 0-13, ufh is 14-29 sys is 30-33. Start name with Rad or Ufh if required.
        if  self.zone < 14 :
            self.zoneName = 'Rad '
        elif self.zone < 30 :
            self.zoneName = 'Ufh '
        else :
            self.zoneName = ''
            
        # Create the text for the zone name.
        self.zoneName = self.zoneName + zoneData[self.zone].GetZoneName()
        return self.zoneName
        
    def GetTime (self, index) :
        # index selects the ON or OFF time field (ON = 1, OFF = 3).
        return self.allProgramFields [self.currentProgramEntryNumber][index].GetEditTime ()

    def RecoverPreEditTime (self, index) :
        # index selects the ON or OFF time field (ON = 1, OFF = 3).
        return self.allProgramFields [self.currentProgramEntryNumber][index].RecoverTime ()

    def GetDigitPosition (self, index) :
        # index selects the ON or OFF time field (ON = 1, OFF = 3).
        return self.allProgramFields [self.currentProgramEntryNumber][index].GetDigitIndex ()

    def GetDays (self, index) :
        return self.allProgramFields [self.currentProgramEntryNumber][index].GetDaysEntry ()

    def CheckIfAutoMode (self) :        
        # Search for 'auto' in text on 1st line. If it is there we reurn true.
        return self.autoManMode[0] == 'AUTO'

    def ClearTime (self, index) :
        # index selects the ON or OFF field (ON = 1, OFF = 3).
        self.allProgramFields [self.currentProgramEntryNumber][index].ClearTimeEntry ()
        self.dataChanged = True

    def ClearDays (self, index) :
        # index selects the day field (DAY = 4). We may have on day and off days in the future.
        self.allProgramFields [self.currentProgramEntryNumber][index].ClearDaysEntry ()
        self.dataChanged = True

    def ModifyTime (self, index, digitValue) :
        # index selects the ON or OFF field (ON = 1, OFF = 3).
        cursor = self.allProgramFields [self.currentProgramEntryNumber][index].SetDigit (digitValue)
        # If the return value is > 0 we had a valid digit so move the cursor on.
        if cursor > 0 :
            self.SetCursor (index, cursor)
            self.dataChanged = True
        
        # Return value will be: 0 = fail, +ve = OK not finished, -ve = OK and finished.
        return cursor
        
    def SetCursor (self, index, cursor) :
        # index selects the ON or OFF field (ON = 1, OFF = 3).
        self.allProgramFields [self.currentProgramEntryNumber][index].SetCharacter (cursor)
        self.dataChanged = True
           
    def ModifyDay (self, index, dayValue) :
        # index selects the day field (DAY = 4). We may have on day and off days in the future.
        self.allProgramFields [self.currentProgramEntryNumber][index].SetDay (dayValue)
        self.dataChanged = True
           
    def SaveAllProgramEntries (self) :
        # Merge the list of program entry text strings into a string and then write this string to file.  
        f = open (self.zoneFileName, 'w')
        f.write ("".join (self.allProgramLines))
        f.close ()
        
    def SwitchModes (self) :
        if self.CheckIfAutoMode () == True :
            self.allProgramFields [0][self.autoManMode[1]] = 'Man'
            self.autoManMode[0] = 'MAN'
        else :
            self.allProgramFields [0][self.autoManMode[1]] = 'Auto'
            self.autoManMode[0] = 'AUTO'

        self.dataChanged = True

    def UpdateProgramEntries (self) :
        # Merges the current list of program fields back into a list of program text strings. We do not save any entries
        # that do not have valid program times. If none of the entries is valid we create a new blank entry.
        # 1st clear the program text strings list.
        self.allProgramLines = []

        for line in range (0, len (self.allProgramFields)) :
            # The 1st line (line 0) is the auto/man mode line so only replace on or off time objects from line 1 onwards
            # with strings.
            if line == 0 :
                # Process 1st line.
                self.allProgramLines.append (" ".join (self.allProgramFields[line])+'\n')
                
            else :
                # Get the on time, off time and days as text strings.
                self.entryOnTime = self.allProgramFields [line][GD.ON_TIME_INDEX].GetEditTime ()
                self.entryOffTime = self.allProgramFields [line][GD.OFF_TIME_INDEX].GetEditTime ()
                self.entryDays = self.allProgramFields [line][GD.DAYS_INDEX].GetDaysEntry ()

                # Only process the line if it has valid times and days (off > on and a valid day).
                if self.entryOffTime > self.entryOnTime and self.entryDays != '_______' :
                    # Replace object fields with strings
                    self.allProgramFields [line][GD.ON_TIME_INDEX] = self.entryOnTime
                    self.allProgramFields [line][GD.OFF_TIME_INDEX] = self.entryOffTime
                    self.allProgramFields [line][GD.DAYS_INDEX] = self.entryDays
                    # Merge the fields into a space separated string and add a new line character at the line end.
                    self.allProgramLines.append (" ".join (self.allProgramFields[line])+'\n')

        # Update number of entries. 1st line is auto / man mode line so we exclude from number of entries.
        self.numberOfEntries = len (self.allProgramLines) - 1

        # If we now have no entries create a blank one.
        if self.numberOfEntries == 0 :           
            # Create new line for entry and add it on to end of list.
            self.allProgramLines.append ('On 00:00 Off 00:00 _______\n')
            self.numberOfEntries = 1

        # Make 1st line the current line
        self.currentProgramEntryNumber = 1

        # Write back to file.
        self.SaveAllProgramEntries ()
        self.dataChanged = False

        # Now read back the modified file to update our object image.
        self.__init__(self.zone)

    def CheckIfDataChanged (self) :
        return self.dataChanged

    def CheckIfDisabled (self, index) :
        # index selects the day field (DAY = 4). We may have on day and off days in the future.
        return self.allProgramFields [self.currentProgramEntryNumber][index].CheckIfDayDisabled ()

        
################################################################################
#
# Function: ReadZoneTimes (zone)
#
# Parameters: zone - integer - the zone to get the programmed times of
#
# Returns:
#
# Globals modified:
#
# Comments: 
#
################################################################################

def ReadZoneTimes (zone) :

    global zoneTimes

    # Create object of all the programmed times for this zone.
    zoneTimes = times (zone)

################################################################################
#
# Class: zone
#
# Parameters: zoneName - string - the name of the zone
#
# Methods:
#
# Globals modified:
#
# Comments: 
#
################################################################################

class zone :

    # We will keep the pump status for each heating zone here. This will enable us to check if any zone requires a pump on.
    # Locations 0-13 are for the rad pump and 14-29 for the ufh pump.
    # Values: -1 = pump off, 0 = pump on, +ve = delay until pump on in seconds.
    pumpStatus = [-1]*30
    
    def __init__ (self, zoneCode, zoneName) :
        # The zonecode is 0-13 for rads and 14-29 for ufh
        self.zoneCode = zoneCode
        # The name of the zone as displayed to the user and also used for creating zone file name.
        self.zoneName = zoneName
        # Boost off time day, hour, minute.
        self.boostDayOff = 0
        self.boostHourOff = 0
        self.boostMinuteOff = 0
        # Status that boost should be set to. 0=OFF, 1=ON
        self.newBoostStatus = 0
        # Status that boost is currently. 0=OFF, 1=ON
        self.currentBoostStatus = 0
        # Status the zone should be set to. 0=OFF, 1=ON, -1=ON but CANcelled
        self.newTimedStatus = 0
        # Status the zone is currently. 0=OFF, 1=ON, -1=ON but CANcelled
        self.currentTimedStatus = 0
        # Flag to show if button is illuminated. We use this as a flash indicator when the zone is changing state.
        #self.buttonLamp = 0 
        # Relay cleardown timer. +ve=seconds to cleardown, 0=no cleardown, -1=cleardown required.
        self.clearDownTimer = 0
     
    def GetZoneName (self):
        return self.zoneName
        
    def CheckIfZoneBoostOn (self) :
        # Boost day is set to -1 when boost is off.
        #return self.boostDayOff != -1
        return self.newBoostStatus == 1

    def SetZoneBoostOff (self) :
        # Request an off.
        #self.boostDayOff = -1
        self.newBoostStatus = 0
        # If the zone is on from a timed request we can clear the current status as no operation needs to run as it needs to stay on.
        if self.currentTimedStatus == 1 :
            self.currentBoostStatus = 0

    def SetZoneBoostOn (self, boostDayOff, boostHourOff, boostMinuteOff) :
        # Request an on.
        self.newBoostStatus = 1
        # If the zone is already on from a timed request we can set the current status as no operation needs to run as it is already on.
        if self.currentTimedStatus == 1 :
            self.currentBoostStatus = 1
        # Set the off time for the boost.
        self.boostDayOff = boostDayOff
        self.boostHourOff = boostHourOff
        self.boostMinuteOff = boostMinuteOff

    def GetBoostOffTime (self) :
        return (self.boostDayOff, self.boostHourOff, self.boostMinuteOff)

    def SetZoneTimedOn (self) :
        # Request an on.
        self.newTimedStatus = 1
        # If the zone is already on from a boost request we can set the current status as no operation needs to run as it is already on.
        if self.currentBoostStatus == 1 :
            self.currentTimedStatus = 1
          
    def SetZoneTimedOff (self) :
        # Request an off.
        self.newTimedStatus = 0
        # If the zone is already cancelled then we can clear the current status as no operation needs to run as it is already off. We
        # can also clear the current status if the zone is on from a boost request as no operation needs to run as it needs to stay on.
        if self.currentTimedStatus == -1 or self.currentBoostStatus == 1 :
            self.currentTimedStatus = 0

    def SetZoneTimedCancelled (self) :
        self.newTimedStatus = -1

    def CheckIfZoneStatusChanged (self) :
        return self.newTimedStatus != self.currentTimedStatus or self.newBoostStatus != self.currentBoostStatus

    def CheckIfZoneOnRequested (self) :
        return self.newTimedStatus == 1  or  self.newBoostStatus == 1

    def CheckIfZoneTimedIsCancelled (self) :
        return self.newTimedStatus == -1

    def CheckIfZoneTimedWasCancelled (self) :
        return self.currentTimedStatus == -1

    def CheckIfZoneOn (self) :
        return self.currentTimedStatus == 1  or  self.currentBoostStatus == 1
    
    def UpdateCurrentZoneStatus (self) :
        self.currentTimedStatus = self.newTimedStatus
        self.currentBoostStatus = self.newBoostStatus

    def UpdatePumpStatus (self) :
        # Set pump delay time if zone is on or set -1 flag if zone is off.
        if self.currentTimedStatus == 1 or  self.currentBoostStatus == 1:
            self.pumpStatus[self.zoneCode] = GD.PUMP_DELAY_TIME
        else :
            self.pumpStatus[self.zoneCode] = -1
            
    def CheckIfPumpRequired (self) :
        if self.zoneCode >= 14 :
            # This will tell us if any ufh zone is on and pump is required.
            return 0 in self.pumpStatus[14:30]
        else :
            # This will tell us if any rad zone is on and pump is required.
            return 0 in self.pumpStatus[0:14]

    def UpdatePumpTimer (self) :
        # If the timer is +ve decrement it. It will then stick at zero meaning turn pump on.
        # If the value is -1 for off nothing happens.
        if  self.pumpStatus[self.zoneCode] > 0 :
            self.pumpStatus[self.zoneCode] -= 1
            print 'pump', self.pumpStatus[self.zoneCode]
            # Tell caller if we have reached zero. Time to turn pump on.
            if  self.pumpStatus[self.zoneCode] == 0 :
                return True
        return False

    def UpdateCleardownTimer (self) :
        # If the timer is +ve decrement it. It will then stick at -1 meaning time for cleardown.
        # If the value is 0  nothing happens.
        if self.clearDownTimer > 0 :
            print self.clearDownTimer
            self.clearDownTimer -= 1
            if self.clearDownTimer < 1 :
                self.clearDownTimer = -1
        return self.clearDownTimer

    def CancelCleardownTimer (self) :
        self.clearDownTimer = 0

    def SetCleardownTimer (self, cleardownTime) :
        self.clearDownTimer = cleardownTime

    def CheckIfTimeForCleardown (self) :
        return self.clearDownTimer == -1



################################################################################
#
# Function: InitialiseZones ()
#
# Parameters: none
#
# Returns:
#
# Globals modified:
#
# Comments: Creates a dictionary of zone objects, One for each heating zone and system zones (immersions).
#
################################################################################

def InitialiseZones () :
    global zoneData

    # Create sequence of text names for the zones. 14 for rads, 16 for ufh and 4 for immersions.
    zoneNames = ('Bed 1', 'Bed 2', 'Bed 3', 'Bed 4', 'Bed 5', 'Bath 1', 'Bath 2', 'Bath 3-4',
                            'Kitchen', 'Dining', 'Library', 'Cloak', 'Sitting', 'Hall Up',
                            'Bed 1', 'Bed 2', 'Bed 3', 'Bed 4', 'Bed 5', 'Bath 1', 'Bath 2', 'Bath 3-4',
                            'Kitchen', 'Dining', 'Library', 'Cloak', 'Sitting', 'Hall Up', 'Hall Down', 'Sittingx',
                            'Immersion 1', 'Immersion 2', 'Immersion 3', 'Immersion 4' )
    # Zone id codes start at 0.
    zoneCodes = 0
    # Now build a dictionary of data objects. 1 for each zone.
    zoneData = {}
    for name in zoneNames :
        zoneData [zoneCodes] = zone (zoneCodes, name)
        zoneCodes += 1
         
################################################################################
##
## Function: UpdateZoneStatus (zone)
##
## Parameters: zone - integer - the zone required 0 - 29 (0-13 rads, 14-29 ufh)
##
## Returns: 4 integer tuple - (status from 0-5, day from 0-6, hour from 0-23, minute from 0-59)
## Values for status are:
##               0=zone not active - time is next on time.
##               1=zone active - time is off time
##               2=manual mode - day is set to -1
##               3=boost mode - time is off time
##               4=zone active, but cancelled - time is off time
##               5=error in zone time file - day set to -1
##
## Globals modified:
##
## Comments: Scan the zone times file for the zone supplied. We will search through the programmed times to update the zone
## status to on or off, as required. Prior to this we will check if a boost on is in operation as this overrides any programmed
## operation. We return a status code and time as defined above so we can display it to the user. If the system is off we will
## turn any 'on' operations to 'off' operations. This will have the effect of closing all the zone valves when the system is off.
##
################################################################################

def UpdateZoneStatus (zone) :

    # We will keep all the on times we find here.
    onTimes = []

    print CreateFileName (zone)[:-4],
    display.debugMessage.StartMessage ( CreateFileName (zone)[:-4])
    
    # Get the time now.
    timenow = time.localtime (time.time())
    timeNowHourMinute = (timenow.tm_hour, timenow.tm_min)
    dayNow = (timenow.tm_wday,)

    # Check if we have a boost set for this zone. This will override any programmed time.
    if zoneData[zone].CheckIfZoneBoostOn() == True :

        # We have a boost so get the boost off time.
        boostOffDay, boostOffHour, boostOffMinute =  zoneData[zone].GetBoostOffTime()
    
        print 'BOOST',
        display.debugMessage.AddToMessage (' Boost')
        
        # A boost period can end the following day so we need to check we are on the actual end day. We cannot
        # include the offday with offhour and offminute as the offday could be Monday (0) for a sunday (6) boost.
        # Check if boost period is ended and set flags accordingly.
        if boostOffDay == timenow.tm_wday  and timeNowHourMinute >= (boostOffHour, boostOffMinute) :

                # Boost has ended so set boost to OFF.
                zoneData[zone].SetZoneBoostOff ()
                print 'OFF'
                display.debugMessage.DisplayMessage (' Off')
        else :
                print 'ON'
                display.debugMessage.DisplayMessage (' On')
                # We have a boost so check if the system is off and if it is turn this zone off.
                if system.systemControl [GD.SYSTEM_OFF_MODE].CheckIfBitHigh () == True :
                    zoneData[zone].SetZoneBoostOff ()
                
                return (GD.STATUS_BOOST_MODE, boostOffDay, boostOffHour, boostOffMinute)

    # No boost or boost ended so create the filename for this zone so we can get the program data.
    zoneFileName = CreateFileName (zone)

   # Get all the programmed on-off times for this zone from the file into a list.
    f = open (zoneFileName, 'r')
    zoneProgrammedTimes = f.readlines ()
    f.close ()

    # The 1st line in the file tells us if the mode is MANual or AUTo.
    # If it is manual we set the zone OFF and tell the caller that the zone is in manual mode.
    if zoneProgrammedTimes[0].upper ().find ('MAN') >= 0 :
        print 'MAN OFF'
        zoneData[zone].SetZoneTimedOff ()
        return (GD.STATUS_MANUAL_MODE, GD.DAY_TIME_NOT_VALID, 0, 0)

    # Scan through each of the programmed on-off times in the list. Miss 1st line, which is auto/manual flag.
    for zoneOnOffTimeSet in zoneProgrammedTimes[1:] :

        # Get all the fields for this programmed on-off time into a list
        zoneOnOffTime = zoneOnOffTimeSet.split ()

        # Create HH,MM integer tuples for this on-off time (the program string has 2 digits each for HH and MM).
        zoneOnTime = (int (zoneOnOffTime[ON_TIME_INDEX][HOUR_INDEX : HOUR_INDEX+2]),
                                 int (zoneOnOffTime[ON_TIME_INDEX][MINUTE_INDEX : MINUTE_INDEX+2]))
        zoneOffTime = (int (zoneOnOffTime[OFF_TIME_INDEX][HOUR_INDEX : HOUR_INDEX+2]),
                                 int (zoneOnOffTime[OFF_TIME_INDEX][MINUTE_INDEX : MINUTE_INDEX+2]))

        # Test if day and time now are within this programmed on-off time, meaning the zone is ON.
        if zoneOnOffTime[DAYS_INDEX][dayNow[0]] in ('M', 'T', 'W', 'F', 'S') and\
          timeNowHourMinute  >= zoneOnTime and\
          timeNowHourMinute  < zoneOffTime:

            print 'ON'
            print zoneOnOffTime[DAYS_INDEX][dayNow[0]]
            print timeNowHourMinute, zoneOnTime
            print timeNowHourMinute, zoneOffTime
          
            # The zone is programmed ON, but we need to check if the user has cancelled the period.
            if zoneData[zone].CheckIfZoneTimedIsCancelled() == True :
                print 'CANCELLED'
                # Return status and the off time.
                return ((GD.STATUS_ZONE_CANCELLED,)  + dayNow + zoneOffTime)
            else :
                # Period not cancelled so now check if the system is off and if it is turn the zone off.
                if system.systemControl [GD.SYSTEM_OFF_MODE].CheckIfBitHigh () == True :
                    zoneData[zone].SetZoneTimedOff ()
                else :
                    # The system is on so set the zone on.
                    zoneData[zone].SetZoneTimedOn()
                    print 'ON'
                #  Return status and the off time.
                return ((GD.STATUS_ZONE_ACTIVE,)  + dayNow + zoneOffTime)

        # If we get here the zone is not ON for this programmed on-off time, so we need to save each active day for
        # this programmed on-off time along with the on time. Later when we have saved all the day and on times for
        # every programmed on-off time we will be able to find when the next on time will be so we can tell the user.
        
        # Scan through day field for this on-off time to find active days.
        for dayNumber in range (0,7) :

            # Is day active? It will be M, T, W, T, F, S or S if it is and _ or lowercase if it isn't.
            if zoneOnOffTime[DAYS_INDEX][dayNumber] in ('M', 'T', 'W', 'F', 'S') :

                # Is the time range valid (off > on)?
                if zoneOffTime > zoneOnTime :

                    # Put the day number and on time for this day in list (sorted).
                    bisect.insort (onTimes, (dayNumber,) + zoneOnTime)

    else:
        # Get here if all programmed times have been scanned and no ON period found so find the next ON time so we
        # can tell user we are 'Off Until HH:MM On DayX'. Make sure we have found some ON times 1st and report an error
        # if there are none.
        if len (onTimes) :
            nextOnTimeIndex = bisect.bisect (onTimes, dayNow + timeNowHourMinute)

            # If the nextOnTimeIndex is after the last on time (equal to length) wrap round to 1st on time.
            if nextOnTimeIndex == len (onTimes) :
                nextOnTimeIndex = 0

            # Set the zone's status OFF. This will reset any cancel.
            zoneData[zone].SetZoneTimedOff ()
            print 'OFF'

            # Get the on time.
            nextOnTime = onTimes[nextOnTimeIndex]

            # Tell caller zone is not ON and supply next on time.
            return ((GD.STATUS_ZONE_NOT_ACTIVE,) + nextOnTime)
        else:
            # Tell caller error in program file
            return (GD.STATUS_PROGRAM_FILE_ERROR, GD.DAY_TIME_NOT_VALID, 0, 0) 

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

