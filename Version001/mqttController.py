import time
import json
import socket
import paho.mqtt.client as mqttClient

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('4.2.2.1', 0))
#ourIp = s.getsockname()[0]
#ourIp = socket.gethostbyname(socket.gethostname())
isRpi = s.getsockname()[0] == "192.168.0.243"

if isRpi:
    import RPi.GPIO as GPIO

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
    restoredData = json.loads (message.payload).items()
    zone, state = restoredData[0]
    state = 0 if state == "on" else 1
    print 'Restored:',restoredData, zone,state,zonePin [zone]

    # Make sure the zone is a valid one.
    if zone in zonePin :
        print ("valid")
        if isRpi: GPIO.output (zonePin [zone], state)

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

brokerAddress = "192.168.0.244"  

client = mqttClient.Client(id)
client.on_connect = on_connect
client.on_message = on_message
client.connect(brokerAddress)
client.loop_start ()

try:
    while True:
        time.sleep(1)
 
except KeyboardInterrupt:
    print "exiting"
    client.disconnect()
    client.loop_stop()

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
