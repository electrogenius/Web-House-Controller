import time
import json
import socket
import paho.mqtt.client as mqttClient

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('4.2.2.1', 0))
#ourIp = s.getsockname()[0]
#ourIp = socket.gethostbyname(socket.gethostname())
isRpi = s.getsockname()[0] == "192.168.0.243"
print isRpi
if isRpi:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)
    id = "RPI"
else:
    id = "WIN"

def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
        print("Connected to broker from "+id)
        client.subscribe("zone/control/state") 
    else:
        print("Connection failed")
 
def on_message(client, userdata, message):
    print "Message received: "  + message.payload
    restoredData = json.loads (message.payload)
    print 'Restored:',restoredData

    if restoredData["zone"] == "on":
        print ("ON")
        if isRpi: GPIO.output (23,0)
    else:
        print ("OFF")
        if isRpi: GPIO.output (23,1)

brokerAddress = "192.168.0.244"  
 
client = mqttClient.Client(id)               #create new instance
client.on_connect = on_connect
client.on_message= on_message
client.connect(brokerAddress) 
client.loop_start ()

try:
    while True:
        time.sleep(1)
 
except KeyboardInterrupt:
    print "exiting"
    client.disconnect()
    client.loop_stop()
