import commonNetControl as netControl

# Get the id we want for this controller. We use a backup code for development work.
from commonStrings import GSM_ID, BU_GSM_ID

import multiprocessing
from StringIO import StringIO

# We may need to divert stdout so use StringIO to initialise a variable to use.
catchStdout = StringIO ()

################################################################################

# Set this true for the backup version when we are developing code. This will then only pass commands to other backup
# controllers. E.g. gate backup.

useBackupVersion = False

################################################################################

# List of the numbers to send input status change messages to. This list will be populated and depopulated by using the
# Add and Remove commands. At startup or whenever the list is changed it will be read from or written to calledNumbers.txt file.
calledNumbers = []

################################################################################

# List of the numbers we allow to access the system. This list will be populated and depopulated by using the Add and Remove
# Allowed commands. At startup or whenever the list is changed it will be read from or written to AllowedNumbers.txt file.
allowedNumbers = []

################################################################################

# To pass messages between the RPI controllers we use TCP sockets. All communication is handled in another process.
# Commands to and status from the TCP routines will use multiprocessing queues.

netSendQueue = multiprocessing.Queue ()
netReceiveQueue = multiprocessing.Queue ()

if useBackupVersion :
    netProcess = multiprocessing.Process (target = netControl.NetControlProcess,
                                                           args = (netSendQueue, netReceiveQueue, BU_GSM_ID))
else:
    netProcess = multiprocessing.Process (target = netControl.NetControlProcess,
                                                           args = (netSendQueue, netReceiveQueue, GSM_ID))

################################################################################

# We have a monitor command that directs STDOUT to a TCP connection so that we can monitor the operation of the
# controller. We wouuld need to do this as we cannot use the terminal if the controller has been started with systemd.
# we use this variable to hold the address of the last tcp connection that ran the monitor command.
savedTcpForMonitor = None

################################################################################

# Flag to indicate if we want to send alerts, such as gate button presses, to the sms numbers. In normal use we
# would not do this when the house is occupied, but when the house is empty we may want to get these alerts.
sendAlertsToSms = False

################################################################################

# Initialise the destination we are going to send a pending reply to. We will have a pending reply if we have 
# received a command that we are not able to reply to immediately. E.g. If we received an OPEN GATE command
# we would pass this to the gate controller. We would then have to wait for the gate controller to say when the
# gates are open before we could reply to the command. This would be a pending reply. For a pending reply
# we use a List. The 1st element is the type of reply - tcp, sms etc. The 2nd is the address - ip address and port,
# sms number etc or nothing for stdout. Note that we cannot cope with multiple pending replies.
pendingReplyDestination = [None, None]

################################################################################


    
