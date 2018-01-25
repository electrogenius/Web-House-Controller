
################################################################################

# Definition of the RPI GPIO pin usage. We use board pin numbering. There are 4 inputs to the RPI which are driven by
# 4 output lines on a Texecom expander and there are 4 outputs from the RPI which drive 4 zones on a Texecom expander.

# GPIO output lines fed to Texecom expander zone inputs via opto buffer. High sets zone secure (closed).
TEXECOM_NET1_EXP3_ZONE_29 = 23  # Connected to a chime zone. We will pulse low when a gate button is pressed.
TEXECOM_NET1_EXP3_ZONE_30 = 21
TEXECOM_NET1_EXP3_ZONE_31 = 19  # Gate operate. High pulse will operate gate.
TEXECOM_NET1_EXP3_ZONE_32 = 15  # Power control to router. High will power down router. Low will power up router.

STATUS_LED_1 = 24

# GPIO input lines fed from Texecom expander outputs. Lines are active low as expander and opto buffer outputs are o/c.
TEXECOM_NET1_EXP3_OUTPUT_4 = 13 # Gate closed 
TEXECOM_NET1_EXP3_OUTPUT_5 = 11 # Power fail 
TEXECOM_NET1_EXP3_OUTPUT_6 = 7  # Fire alarm
TEXECOM_NET1_EXP3_OUTPUT_7 = 26 # Security alarm


################################################################################

# Time in seconds to turn off router to perform a reboot.

ROUTER_REBOOT_TIME = 15

################################################################################
