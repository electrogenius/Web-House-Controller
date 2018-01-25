import serial
################################################################################
#
# Function: InitialiseDisplayKeyboardModule ()
#
# Parameters: None
#
# Returns: serial port object - this is the port to the display module
#
# Globals modified:
#
# Comments: Opens the port to the display module.
#
################################################################################

def InitialiseDisplayKeyboardModule () :

    # Use serial port for communication
    serialPort = serial.Serial ("/dev/ttyAMA0", baudrate=9600, bytesize=8,parity='N',stopbits=1)
   
    # When we initialise the serial port the display module receives a spurious character so we feed it nulls
    # until it sends us back a NAK to get it back in sync.

    # Set a reasonable timeout for sending the nulls (the ser.read will cause the wait).
    serialPort.timeout = 0.5

    # Now wait for the display module to send the NAK (we do not check if it is a NAK)
    while (serialPort.read () =='') :
        serialPort.write (chr (0))
        
    while (serialPort.read () !='') :
        print '+'

    # Now set no timeout so we do not wait when looking for received data in the main loop.
    serialPort.timeout=0

    # Pass serial port object back to caller.
    return serialPort


################################################################################
#
# Function: WriteToDisplay (sequence)
#
# Parameters: sequence - string - this contains the bytes to send to the display, excluding the checksum
#                      
# Returns: Nothing
#
# Globals modified:
#
# Comments: Simply sends the string of bytes to the serial port and adds the checksum to the end
#
# TODO: SORT OUT RESPONSE TO ACK NAK
#
################################################################################

def WriteToDisplay (sequence) :

    checksum = 0
    
    # Only send the sequence if there is one.
    if sequence != '' :
    
        # Send all the message except the checksum. Calculate checksum as we go.
        for messageByte in sequence:
            IOModule.write (messageByte)
            checksum ^= ord (messageByte)

        # Now send the checksum.
        IOModule.write (chr (checksum))
        
        print hex (checksum)
        
        # Wait for ACK/NAK (TODO)
 #       CheckForSerialInput(GD.CHECK_FOR_ACK)
    
    return

################################################################################
#
# Function: DisplayForm (form)
#
# Parameters: form - integer - the form required
#
# Returns:
#
# Globals modified:
#
# Comments: Displays the required form on the display module
#
################################################################################

def DisplayForm (form) :
    # Build the form select message (excluding checksum).
    formSelectMessage = chr (0x01) + chr (0x0a) + chr (form) + chr (0x00) + chr (0x00)
    # Send to the display module.
    WriteToDisplay (formSelectMessage)
    

# Initialise the serial port and the display module.
IOModule = InitialiseDisplayKeyboardModule ()

DisplayForm (0x05)

IOModule.timeout = 1

# Try and get byte and then restore timeout to zero.
messageId = IOModule.read (4)
IOModule.timeout = 0

print messageId