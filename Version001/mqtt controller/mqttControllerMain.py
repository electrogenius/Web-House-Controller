import time
import json
import socket


import paho.mqtt.client as mqttClient

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect (("8.8.8.8", 80))
isRpi = s.getsockname()[0] == "192.168.0.243"

if isRpi:
    import RPi.GPIO as GPIO
    import smbus

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)
    id = "RPI"
else:
    id = "WIN"

# Lookup to get hardware GPIO pin for a given zone.
zonePin = {
    "zone1": 18, "zone2": 23
}
# We will use a dictionary to hold the state that we need to set a zone. The MQTT message arrives as a 1 element dictionary
# so we will append it to this dictionary. Each element will consist of the key:value pair of - zone number : state. State will
# be received as "on" or "off". Once we have set the relays to activate/deactivate the zone we replace state with a timer
# value which we decrement every second. When this reaches zero we will cleardown the zone relay to the idle condition.
zoneRelayState = {}





################################################################################
#
# Function:  PulseLatchingRelay (I2CPort, register, relayBit)
#
# Parameters:  I2CPort - I2C smbus object
#                     register - the I2C address of the relay controller
#                     relayBit - the binary bit of the bit to be pulsed
#
# Returns:
#
# Globals modified:
#
# Comments: Pulses the required relay specified by relayBit. We are controlling latching relays in the valve relay matrix so
#                   we have to give the required activate time.
#
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
#
# Function:  activateHeatingZoneRelay (I2CPort, relayZone, operation)
#
# Parameters: I2CPort - I2C smbus object
#                    relayZone - integer - the zone
#                   operation - string - off, on or cleardown
#
# Returns:
#
# Globals modified:
#
# Comments:
#
################################################################################

def activateHeatingZoneRelay (I2CPort, relayZone, operation) :

        # Select the correct I2C status register for UFH or RAD relays.
        register = 0x3a  if relayZone >= 14 else  0x3a
        
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
        
        # If we are in cleardown we need to turn off the power relay first and then the open relay.
        if operation == "cleardown" :
            print "cleardown"
            # Set the mode bit low to select the power relay (low bit 4 = power).
            relays &= ~0x10

            # Send to relay register, wait for relays to stabilise.
            I2CPort.write_byte (register, relays)
            print 'select mode power ', hex(relays^0xff)
            time.sleep (0.1)

            # Now pulse OFF relay ( bit 6) to ensure power is removed from the valve.
            PulseLatchingRelay (I2CPort, register, 0x40)

            # Set the mode bit to select the open relay (high bit 4 = open), Wait for relay to stabilise.
            relays |= 0x10
            I2CPort.write_byte (register, relays)
            print 'select open ', hex(relays^0xff)
            time.sleep (0.1)

            # Now pulse OFF relay (bit 6) to ensure open is removed from the valve.
            PulseLatchingRelay (I2CPort, register, 0x40)
        else :
            # Must be on or off.
            # Set the mode bit to select the open relay (high  bit 4 = open), Wait for relay to stabilise.
            relays |= 0x10
            I2CPort.write_byte (register, relays)
            print 'select open ', hex(relays^0xff)
            time.sleep (0.1)

            # if is on we need to set the open relay first and then the power relay.
            if operation == "on" :
                # Valve needs to open so pulse the ON relay (bit 5).
                PulseLatchingRelay (I2CPort, register, 0x20)

            else :
                # Valve needs to close so pulse OFF relay (bit 6).
                PulseLatchingRelay (I2CPort, register, 0x40)

            # Set the mode bit to select power relay (low bit4 = power), wait for relay to stabilise.
            relays &= ~0x10
            I2CPort.write_byte (register, relays)
            print 'select power ', hex(relays^0xff)
            time.sleep (0.1)

            # Now pulse ON relay (bit 5) to turn power to the valve on.
            PulseLatchingRelay (I2CPort, register, 0x20)

        # Relay operations complete so set all relays to inactive (except pump).
        # Deactivate relays in sequence so only 1 relay at a time is powered down to minimise back emfs.
        for bitSelect in (0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F, 0x7F) :
            I2CPort.write_byte (register, relays | bitSelect)
            time.sleep (0.1)
        print 'relays all off '

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

def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("Connected to broker from "+id)
        client.subscribe("zone/control/state") 
    else:
        print("Connection failed")

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

def on_message(client, userdata, message):
    print "Message received: "  + message.payload
    # Message arrives as dictionary so convert to list so we can get key,value
    # tuple. We only use 1st entry for zone control so zone is in [0][0] and
    # state is in [0][1].
   # restoredData = json.loads (message.payload).items()
    restoredData = json.loads (message.payload)
    zoneRelayState.update (restoredData)
    print restoredData, zoneRelayState
    #zone, state = restoredData[0]
    #state = 0 if state == "on" else 1
    #print 'Restored:',restoredData, zone,state,zonePin [zone]

    # Make sure the zone is a valid one.
    #if zone in zonePin :
   #     print ("valid")
        #if isRpi: GPIO.output (zonePin [zone], state)

################################################################################
#
# Function:  main () :
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

def main () :

    #Initialise the I2C port used for the relays and get I2C port object.
    if isRpi:I2CPort = smbus.SMBus (1)

    brokerAddress = "192.168.0.244"  
    client = mqttClient.Client(id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(brokerAddress)
    client.loop_start ()

    try:
        while True:
            time.sleep(1)
           # We make a list of zones that have completed cleardown so we can remove them.
            completedZones = []
            # Scan through all the zones waiting for action.
            for zone in zoneRelayState :
                # Get the physical address from the zone number. We will use this to select relay.
                # Physical addresses start at zero so adjust address as zones start at 1.
                zoneAddress = int (zone [4:]) -1
                # Does a zone need turning on or off?
                if  zoneRelayState [zone] in ["on", "off"] :
                    print zoneAddress, zoneRelayState [zone]
                    # Go and do activation.
                    activateHeatingZoneRelay (I2CPort, zoneAddress,  zoneRelayState [zone])
                    # Now set cleardown timer. Different times required for on and off.
                    zoneRelayState [zone] = 60 if zoneRelayState [zone] == "off" else 30
                else :
                    # Zone must be in cleardown delay so decrement delay.
                    zoneRelayState [zone] -= 1
                    # Have we reached time for cleardown?
                    print 'timer',  zoneRelayState [zone]
                    if zoneRelayState [zone] == 0 :
                        # Go and do cleardown.
                        activateHeatingZoneRelay (I2CPort, zoneAddress,  "cleardown")

                        # Save this zone so we can delete it later now that we are finished with it.
                        # We can't delete it from within this loop.
                        completedZones.append (zone)
                        print 'completed zones', completedZones
            
            # Now delete any zones we have finished with (cleardown has been completed).
            for zone in completedZones :
                del zoneRelayState [zone]

    
    except KeyboardInterrupt:
        print "exiting"
        client.disconnect()
        client.loop_stop()




    
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



