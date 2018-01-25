import commonNetControl as netControl

import commonStrings as STR
import gateCommands as commands
import gateGeneral as general
import gateControl
import gateLedControl as ledControl

# Get the ids we use for this controller. We use a backup code for development work.
from commonStrings import GATE_ID, BU_GATE_ID

import multiprocessing

################################################################################

# Set this true for the backup version when we are developing code. This will then only pass commands to other backup
# controllers. E.g. gsm backup.

useBackupVersion = False

################################################################################
'''
Flag to show if we are in pedestrian or vehicle mode. In pedestrian mode we only allow the open/close button to partially
open the left gate. This would normally used at night or during periods of no occupation to prevent vehicles from entering.
Pedestrian mode is activated using the PED line to the controller. Vehicle mode operates both gates to full open.
'''
pedestrianVehicleMode = 'VEHICLE'

################################################################################
'''
Flag to show if we are in daytime or nighttime mode. In nighttime mode we turn on the drive lights when the gate is NOT
closed. We also turn on the sign light.
'''
dayNightMode = STR.DAY

################################################################################
'''
Flag to show the current state of the gates. We hold the last message received from the gate process here.
'''
gateState = None

################################################################################
'''
Flag to show the last timed opening or closing of the gates. We keep this so that once we have opened or closed the
gates by timer we do not attempt to re-open or re-close them again as the user may have opened or closed them.
'''
lastTimedGateAction = None

################################################################################
'''
List of all the open TCP sockets. We run as a socket server so that other devices can connect to send commands and
receive data. The server socket and all the open client sockets will be kept here.
'''
tcpSocketList = []

################################################################################
'''
To perform control of leds and lights we use another process. To indicate which leds to control we use a multiprocessing
queue and send Commands as required. Using another process alows us to use a simple loop with a delay for flashing the leds.
'''
ledCommandQueue = multiprocessing.Queue ()
ledProcess = multiprocessing.Process (target = ledControl.LedControl, args = (ledCommandQueue,))

################################################################################
'''
To control opening and closing of the gates by command we use another process. The reason for this is that sometimes we
will not know the current state of the gates and in this situation we will need to go through a sequence of states to bring the
gates to a known state. By using a process we can run a state machine without needing to place it in the main program loop.
Commands to and status from the state machine will use multiprocessing queues.
'''
gateCommandQueue = multiprocessing.Queue ()
gateStatusQueue = multiprocessing.Queue ()
gateProcess = multiprocessing.Process (target = gateControl.GateControl, args = (gateCommandQueue, gateStatusQueue))

################################################################################
'''
To pass messages between the RPI controllers we use TCP sockets. All communication is handled in another process.
Commands to and status from the TCP routines will use multiprocessing queues.
'''
netSendQueue = multiprocessing.Queue ()
netReceiveQueue = multiprocessing.Queue ()

if useBackupVersion :
    netProcess = multiprocessing.Process (target = netControl.NetControlProcess,
                                                           args = (netSendQueue, netReceiveQueue, BU_GATE_ID))
else:
    netProcess = multiprocessing.Process (target = netControl.NetControlProcess,
                                                           args = (netSendQueue, netReceiveQueue, GATE_ID))


################################################################################
