#import subprocess
import ow

#p = subprocess.Popen("owread /28.898BD1010000/temperature", stdout=subprocess.PIPE, shell=True)
#(output, err) = p.communicate()
#print "Temprature 1 is", output

#output = subprocess.check_output ("owread /28.6DC326060000/temperature", shell=True)

#print "Temprature 2 is ", output

#print subprocess.check_output ("owdir", shell=True)

#print subprocess.check_output ("owread /28.6DC326060000/type", shell=True)

ow.init( 'localhost:4304' ) 

def ReadTemperatureSensor (sensor) :

    # Lookup table to convert our sensor id into 1 wire device id.
    device_Id = {
        SYSTEM_WOODBURNER_FLOW_TEMP :    'F610B7060000',
        SYSTEM_WOODBURNER_RETURN_TEMP : 'FFFD30070000'
    }
    
    # Create the string to send to OW and get the temperature.
    temperature = ow.Sensor('/uncached/28.'+ device_Id [sensor] ).temperature

    return temperature
    
    # Create the string to send to the OWFS and get the temperature.
    #temperature = float (subprocess.check_output ('owread /28.'+ device_Id [sensor] + '/temperature',shell = True))
    #temperature = 0

    return temperature

# Woodburner flow temperature from sensor mounted at woodburner flow pipe
SYSTEM_WOODBURNER_FLOW_TEMP = 54

# Woodburner flow temperature from sensor mounted at woodburner return pipe
SYSTEM_WOODBURNER_RETURN_TEMP = 55

a = ReadTemperatureSensor (SYSTEM_WOODBURNER_FLOW_TEMP)
b = ReadTemperatureSensor (SYSTEM_WOODBURNER_RETURN_TEMP)

print 'Flow',a,'Return',b
