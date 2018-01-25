import time
import zones
import smbus
import GD
import system
  
################################################################################
##
## Function: ActivateSystemRelay (I2CPort, systemRelay, setHigh)
##
## Parameters: I2CPort - I2C smbus object
##                    systemRelay - the relay to activate
##                    setHigh - True for high, False for low
##
## Returns:
##
## Globals modified:
##
## Comments: Looks up the status of a system control bit and sets relay on or off as required. Note: relays are active low drive.
##
################################################################################

def ActivateSystemRelay (I2CPort, systemRelay, setHigh) :

    # TEMP TO ALLOW WITHOUT SYSTEM HARDWARE
   ## if systemRelay not in (GD.SYSTEM_RAD_PUMP, GD.SYSTEM_UFH_PUMP) : return

    # Get the I2C parameters from our system control data.
    address = system.systemControl [systemRelay].GetAddress () 
    mask = system.systemControl [systemRelay].GetBitMask ()
    
    # Read existing relay status for all relay bits at this address.
    relayStatus = I2CPort.read_byte (address)
    
    # Do we need to set this bit high or low?
    if setHigh == True :
    
        # We need to turn relay on so invert bit mask so bit we want is now zero, for active low, and all others will be high.
        # AND it with existing bits to clear the bit we need to set low output for relay.
        mask ^= 0xff 
        relayStatus &= mask
    else :
    
        # Need to turn relay off so we can just OR the bit with the existing bits to set high output for relay.
        relayStatus |= mask
        
    # Write new relay staus back for all the relay bits at this address.
    I2CPort.write_byte (address, relayStatus)
        
################################################################################
##
## Function: UpdateSystemOutputs (I2CPort)
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments: Scan through the system output config bits and update a relay that needs to be changed.
##
################################################################################

def UpdateSystemOutputs (I2CPort) :

    # Scan through the outputs until we find one that needs updating.
    for systemOutput in (GD.SYSTEM_OUTPUT_GROUP) :
    
        # Only do I2C transfer if relay needs updating.
        if system.systemControl [systemOutput].CheckIfBitChanged () == True :
            
            # Set relay as required by system status
            setHigh = system.systemControl [systemOutput].CheckIfBitHigh ()
            ActivateSystemRelay (I2CPort, systemOutput, setHigh)
            
            # Update status for bit now we have done relay update.
            system.systemControl [systemOutput].UpdateBitChangedStatus ()
            
            # Now that we have updated a relay we will leave. This is so that we only update 1 relay every time we are called,
            # which is once a second. This will minmise power surges on the system as devices will be powered gradually rather
            # than all at once.
            break

    for systemConfig in (GD.TANK_2_MANUAL_OVERRIDE_GROUP) :
        system.systemControl [systemConfig].UpdateBitChangedStatus ()
 
################################################################################
##
## Function: UpdatePulsedOutputLines ()
##
## Parameters:
##
## Returns:
##
## Globals modified:
##
## Comments:  Scan through and update all the output line pulse timers. If any are finished set the output line low.
##
################################################################################

def UpdatePulsedOutputLines (I2CPort) :

    for systemOutput in GD.SYSTEM_PULSED_OUTPUTS_GROUP :
        if system.systemControl [systemOutput].CheckIfBitTimerFinished () == True :
            ActivateSystemRelay (I2CPort, systemOutput, False)
            print 'SET IT LOW'
        

################################################################################
##
## Function:  PulseLatchingRelay (I2CPort, register, relayBit)
##
## Parameters: I2CPort - I2C smbus object
##                     register - the I2C address of the relay controller
##                     relayBit - the binary bit of the bit to be pulsed
##
## Returns:
##
## Globals modified:
##
## Comments: Pulses the required relay specified by relayBit. We are controlling latching relays in the valve relay matrix so
##                    we have to give the required activate time.
##
################################################################################

def PulseLatchingRelay (I2CPort, register, relayBit) :
    # Read existing relay status.
    relayStatus = I2CPort.read_byte (register)
    # Set the relay to pulse (active low pulse).
    relayStatus &= ~relayBit
    # Pulse it low.
    I2CPort.write_byte (register, relayStatus)
    print 'pulse on ', hex(relayStatus^0xff)
    # Give it some time to activate.
    time.sleep (0.1)       
    # Now set up to clear the relay pulse (set it back high).
    relayStatus |= relayBit
    # Restore the level high.
    I2CPort.write_byte (register, relayStatus)
    print 'pulse off ', hex(relayStatus^0xff)
    # Give it time to activate.
    time.sleep (0.1)

################################################################################
##
## Function:  ActivateHeatingZoneRelay (I2CPort, relayZone)
##
## Parameters: I2CPort - I2C smbus object
##                    relayZone - integer - the zone to check if activation required.
##
## Returns:
##
## Globals modified:
##
## Comments: 
##
################################################################################

def ActivateHeatingZoneRelay (I2CPort, relayZone) :

    # Find out if status of this zone has changed, if it now needs to be on or needs a cleardown.
    statusChanged = zones.zoneData[relayZone].CheckIfZoneStatusChanged () == True
    statusOn = zones.zoneData[relayZone].CheckIfZoneOnRequested () == True
    clearDown = zones.zoneData[relayZone].CheckIfTimeForCleardown () == True

    # If the status has changed we need to update our current status.
    if statusChanged :
        zones.zoneData[relayZone].UpdateCurrentZoneStatus()

     # Has the status changed or is it time for cleardown on this zone?
    if statusChanged or clearDown :

        print 'STATUS CHANGED'

        # Select the correct I2C status register for UFH or RAD relays.
        register = GD.I2C_ADDRESS_0X38  if relayZone >= 14 else  GD.I2C_ADDRESS_0X39
        
        # Read the status register to get the current state of the pump bit. Mask off all except pump bit.
        # Bits are active low - so a 0 = on.
        relays = I2CPort.read_byte (register)
        relays &= 0x80
    
        # Invert the pump bit as these are active low outputs and we are going to OR in bits.
        relays ^= 0x80
        # OR in the zone required (bits 0-3). Adjust to get UFH zone in range 0-15 from 14-29.
        relays |= relayZone
        if relayZone >= 14 :
            relays -= 14

        # Invert bits to make active low outputs.
        relays ^= 0xff

        # Activate the zone select relays in sequence so only 1 relay at a time is powered up to minimise current surge.
        for bitSelect in (0x07, 0x03, 0x01, 0x00) :
            I2CPort.write_byte (register, relays | bitSelect)
            time.sleep (0.1)
        
        # If we are in cleardown we need to turn off the power relay first.
        if clearDown and not statusChanged :
            # Set the mode bit to select the power relay (active low bit4).
            relays &= ~0x10

            # Send to relay register, wait for relays to stabilise.
            I2CPort.write_byte (register, relays)
            print 'select mode power ', hex(relays^0xff)
            time.sleep (0.1)

            # Now pulse OFF relay (active low bit6) to ensure power is removed from the valve.
            PulseLatchingRelay (I2CPort, register, 0x40)

            # Clear the mode bit to select the open relay (active low bit4), Wait for relay to stabilise.
            relays |= 0x10
            I2CPort.write_byte (register, relays)
            print 'select open ', hex(relays^0xff)
            time.sleep (0.1)

        # We get here if there has been a status change or it is  a cleardown. If it is a status change and the new status = ON
        # then we will turn the relay on to open the valve when power is turned on. If it is a status change and the new
        # status = OFF  or there is no status change (must be a cleardown) we will turn the relay off. This will either close the
        # valve if we apply power for a status change or simply turn the relay off for a cleardown.
        # Do we need to open the valve?
        if statusChanged and statusOn :
            # Valve needs to open so pulse the ON relay (active low bit5).
            PulseLatchingRelay (I2CPort, register, 0x20)
            # Set the cleardown timer for the period required before we can clear the valve down. ADJUST THIS LATER
            zones.zoneData[relayZone].SetCleardownTimer (30)
        else :
            # Valve needs to close so pulse OFF relay (active low bit6).
            PulseLatchingRelay (I2CPort, register, 0x40)
            # Set the cleardown timer for the period required before we can clear the valve down. ADJUST THIS LATER
            zones.zoneData[relayZone].SetCleardownTimer (65)

        # If we are here because of a status change we need to activate the power relay on. For a cleardown we do not need
        # to do anything as a cleardown simply turns off the power and open relays.
        if statusChanged :
            # Set the mode bit to select power relay (active low bit4), wait for relay to stabilise.
            relays &= ~0x10
            I2CPort.write_byte (register, relays)
            print 'select power ', hex(relays^0xff)
            time.sleep (0.1)

            # Now pulse ON relay (active low bit5) to turn power to the valve on.
            PulseLatchingRelay (I2CPort, register, 0x20)

            # Valve is now operating so set pump status required.
            zones.zoneData[relayZone].UpdatePumpStatus()
         
        # Not a status change so are we here because of a cleardown?
        elif clearDown :
            # Cleardown - now it is done cancel the timer.
            zones.zoneData[relayZone].CancelCleardownTimer () 

        # Relay operations complete so set all relays except pump to inactive.
        # Deactivate the zone select relays in sequence so only 1 relay at a time is powered down to minimise back emfs.
        for bitSelect in (0x01, 0x03, 0x07, 0x0F, 0x1F) :
            I2CPort.write_byte (register, relays | bitSelect)
            time.sleep (0.1)
        #relays |= 0x7f
        #I2CPort.write_byte (register, relays)
        print 'relays all off ', hex(relays^0xff)


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


