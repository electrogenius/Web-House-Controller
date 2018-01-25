################################################################################

# Definition of the RPI GPIO pin usage. We use board pin numbering.

# GPIO output lines. Outputs are active high.
START_GATE_OUTPUT = 38          # Start input to gate controller. N.B. alternate action input. open, stop, close, stop, open etc.
STOP_GATE_OUTPUT = 36           # Stop input to gate controller.
PED_OUTPUT = 40                     # PEDestrian input to gate controller.
GREEN_LED_OUTPUT = 32          # Green LED.
RED_LED_OUTPUT = 18             # Red LED.
DRIVE_LED_OUTPUT = 12         # Lights on drive.
FRONT_LED_OUTPUT = 22        # Lights either side of house sign.
SIGN_LED_OUTPUT = 16          # Lights illuminating house sign.
STATUS_LED_1 = 26               # Diagnostic LED on output board of controller.
STATUS_LED_2 = 29               # Diagnostic LED on input board of controller.

# GPIO input lines. Inputs are active low  due to inversion in opto.
GATE_MOVING_INPUT = 37                        # Active when either gate moving from lamp output of gate controller.
STOP_CALL_BUTTON_INPUT = 33                  # Active when NEITHER stop button pressed as buttons are wired in series as n/c.
OPEN_CLOSE_BUTTON_INPUT = 35               # Active when EITHER open button pressed as buttons are wired in parallel as n/o.
LEFT_GATE_CLOSED_SWITCH_INPUT = 31      # Active when left gate is closed from reed switch.
RIGHT_GATE_CLOSED_SWITCH_INPUT = 15   # Active when right gate is closed from reed switch.
LEFT_GATE_OPEN_SWITCH_INPUT = 13         # Active when left gate is fully open from reed switch.
RIGHT_GATE_OPEN_SWITCH_INPUT = 11      # Active when right gate is fully open from reed switch.
EXTERIOR_LIGHTS_RELAY_INPUT = 7          # Active when exterior lights are on. From relay in garage.

################################################################################
