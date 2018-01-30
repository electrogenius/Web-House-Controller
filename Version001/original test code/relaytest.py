import time
import smbus

I2CPort = smbus.SMBus (1)
address = 0x39
sequence = (0x20,0x40,0x10,0x08,0x04,0x02,0x01,0x80,0x00)
lastData1 = 0xff
lastData2 = 0xff

while True :
    portData =  I2CPort.read_byte_data (0x3c, 0xff)
    if lastData1 != portData :
        print '3C= ',hex(portData)
        lastData1 = portData
    portData =  I2CPort.read_byte_data (0x3d, 0xff)
    if lastData2 != portData :
        print '3D= ',hex(portData)
        lastData2 = portData
    
    for relayStatus in sequence :
        I2CPort.write_byte (address, ~relayStatus)
        time.sleep (.2)
    if address == 0x39 :
        address = 0x38
    elif address == 0x38 :
        address = 0x3b
    elif address == 0x3b :
        address = 0x3a
    else :
        address = 0x39
