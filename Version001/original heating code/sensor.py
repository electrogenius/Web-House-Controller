import time
import zones
import smbus
import GD
import system
import ow

  

################################################################################
##
## Function: ReadSystemInputs (I2CPort)
##
## Parameters: I2CPort - I2C smbus object
##
## Returns:
##
## Globals modified:
##
## Comments: Reads all the system inputs. if an input has changed state we debounce it and then update the config input
## to the new state. The system inputs are read 8 bits at a time from our 3 I2C input ports. We then we check each of our
## config inputs to see if it is one of the bits we have read. If it is we check if the value is changed from our current config
## bit. If it is we decrement a debounce timer and when this reaches zero we will update the config bit with the new value.
## We will call this function every second so the debounce timers will decrement every second. This allows us to remove the
## spurious pulses from the flow switches caused by people turning taps on and off quickly. This stops us from turning pumps
## on and off in quick succesion.
##
################################################################################

def ReadSystemInputs (I2CPort) :

    # TEMP TO ALLOW WITHOUT INPUT HARDWARE
    ##return

    # Scan through each of our I2C inport port addresses.
    for address in (GD.I2C_ADDRESS_0X3C, GD.I2C_ADDRESS_0X3D) :
        # Get the 8 bits from a port address.
        portData =  I2CPort.read_byte_data (address, 0xff)
        # Scan through each of our system config inputs to see if it belongs to this port address.
        for systemInput in GD.SYSTEM_INPUT_GROUP :
            #Is this input on the port address we have just read?
            if address == system.systemControl [systemInput].GetAddress () :
                # Input is on this port address so get the bit state using the bit mask and convert to boolean.
                # Note inputs are low = on so we invert here so system bit is high = on.
                bitState = ((portData & system.systemControl [systemInput].GetBitMask ()) == 0)
                # Update bit.
                system.systemControl [systemInput].UpdateInputBit (bitState)

################################################################################
##
## Function: ReadTemperatures (command, result)
##
## Parameters: command - queue - we pass a 2 element tuple here, 1st element is the sensor id, 2nd element is the read time
##                    result - queue - we pass a 2 element tuple here, 1st element is the sensor id, 2nd element is the temperature
##
## Returns:
##
## Globals modified:
##
## Comments: This is run as a process. We do this as 1 wire causes a delay whenever a temperature is read and by running it
## as a process our main code is not affected by the delay. Commands and results are sent via 2 queues. For commands we
## send a tuple consisting of the device id and the interval, in seconds, to read the sensor. if the interval is is set -ve the sensor
## is not read. Results are returned as a tuple consisting of the device id and the temperature.
## Note: Because of the delay in the 1 wire operation if a large number of sensors are being read on a short interval then the
## timing interval is going to be degraded.
##
################################################################################
 
def ReadTemperatures (command, result):
    # Build a dictonary so that for each sensor id we keep the 1 wire address, the interval required, the time to the next read.
    # Setting the interval to -ve stops reading for that sensor, setting the interval to zero sets the reading to the maximum rate.
    deviceId = {}
    for sensor in GD.SYSTEM_TEMPERATURE_GROUP :
        deviceId [sensor] = [system.systemControl [sensor].GetAddress (), -1, -1]
        
    while 1 :
        
        # Set the tick timer to  1 second. If we do a 1 wire read we will change this to 0.25 to allow for the 0.75 seconds it takes
        # to do a 1 wire read!! 
        tickTime = 1
        
        # Every tick time we will scan through every sensor id.
        for sensor in deviceId :
        
            # If we have received a command; load the data. A command is a 2 element tuple. 1st element [0] is the sensor id
            # 2nd element [1] is the time interval. We will set the time to next read to 1 so that it will be read now.
            if not command.empty () : 
                commandData = command.get ()
                deviceId [commandData [0]] [1] = commandData [1]
                deviceId [commandData [0]] [2] = 1
                
           # Get the address, interval and time to next read for this sensor.
            address, interval, timeToRead = deviceId [sensor]
            
            # Is this sensor active?
            if interval >= 0:
            
                # Build the address string for this senor.
                address = '/uncached/28.' + address
                
                # Initialise temperature to a null string so we can check later if we have read a temperature.
                sensorTemperature = ''
                
                # If interval is zero it is maximum rate so read the sensor.
                if interval == 0 :
                    sensorTemperature = ow.Sensor(address).temperature
                    # Adjust the tick time to try and allow for the 0.75 second delay that occurs doing a 1 wire read.
                    tickTime = 0.25     
                
                # If the time to read is not at end decrement it.
                elif timeToRead > 1 :
                    deviceId [sensor][2] -= 1
                    
                # The time to read is at the end (1) reload it with the interval and read the sensor.
				# Note that reading the sensor returns a string.
                else :
                    deviceId [sensor][2] = interval
                    sensorTemperature = ow.Sensor(address).temperature                   
                    # Adjust the tick time to try and allow for the 0.75 second delay that occurs doing a 1 wire read.
                    tickTime = 0.25

                # If we have we got a temperature and space in the queue for this result send it. If for some reason
                # there is not space in the queue then this result is going to be discarded. This does not matter as
                # we will read the temperature again at the next interval time.
				# We convert the temperature string to an int via a float.
                if sensorTemperature and not result.full () :
                    result.put ((sensor, int (float (sensorTemperature))))
        
        # Wait for our tick time
        time.sleep (tickTime)

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


  