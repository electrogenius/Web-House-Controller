print 'Loaded GD module'

################################################################################
## This is a temp bit of code so we can switch between our dev board and the real heating system. We use the ip address
## to load different values for each board such as delays and 1-wire addresses.
import socket
def IfDev () :
    s = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    s.connect (("8.8.8.8", 80))
    return s.getsockname () [0] [10:13] == '245'
 ################################################################################
  
# We keep all our globals and "constants" here

################################################################################

KEYVALUE_NONE = 0

# Rad Zone select keys are 1 - 14
KEYVALUE_RAD_BED_1 = 1
KEYVALUE_RAD_BED_2 = 2
KEYVALUE_RAD_BED_3 = 3
KEYVALUE_RAD_BED_4 = 4
KEYVALUE_RAD_BED_5 = 5
KEYVALUE_RAD_BATH_1 = 6
KEYVALUE_RAD_BATH_2 = 7
KEYVALUE_RAD_BATH_3_4 = 8
KEYVALUE_RAD_KITCHEN = 9
KEYVALUE_RAD_DINING = 10 
KEYVALUE_RAD_LIBRARY= 11
KEYVALUE_RAD_CLOAK = 12
KEYVALUE_RAD_SITTING = 13
KEYVALUE_RAD_HALL_UP = 14

KEY_GROUP_RADS = tuple (range (KEYVALUE_RAD_BED_1, KEYVALUE_RAD_HALL_UP+1))

# Ufh Zone select keys are 15 - 30
KEYVALUE_UFH_BED_1 = 15
KEYVALUE_UFH_BED_2 = 16
KEYVALUE_UFH_BED_3 = 17
KEYVALUE_UFH_BED_4 = 18
KEYVALUE_UFH_BED_5 = 19
KEYVALUE_UFH_BATH_1 = 20
KEYVALUE_UFH_BATH_2 = 21
KEYVALUE_UFH_BATH_3_4 = 22
KEYVALUE_UFH_KITCHEN = 23
KEYVALUE_UFH_DINING = 24
KEYVALUE_UFH_LIBRARY= 25
KEYVALUE_UFH_CLOAK = 26
KEYVALUE_UFH_SITTING = 27
KEYVALUE_UFH_HALL_UP = 28
KEYVALUE_UFH_HALL_DOWN = 29
KEYVALUE_UFH_HALL_SITTINGX = 30

KEY_GROUP_UFH = tuple (range (KEYVALUE_UFH_BED_1, KEYVALUE_UFH_HALL_SITTINGX+1))

# Immersion select keys.
KEYVALUE_IMM_1_TIME = 31
KEYVALUE_IMM_2_TIME = 32
KEYVALUE_IMM_3_TIME = 33
KEYVALUE_IMM_4_TIME = 34

KEY_GROUP_IMMERSIONS = tuple (range (KEYVALUE_IMM_1_TIME, KEYVALUE_IMM_4_TIME+1))

KEY_GROUP_ALL_ZONES = KEY_GROUP_RADS + KEY_GROUP_UFH + KEY_GROUP_IMMERSIONS
                                            
# Numeric keys are 50 - 59.
KEYVALUE_NUMERIC_0 = 50
KEYVALUE_NUMERIC_1 = 51
KEYVALUE_NUMERIC_2 = 52
KEYVALUE_NUMERIC_3 = 53
KEYVALUE_NUMERIC_4 = 54
KEYVALUE_NUMERIC_5 = 55
KEYVALUE_NUMERIC_6 = 56
KEYVALUE_NUMERIC_7 = 57
KEYVALUE_NUMERIC_8 = 58
KEYVALUE_NUMERIC_9 = 59

KEY_GROUP_NUMERIC = tuple (range (KEYVALUE_NUMERIC_0, KEYVALUE_NUMERIC_9+1))

# Day of week keys are 60 - 69.
KEYVALUE_DAY_MONDAY = 60
KEYVALUE_DAY_TUESDAY =61
KEYVALUE_DAY_WEDNESDAY = 62
KEYVALUE_DAY_THURSDAY = 63
KEYVALUE_DAY_FRIDAY = 64
KEYVALUE_DAY_SATURDAY = 65
KEYVALUE_DAY_SUNDAY = 66
KEYVALUE_DAY_MON_FRI = 67
KEYVALUE_DAY_SAT_SUN =68
KEYVALUE_DAY_EVERY =69

KEY_GROUP_DAYS = tuple (range (KEYVALUE_DAY_MONDAY, KEYVALUE_DAY_EVERY+1))

# Keyboard control and edit codes.
KEYVALUE_PROGRAM = 70
KEYVALUE_SYSTEM = 71
KEYVALUE_BOOST = 72
KEYVALUE_MODE = 73
KEYVALUE_CAN_RES = 74
KEYVALUE_NEXT_PROGRAM_ENTRY = 75
KEYVALUE_PREV_PROGRAM_ENTRY = 76
KEYVALUE_NEW = 77
KEYVALUE_ON_AT = 79
KEYVALUE_OFF_AT = 80
KEYVALUE_DAY = 81
KEYVALUE_ENABLE_DISABLE = 82
KEYVALUE_CLEAR = 83
KEYVALUE_SAVE = 84
KEYVALUE_AUTO_MANUAL = 85
KEYVALUE_UFH = 86
KEYVALUE_RAD = 87
KEYVALUE_NEXT_STATUS_ENTRY = 88
KEYVALUE_PREV_STATUS_ENTRY = 89

# System keys start from here.
SYSTEM_KEY_START = 100

KEYVALUE_WAKEUP = 100

# Main System functions
KEYVALUE_SYSTEM_OFF =101
KEYVALUE_SYSTEM_OPTIONS = 102
KEYVALUE_AUTO_MODE = 103
KEYVALUE_AUTO_OPTIONS = 104
KEYVALUE_MANUAL_MODE = 105
KEYVALUE_MANUAL_OPTIONS = 106
KEYVALUE_HOLIDAY_MODE = 107
KEYVALUE_HOLIDAY_OPTIONS = 108

# Manual mode options
KEYVALUE_T1_TO_HEAT = 110
KEYVALUE_OIL_TO_T1 = 111
KEYVALUE_T2_TO_HEAT = 112
KEYVALUE_OIL_TO_T2 = 113
KEYVALUE_OIL_TO_HEAT = 114
KEYVALUE_OIL_OFF =115
KEYVALUE_MANUAL_OVERRIDE = 143
KEYVALUE_DISPLAY_STATUS = 180

# Auto mode options
KEYVALUE_HEATING_SOURCES = 118
KEYVALUE_T1_SOURCES = 119
KEYVALUE_T2_SOURCES = 120
KEYVALUE_BOILER_PRIORITY = 121

# System options
KEYVALUE_IMMERSION_TIMES = 122
KEYVALUE_WINTER_PERIOD = 123

# Menu exit keys
KEYVALUE_EXIT = 78
KEYVALUE_RETURN_TO_SYSTEM_EXIT = 109
KEYVALUE_FINISHED = 139
KEYVALUE_RAD_SELECT_EXIT = 140
KEYVALUE_UFH_SELECT_EXIT = 141
KEYVALUE_EDIT_EXIT = 142
KEYVALUE_MANUAL_CONTROL_MAIN_MENU_EXIT = 144
KEYVALUE_MANUAL_CONTROL_OPTION_EXIT = 160
KEYVALUE_RETURN_TO_SYSTEM_OPTIONS_EXIT = 138

# Manual Control main menu
KEYVALUE_WOODBURNER_CONTROL = 116
KEYVALUE_IMMERSION_CONTROL =117
KEYVALUE_HEATING_CONTROL = 157
KEYVALUE_BOILER_CONTROL = 158
KEYVALUE_TANK_1_CONTROL = 159
KEYVALUE_TANK_2_CONTROL = 132

# Immersion manual control options
KEYVALUE_IMM_1_ON = 124
KEYVALUE_IMM_2_ON = 125
KEYVALUE_IMM_3_ON = 126
KEYVALUE_IMM_4_ON = 127
KEYVALUE_IMM_1_OFF = 128
KEYVALUE_IMM_2_OFF = 129
KEYVALUE_IMM_3_OFF = 130
KEYVALUE_IMM_4_OFF = 131

# Woodburner manual control options
KEYVALUE_WB_PUMP_1_ON = 133
KEYVALUE_WB_PUMP_2_ON = 134
KEYVALUE_WB_PUMP_1_OFF = 135
KEYVALUE_WB_PUMP_2_OFF = 136
KEYVALUE_WB_ALARM = 137

# Tank 1 manual control options
KEYVALUE_TANK_1_PUMP_ON = 145
KEYVALUE_TANK_1_PUMP_OFF = 146
KEYVALUE_V1_EXT_TO_T1 = 147
KEYVALUE_V1_EXT_TO_HEATING = 148

# Tank 2 manual control options
KEYVALUE_TANK_2_PUMP_ON = 149
KEYVALUE_TANK_2_PUMP_OFF = 150
KEYVALUE_V2_T2_TO_INT = 151
KEYVALUE_V2_T2_RECYCLE = 152

# Boiler manual control options
KEYVALUE_BOILER_ON = 153
KEYVALUE_BOILER_OFF = 154
KEYVALUE_V3_BOILER_TO_T2 = 155
KEYVALUE_V3_BOILER_TO_INT = 156

# Heating manual control options
KEYVALUE_RAD_PUMP_ON = 161
KEYVALUE_RAD_PUMP_OFF = 162
KEYVALUE_UFH_PUMP_ON = 163
KEYVALUE_UFH_PUMP_OFF = 164

# Status select options
KEYVALUE_IMM_1_STATUS = 165
KEYVALUE_IMM_2_STATUS = 166
KEYVALUE_IMM_3_STATUS = 167
KEYVALUE_IMM_4_STATUS = 168
KEYVALUE_WOODBURNER_STATUS = 169
KEYVALUE_BOILER_STATUS = 170
KEYVALUE_TANK_1_STATUS = 171
KEYVALUE_TANK_2_STATUS = 172
KEYVALUE_RADS_STATUS = 173
KEYVALUE_UFH_STATUS = 174
KEYVALUE_HW_STATUS = 175
KEYVALUE_SYSTEM_STATUS = 176
KEYVALUE_BATH_1_STATUS = 177
KEYVALUE_BATH_2_STATUS = 178
KEYVALUE_BATH_3_4_STATUS = 179

KEY_GROUP_STATUS =  tuple (range (KEYVALUE_IMM_1_STATUS, KEYVALUE_BATH_3_4_STATUS+1))

## 181 is next to use

# Unsued keys
KEYVALUE_NOT_USED_B1 = 227
KEYVALUE_NOT_USED_B2 = 228
KEYVALUE_NOT_USED_B3 = 229
KEYVALUE_NOT_USED_B4 = 230
KEYVALUE_NOT_USED_B5 = 231
KEYVALUE_NOT_USED_B6 = 232
KEYVALUE_NOT_USED_B7 = 233
KEYVALUE_NOT_USED_B8 = 234
KEYVALUE_NOT_USED_B9 = 235
KEYVALUE_NOT_USED_B10 = 236
KEYVALUE_NOT_USED_B11 = 237
KEYVALUE_NOT_USED_B12 = 238
KEYVALUE_NOT_USED_B13 = 239
KEYVALUE_NOT_USED_B14 = 240
KEYVALUE_NOT_USED_B15 = 241
KEYVALUE_NOT_USED_B16 = 242
KEYVALUE_NOT_USED_B17 = 243
KEYVALUE_NOT_USED_B18 = 244
KEYVALUE_NOT_USED_B19 = 245
KEYVALUE_NOT_USED_B20 = 246
KEYVALUE_NOT_USED_B21 = 247
KEYVALUE_NOT_USED_B22 = 248
KEYVALUE_NOT_USED_B23 = 249
KEYVALUE_NOT_USED_B24 = 250
KEYVALUE_NOT_USED_B25 = 251
KEYVALUE_NOT_USED_B26 = 252
KEYVALUE_NOT_USED_B27 = 253
KEYVALUE_NOT_USED_B28 = 254
KEYVALUE_NOT_USED = 255

################################################################################
##
## Keyboard control code groups. 
##
################################################################################

KEY_GROUP_WAITING_MODE = (KEYVALUE_RAD, KEYVALUE_UFH, KEYVALUE_SYSTEM)

KEY_GROUP_SYSTEM_MODE = (KEYVALUE_SYSTEM_OFF, 
                                                 KEYVALUE_AUTO_MODE,
                                                 KEYVALUE_MANUAL_MODE,
                                                 KEYVALUE_HOLIDAY_MODE)

KEY_GROUP_HEATING_MODE = (KEYVALUE_T1_TO_HEAT,
                                                   KEYVALUE_T2_TO_HEAT,
                                                   KEYVALUE_OIL_TO_HEAT)
                                                   
KEY_GROUP_BOILER_MODE = (KEYVALUE_OIL_TO_HEAT,
                                                 KEYVALUE_OIL_TO_T1,
                                                 KEYVALUE_OIL_TO_T2,
                                                 KEYVALUE_OIL_OFF)

KEY_GROUP_MANUAL_MODE = (KEYVALUE_T1_TO_HEAT,
                                                 KEYVALUE_T2_TO_HEAT,
                                                 KEYVALUE_OIL_TO_HEAT,
                                                 KEYVALUE_OIL_TO_T1,
                                                 KEYVALUE_OIL_TO_T2,
                                                 KEYVALUE_OIL_OFF)
                                                   
KEY_GROUP_ALL_IMM = (KEYVALUE_IMM_1_ON, KEYVALUE_IMM_2_ON, KEYVALUE_IMM_3_ON, KEYVALUE_IMM_4_ON,
                                      KEYVALUE_IMM_1_OFF, KEYVALUE_IMM_2_OFF, KEYVALUE_IMM_3_OFF, KEYVALUE_IMM_4_OFF)
                                        
KEY_GROUP_ALL_WB = (KEYVALUE_WB_PUMP_1_ON, KEYVALUE_WB_PUMP_2_ON,
                                     KEYVALUE_WB_PUMP_1_OFF, KEYVALUE_WB_PUMP_2_OFF)
                                      
KEY_GROUP_ALL_T1 = (KEYVALUE_TANK_1_PUMP_ON, KEYVALUE_V1_EXT_TO_T1,
                                    KEYVALUE_TANK_1_PUMP_OFF, KEYVALUE_V1_EXT_TO_HEATING)
                                       
KEY_GROUP_ALL_T2 = (KEYVALUE_TANK_2_PUMP_ON, KEYVALUE_V2_T2_TO_INT,
                                    KEYVALUE_TANK_2_PUMP_OFF, KEYVALUE_V2_T2_RECYCLE)
                                       
KEY_GROUP_ALL_BOILER = (KEYVALUE_BOILER_ON, KEYVALUE_V3_BOILER_TO_INT,
                                           KEYVALUE_BOILER_OFF, KEYVALUE_V3_BOILER_TO_T2)
                                       
KEY_GROUP_ALL_HEATING = (KEYVALUE_RAD_PUMP_ON, KEYVALUE_UFH_PUMP_ON,
                                              KEYVALUE_RAD_PUMP_OFF, KEYVALUE_UFH_PUMP_OFF)
                                              
KEY_GROUP_MANUAL_CONTROL_SELECT = (KEYVALUE_WOODBURNER_CONTROL, KEYVALUE_IMMERSION_CONTROL,
                                                                  KEYVALUE_HEATING_CONTROL, KEYVALUE_TANK_1_CONTROL,
                                                                  KEYVALUE_BOILER_CONTROL, KEYVALUE_TANK_2_CONTROL)

KEY_GROUP_ALL_MANUAL_OVERRIDE =  (KEY_GROUP_ALL_WB + KEY_GROUP_ALL_IMM +
                                                              KEY_GROUP_ALL_HEATING + KEY_GROUP_ALL_T1 +
                                                              KEY_GROUP_ALL_BOILER + KEY_GROUP_ALL_T2)
                                              
################################################################################
##
## System control codes. These are useds as keys to the dictionaries of system control bits objects.
## These objects control either output lines, input lines lines or configuration bits.
##
################################################################################

# Value for no control code
SYSTEM_NONE = 0

## HARDWARE OUTPUTS

# Turn immersion 1 on or off. (Output)
SYSTEM_IMM_1 = 1

# Turn immersion 2 on or off. (Output)
SYSTEM_IMM_2 = 2

# Turn immersion 3 on or off. N.B. currently will also operate immersion 4. (Output)
SYSTEM_IMM_3 = 3

# Turn immersion 4 on or off. N.B. currently not used Imm 4 operates with Imm 3 as above (Output)
SYSTEM_IMM_4 = 4

# Turn the pump on or off that pumps the output of the boiler or tank 2 to the house. (Output)
SYSTEM_TANK_2_PUMP = 5

# Turn the pump on or off that pumps the output of tank 1 through the hot water heat exchanger. This pump is also
# used when either immersion 1 or 2 is on to circulate the water in tank 1 so the whole tank is heated. (Output)
SYSTEM_TANK_1_PUMP = 6

# Turn the oil boiler on and off. (Output)
SYSTEM_BOILER_ON = 7

# Select boiler output either to tank 2 or feed it directly to the house to supply tank 1 or the heating circuits.
# If the boiler is fed to the house then tank 2 cannot feed tank 1 or heating circuits as they share the same pipe. (Output)
SYSTEM_V3_BOILER_TO_INT = 8

# Select boiler / tank 2 to feed the heating circuits. Boiler / tank 2 can feed either the heating circuits or tank 1 but
# not both together. Controlled by a pair of valves designated as Valve 1 (Output)
SYSTEM_V1_EXT_TO_HEATING = 9

# Select boiler / tank 2 to feed tank 1. Boiler / tank 2 can feed either the heating circuits or tank 1 but not both together.
# Controlled by a pair of valves designated as Valve 1  (Output)
SYSTEM_V1_EXT_TO_TANK_1 = 10

# Turn the sitting room wood burner pump 1 on or off. The wood burner has 2 pumps for safety so that flow through the
# back boiler can be maintained even if a pump fails. In normal use each pump is used alternately. (Output)
SYSTEM_WOODBURNER_PUMP_1 = 11

# Turn the sitting room wood burner pump 2 on or off. The wood burner has 2 pumps for safety so that flow through the
# back boiler can be maintained even if a pump fails. In normal use each pump is used alternately. (Output)
SYSTEM_WOODBURNER_PUMP_2 = 12

# Turn the pump that feeds the radiator systen on or off. (Output)
SYSTEM_RAD_PUMP = 49

# Turn the pump that feeds the ufh systen on or off. (Output)
SYSTEM_UFH_PUMP = 50

# Control line to external to switch valve to send feed to internal rather than recirculate. (NOT USED AT PRESENT)
SYSTEM_EXT_TO_INT = 51


## HARDWARE INPUTS

# A radiator heating circuit is active. (Input)
SYSTEM_RAD_DEMAND = 13

# A ufh heating circuit is active. (Input)
SYSTEM_UFH_DEMAND = 14

# Domestic HW is required. (Input)
SYSTEM_HW_DEMAND = 15

# Pulse input from heating flow meter. (Input)
HEATING_FLOW_PULSE = 16

# Immersion 1 is at required temperature. (Input)
SYSTEM_IMM_1_MAX = 17

# Immersion 2 is at required temperature. (Input)
SYSTEM_IMM_2_MAX = 18

# Wood burner flow is detected. (Input)
SYSTEM_WOODBURNER_FLOW_DETECT = 19

# Woodburner temperature sensor connected OK. (Input)
##SYSTEM_WOODBURNER_SENSOR_CONNECTED = 20

# Mains OK. (Input)
SYSTEM_MAINS_FAIL = 21

# Heating temperature sensor connected OK. (Input)
##SYSTEM_HEATING_SENSOR_CONNECTED = 22

# Tank 1 temperature sensor connected OK. (Input)
##SYSTEM_TANK_1_SENSOR_CONNECTED = 23

# Shower in bath 3 or 4 is active. (Input)
SYSTEM_BATH_3_4_SHOWER_ACTIVE = 24

# Shower in bath 2 is active. (Input)
SYSTEM_BATH_2_SHOWER_ACTIVE = 25

# Shower in bath 1 is active. (Input)
SYSTEM_BATH_1_SHOWER_ACTIVE = 26

## SYSTEM CONFIG

# System off. (Config)
SYSTEM_OFF_MODE = 27

# Auto mode. (Config)
SYSTEM_AUTO_MODE = 28

# Manual mode. (Config)
SYSTEM_MANUAL_MODE = 29

# Holiday mode. (Config)
SYSTEM_HOLIDAY_MODE = 30

## MANUAL MODE CONFIG

# Tank 1 to Heating. (Manual mode)
SYSTEM_MANUAL_TANK_1_TO_HEATING = 31

# Tank 2 to Heating. (Manual mode)
SYSTEM_MANUAL_TANK_2_TO_HEATING = 32

# Oil boiler to heating. (Manual mode)
SYSTEM_MANUAL_OIL_BOILER_TO_HEATING = 33

# Oil boiler to Tank 1 or heating. Controlled by a pair of valves designated as Valve 3 (Manual mode)
SYSTEM_MANUAL_OIL_BOILER_TO_TANK1 = 34

# Oil boiler to Tank 2. Controlled by a pair of valves designated as Valve 3 (Manual mode)
SYSTEM_MANUAL_OIL_BOILER_TO_TANK2 = 35

# Oil boiler off. (Manual mode)
SYSTEM_MANUAL_OIL_BOILER_OFF = 36

## AUTO MODE CONFIG

# Tank 1 to Heating. (Auto mode)
SYSTEM_AUTO_TANK_1_TO_HEATING = 37

# Tank 2 to Heating. (Auto mode)
SYSTEM_AUTO_TANK_2_TO_HEATING = 38

# Oil boiler to heating. (Auto mode)
SYSTEM_AUTO_OIL_BOILER_TO_HEATING = 39

# Oil boiler to Tank 1 or heating. Controlled by a pair of valves designated as Valve 3 (Auto mode)
SYSTEM_AUTO_OIL_BOILER_TO_TANK1 = 40

# Oil boiler to Tank 2. Controlled by a pair of valves designated as Valve 3 (Auto mode)
SYSTEM_AUTO_OIL_BOILER_TO_TANK2 = 41

# Oil boiler off. (Auto mode)
SYSTEM_AUTO_OIL_BOILER_OFF = 42

## HOLIDAY MODE CONFIG

# Tank 1 to Heating. (Holiday mode)
SYSTEM_HOLIDAY_TANK_1_TO_HEATING = 43

# Tank 2 to Heating. (Holiday mode)
SYSTEM_HOLIDAY_TANK_2_TO_HEATING = 44

# Oil boiler to heating. (Holiday mode)
SYSTEM_HOLIDAY_OIL_BOILER_TO_HEATING = 45

# Oil boiler to Tank 1 or heating. Controlled by a pair of valves designated as Valve 3 (Holiday mode)
SYSTEM_HOLIDAY_OIL_BOILER_TO_TANK1 = 46

# Oil boiler to Tank 2. Controlled by a pair of valves designated as Valve 3 (Holiday mode)
SYSTEM_HOLIDAY_OIL_BOILER_TO_TANK2 = 47

# Oil boiler off. (Holiday mode)
SYSTEM_HOLIDAY_OIL_BOILER_OFF = 48

## FUTURE USE LINES - NOT CURRENTLY USED
SYSTEM_IMM_3_MAX = 52
SYSTEM_IMM_4_MAX = 53

# Woodburner flow temperature from sensor mounted at woodburner flow pipe
SYSTEM_WOODBURNER_FLOW_TEMP = 54

# Woodburner flow temperature from sensor mounted at woodburner return pipe
SYSTEM_WOODBURNER_RETURN_TEMP = 55


## LAST USED VALUE IS 55



## CONTROL GROUPS

IMMERSION_MANUAL_OVERRIDE_GROUP = (SYSTEM_IMM_1, SYSTEM_IMM_2, SYSTEM_IMM_3, SYSTEM_IMM_4)
WOODBURNER_MANUAL_OVERRIDE_GROUP = (SYSTEM_WOODBURNER_PUMP_1, SYSTEM_WOODBURNER_PUMP_2)
TANK_1_MANUAL_OVERRIDE_GROUP = (SYSTEM_TANK_1_PUMP, SYSTEM_V1_EXT_TO_TANK_1)
TANK_2_MANUAL_OVERRIDE_GROUP = (SYSTEM_TANK_2_PUMP, SYSTEM_EXT_TO_INT)
BOILER_MANUAL_OVERRIDE_GROUP = (SYSTEM_BOILER_ON, SYSTEM_V3_BOILER_TO_INT)
HEATING_MANUAL_OVERRIDE_GROUP = (SYSTEM_RAD_PUMP, SYSTEM_UFH_PUMP)

ALL_MANUAL_OVERRIDE_GROUPS = (WOODBURNER_MANUAL_OVERRIDE_GROUP, IMMERSION_MANUAL_OVERRIDE_GROUP, 
                                                      HEATING_MANUAL_OVERRIDE_GROUP, TANK_1_MANUAL_OVERRIDE_GROUP,
                                                      BOILER_MANUAL_OVERRIDE_GROUP, TANK_2_MANUAL_OVERRIDE_GROUP)

DISABLED_MANUAL_OVERRIDE_GROUPS = (TANK_1_MANUAL_OVERRIDE_GROUP + TANK_2_MANUAL_OVERRIDE_GROUP +
                                                                BOILER_MANUAL_OVERRIDE_GROUP)

SYSTEM_CONTROL_GROUP = (SYSTEM_OFF_MODE, SYSTEM_AUTO_MODE, SYSTEM_MANUAL_MODE, SYSTEM_HOLIDAY_MODE)

HEATING_MANUAL_CONTROL_GROUP = (SYSTEM_MANUAL_TANK_1_TO_HEATING, SYSTEM_MANUAL_TANK_2_TO_HEATING,
                                                            SYSTEM_MANUAL_OIL_BOILER_TO_HEATING)

HEATING_AUTO_CONTROL_GROUP = (SYSTEM_AUTO_TANK_1_TO_HEATING, SYSTEM_AUTO_TANK_2_TO_HEATING,
                                                        SYSTEM_AUTO_OIL_BOILER_TO_HEATING)

HEATING_HOLIDAY_CONTROL_GROUP = (SYSTEM_HOLIDAY_TANK_1_TO_HEATING, SYSTEM_HOLIDAY_TANK_2_TO_HEATING,
                                                             SYSTEM_HOLIDAY_OIL_BOILER_TO_HEATING)

BOILER_MANUAL_CONTROL_GROUP = (SYSTEM_MANUAL_OIL_BOILER_TO_HEATING, SYSTEM_MANUAL_OIL_BOILER_TO_TANK1,
                                                          SYSTEM_MANUAL_OIL_BOILER_TO_TANK2, SYSTEM_MANUAL_OIL_BOILER_OFF)

BOILER_AUTO_CONTROL_GROUP = (SYSTEM_AUTO_OIL_BOILER_TO_HEATING, SYSTEM_AUTO_OIL_BOILER_TO_TANK1,
                                                      SYSTEM_AUTO_OIL_BOILER_TO_TANK2, SYSTEM_AUTO_OIL_BOILER_OFF)

BOILER_HOLIDAY_CONTROL_GROUP = (SYSTEM_HOLIDAY_OIL_BOILER_TO_HEATING, SYSTEM_HOLIDAY_OIL_BOILER_TO_TANK1,
                                                           SYSTEM_HOLIDAY_OIL_BOILER_TO_TANK2, SYSTEM_HOLIDAY_OIL_BOILER_OFF)

ALL_MANUAL_CONTROL_GROUP = (SYSTEM_MANUAL_TANK_1_TO_HEATING, SYSTEM_MANUAL_TANK_2_TO_HEATING,
                                                    SYSTEM_MANUAL_OIL_BOILER_TO_HEATING, SYSTEM_MANUAL_OIL_BOILER_TO_TANK1,
                                                    SYSTEM_MANUAL_OIL_BOILER_TO_TANK2, SYSTEM_MANUAL_OIL_BOILER_OFF)


SYSTEM_OUTPUT_GROUP = (SYSTEM_IMM_1, SYSTEM_IMM_2, SYSTEM_IMM_3, SYSTEM_IMM_4, SYSTEM_TANK_2_PUMP,
                                          SYSTEM_TANK_1_PUMP, SYSTEM_BOILER_ON, SYSTEM_V3_BOILER_TO_INT, SYSTEM_V1_EXT_TO_HEATING,
                                          SYSTEM_V1_EXT_TO_TANK_1, SYSTEM_WOODBURNER_PUMP_1, SYSTEM_WOODBURNER_PUMP_2,
                                          SYSTEM_RAD_PUMP, SYSTEM_UFH_PUMP, SYSTEM_EXT_TO_INT)
                                          
SYSTEM_INPUT_GROUP = (SYSTEM_RAD_DEMAND, SYSTEM_UFH_DEMAND, SYSTEM_HW_DEMAND, HEATING_FLOW_PULSE,
                                        SYSTEM_IMM_1_MAX, SYSTEM_IMM_2_MAX, SYSTEM_WOODBURNER_FLOW_DETECT, SYSTEM_MAINS_FAIL,
##                                        SYSTEM_WOODBURNER_SENSOR_CONNECTED, SYSTEM_TANK_1_SENSOR_CONNECTED,
                                        SYSTEM_BATH_1_SHOWER_ACTIVE, SYSTEM_BATH_2_SHOWER_ACTIVE, SYSTEM_BATH_3_4_SHOWER_ACTIVE)

SYSTEM_PULSED_OUTPUTS_GROUP = (SYSTEM_V1_EXT_TO_HEATING, SYSTEM_V1_EXT_TO_TANK_1)

SYSTEM_TEMPERATURE_GROUP = (SYSTEM_WOODBURNER_FLOW_TEMP, SYSTEM_WOODBURNER_RETURN_TEMP)

KEY_TO_CONTROL_BIT_LOOKUP  = {
                                                        KEYVALUE_IMM_1_TIME : SYSTEM_IMM_1,
                                                        KEYVALUE_IMM_2_TIME : SYSTEM_IMM_2,
                                                        KEYVALUE_IMM_3_TIME : SYSTEM_IMM_3,
                                                        KEYVALUE_IMM_4_TIME : SYSTEM_IMM_4,
                                                        KEYVALUE_SYSTEM_OFF : SYSTEM_OFF_MODE,
                                                        KEYVALUE_AUTO_MODE : SYSTEM_AUTO_MODE,
                                                        KEYVALUE_MANUAL_MODE : SYSTEM_MANUAL_MODE,
                                                        KEYVALUE_HOLIDAY_MODE : SYSTEM_HOLIDAY_MODE
                                                    }


################################################################################

BIT_LOW = 0
BIT_HIGH = 1

BIT_OVERRIDE_LOW = 0
BIT_OVERRIDE_HIGH = 1
BIT_OVERRIDE_NONE = 2

BIT_NOT_TIMED = -1
BIT_TIMING_FINISHED = 0
BIT_SET_TIMING_05 = 5
BIT_SET_TIMING_60 = 60

# I2C addresses and bit definitions

I2C_ADDRESS_0X38 = 0x38 #ufh zone relays
I2C_ADDRESS_0X39 = 0x39 #rad zone relays
I2C_ADDRESS_0X3A = 0x3A #system outputs
I2C_ADDRESS_0X3B = 0x3B #system outputs
I2C_ADDRESS_0X3C = 0x3C #system inputs
I2C_ADDRESS_0X3D = 0x3D #system inputs
I2C_ADDRESS_0X3E = 0x3E #system inputs

BIT_0_MASK = 0x01
BIT_1_MASK = 0x02
BIT_2_MASK = 0x04
BIT_3_MASK = 0x08
BIT_4_MASK = 0x10
BIT_5_MASK = 0x20
BIT_6_MASK = 0x40
BIT_7_MASK = 0x80

# 1 wire addresses
if IfDev () :
    OW_WOODBURNER_FLOW = '0F7AD1010000'
    OW_WOODBURNER_RETURN = '3E5A33070000'
# Use heating box internal sensors for now
    OW_WOODBURNER_FLOW = '898BD1010000'
    OW_WOODBURNER_RETURN = '548E31070000'
# Use development box 1 internal sensors for now
    OW_WOODBURNER_FLOW = '422AB6060000'
    OW_WOODBURNER_RETURN = '5D63B6060000'
else :
    OW_WOODBURNER_FLOW = 'F610B7060000'
    OW_WOODBURNER_RETURN = 'FFFD30070000'

################################################################################
# Zone codes
NO_ZONE = -1
RAD_BED1 = 0

# Values for zone setting
SET_ZONE_INACTIVE = 0
SET_ZONE_ACTIVE = 1

# Status values returned from zone checking
STATUS_ZONE_NOT_ACTIVE = 0
STATUS_ZONE_ACTIVE = 1
STATUS_MANUAL_MODE = 2
STATUS_BOOST_MODE = 3
STATUS_ZONE_CANCELLED = 4
STATUS_PROGRAM_FILE_ERROR = 5
DAY_TIME_NOT_VALID = -1

# Values for current mode. 
MODE_NONE = 0
MODE_RUN = 1
MODE_RAD_WAITING_ZONE_SELECT = 2
MODE_UFH_WAITING_ZONE_SELECT = 3
MODE_OFF_MODE_SELECT = 4
MODE_RAD_ZONE_SELECT = 8
MODE_UFH_ZONE_SELECT = 9
MODE_PROG_TIME = 10
MODE_PROG_DAY = 11
MODE_PROG_ON_AT = 12
MODE_PROG_OFF_AT = 13
MODE_PROG_DAYS_ON = 14
MODE_MANUAL_OPTIONS = 15
MODE_AUTO_OPTIONS = 16
MODE_SYSTEM_OPTIONS = 17
MODE_HOLIDAY_OPTIONS = 18
MODE_MANUAL_OVERRIDE_MAIN_MENU = 19
MODE_IMMERSION_MANUAL_CONTROL = 20
MODE_WOODBURNER_MANUAL_CONTROL = 21
MODE_TANK_1_MANUAL_CONTROL = 22
MODE_TANK_2_MANUAL_CONTROL = 23
MODE_BOILER_MANUAL_CONTROL = 24
MODE_HEATING_MANUAL_CONTROL = 25
MODE_MANUAL_OPTIONS_DISABLED = 26
MODE_IMMERSION_WAITING_SELECT = 27
MODE_IMMERSION_SELECT = 28
MODE_AUTO_MODE_SELECT = 29
MODE_MANUAL_MODE_SELECT = 30
MODE_HOLIDAY_MODE_SELECT = 31
MODE_DISPLAY_STATUS = 32


KEY_TO_MODE_LOOKUP = {
    KEYVALUE_SYSTEM_OFF : MODE_OFF_MODE_SELECT,
    KEYVALUE_AUTO_MODE : MODE_AUTO_MODE_SELECT,
    KEYVALUE_MANUAL_MODE : MODE_MANUAL_MODE_SELECT,
    KEYVALUE_HOLIDAY_MODE : MODE_HOLIDAY_MODE_SELECT
}


# Values for day setting.
DAYS_DISABLED = 99

################################################################################

# Display form codes
BLANK_SCREEN_FORM = 0x04
MAIN_SCREEN_FORM = 0x05

# Backlight control codes
BACKLIGHT_OFF = chr(0x04) + chr(0x00)
BACKLIGHT_LOW = chr(0x04) + chr(0x01)
BACKLIGHT_MAX = chr(0x04) + chr(0x0F)
BACKLIGHT_HALF = chr(0x04) + chr(0x07)

# Sound and volume codes
SOUND_BUZZ = chr (0x00)
SOUND_CLICK = chr (0x01)
SOUND_VOLUME_MAX = chr (0x7f)


# Screen sequences to select variable string fields for main screen.
TOP_RIGHT_INFO_FIELD =  chr(0x02) + chr(0x2C)
ZONE_ON_PROGRAM_FIELD = chr(0x02) + chr(0x2A)
ZONE_OFF_PROGRAM_FIELD = chr(0x02) + chr(0x33)
MIDDLE_RIGHT_INFO_FIELD = chr(0x02) + chr(0x35)
TOP_LEFT_INFO_FIELD =  chr(0x02) + chr(0x29)
BOTTOM_LEFT_INFO_FIELD = chr(0x02) + chr(0x2D)
BOTTOM_RIGHT_INFO_FIELD = chr(0x02) + chr(0x2E)
MIDDLE_LEFT_INFO_FIELD = chr(0x02) + chr(0x39)

# Screen sequences to select set string fields for main screen. Fifth byte will select the string
##MAIN_INFO_FIELD = chr(0x01) + chr(0x11) + chr(0x39)  + chr(0x00)

# Keyboard image select values. These must match image order in visi genie definition.
RAD_WAITING_SELECT_KEYBOARD_IMAGE = 0
UFH_WAITING_SELECT_KEYBOARD_IMAGE = 1
RAD_SELECT_KEYBOARD_IMAGE = 2
UFH_SELECT_KEYBOARD_IMAGE = 3
TIME_SELECT_KEYBOARD_IMAGE = 4
DAY_SELECT_KEYBOARD_IMAGE = 5
SYSTEM_OFF_SELECT_KEYBOARD_IMAGE = 6
SYSTEM_OPTIONS_KEYBOARD_IMAGE = 9
AUTO_OPTIONS_KEYBOARD_IMAGE = 8
MANUAL_OPTIONS_KEYBOARD_IMAGE = 7
HOLIDAY_OPTIONS_KEYBOARD_IMAGE = 10
IMMERSION_CONTROL_KEYBOARD_IMAGE = 11
WOODBURNER_CONTROL_KEYBOARD_IMAGE = 12
MANUAL_CONTROL_KEYBOARD_IMAGE = 13
TANK_1_CONTROL_KEYBOARD_IMAGE = 14
TANK_2_CONTROL_KEYBOARD_IMAGE = 15
BOILER_CONTROL_KEYBOARD_IMAGE = 16
HEATING_CONTROL_KEYBOARD_IMAGE = 17
IMMERSION_WAITING_SELECT_KEYBOARD_IMAGE = 18
IMMERSION_SELECT_KEYBOARD_IMAGE = 19
AUTO_MODE_SELECT_KEYBOARD_IMAGE = 20
MANUAL_MODE_SELECT_KEYBOARD_IMAGE = 21
HOLIDAY_MODE_SELECT_KEYBOARD_IMAGE = 22
SYSTEM_STATUS_SELECT_KEYBOARD_IMAGE = 23


# The ID for a user button message received from the display.
USERBUTTON_MESSAGE = 0x21

# Button numbers for the buttons on the wakeup and failed screens.
FAILED_BUTTON = 21
WAKEUP_BUTTON = 22

# Key button select values. These must match the button order in visi genie definitions of buttons.
KEY_BUTTON_BOOST = 10
KEY_BUTTON_CAN_RES = 15
KEY_BUTTON_AUTO_ENB = 19

# Key image select values. These must match the image order in visi genie definitions of images.

# Button/Image 5
KEY_IMAGE_PREVIOUS = 1

# Button/Image 10
KEY_IMAGE_BOOST = 2
KEY_IMAGE_BOOST_OFF = 3
KEY_IMAGE_NEXT = 1

# Button/Image 15
KEY_IMAGE_BLANK = 0
KEY_IMAGE_CANCEL = 3
KEY_IMAGE_RESUME = 4

# Button/Image 19
KEY_IMAGE_UFH_SITTINGX = 2
KEY_IMAGE_AUTO = 13
KEY_IMAGE_MANUAL = 14
KEY_IMAGE_DISABLE = 15
KEY_IMAGE_ENABLE = 16

# On and off times pointer select values
DIGIT_0_ON_OFF_PTR = 0
DIGIT_1_ON_OFF_PTR = 1
DIGIT_2_ON_OFF_PTR = 2
DIGIT_3_ON_OFF_PTR = 3
DIGIT_ALL_PTR_ON = 4
CLEAR_ON_OFF_PTR = 5

# Bottom left info field message select values.
INFO_1_BLANKED = 0
NOT_SAVED_PROMPT = 1
SAVE_OR_EXIT_PROMPT = 2
INFO_1_CLEAR_TO_CONFIRM = 3

# Top right info field message select values.
CLOCK_DISPLAY = -1

# Bottom right info field message select values.
CLEAR_THE_NOT_VALID_PROMPT = 0
NOT_VALID_PROMPT = 1
DISABLED_PROMPT = 2

#Middle left info field message select values.
BLANK_PROMPT = 0
RAD_SELECT_PROMPT =  1
UFH_SELECT_PROMPT = 2
SYSTEM_SELECT_PROMPT = 3
SYSTEM_OPTIONS_PROMPT = 4
AUTO_OPTIONS_PROMPT = 5
MANUAL_OPTIONS_PROMPT = 6
HOLIDAY_OPTIONS_PROMPT = 7
IMMERSION_SELECT_PROMPT = 8
WB_PUMP_SELECT_PROMPT = 9
MANUAL_OVERRIDE_PROMPT = 10
TANK_1_CONTROL_PROMPT = 11
TANK_2_CONTROL_PROMPT = 12
BOILER_CONTROL_PROMPT = 13
HEATING_CONTROL_PROMPT = 14
OPTIONS_DISABLED_PROMPT = 15
SELECT_IMMERSION_PROMPT = 16
DISPLAY_STATUS_PROMPT = 17
PRESS_ANY_KEY_PROMPT = 18


# Rad on and Ufh on field message select values
RADS_OFF = 0
RADS_ON = 1
UFH_OFF = 0
UFH_ON = 1

# Auto manual field select values
MANUAL_MODE = 0
AUTO_MODE = 1
AUTO_MANUAL_BLANKED = 2

EDIT_CURSOR = '_'

################################################################################

# Flag values to show if we are looking for ACK or button from the display module.
CHECK_FOR_ACK = 0
CHECK_FOR_BUTTON = 1

# Time to wait before starting pump when a zone valve is opening.
PUMP_DELAY_TIME = 10

# Time to wait before we revert to run mode between keypresses.
if IfDev () :
    KEYPRESS_WAIT_TIME = 2000
else :
    KEYPRESS_WAIT_TIME = 20

# Flag values to select type of update to do when updating key images
UPDATE_ALL = 0
UPDATE_CHANGED = 1
NONE_ACTIVE = -1

# Indexes to the program entries fields on each line of the programming data file.
ON_TIME_INDEX = 1
OFF_TIME_INDEX = 3
DAYS_INDEX = 4

################################################################################
## Global variables.
################################################################################

# When a zone is changing state we flash the key image. This flag is set and cleared by the 1 second tick to give us a flash.
flashOn = False
    
# If we try and clear a complete entry we will set this so user has to press clear a 2nd time to confirm.
clearPending = False

# If we have modified data we will set this if we try to exit to give user a chance to save data.
exitPending = False

# Counter for number of times boost key is pressed so we know how many hours to add.
boostPresses = 0

# Each time a keypress is detected we reload this timer. It will be decremented at 1s intervals and when it reaches zero
# we will switch to run mode. This is to guard against the user not finishing aprogramming or control operation.
timeToRunMode = KEYPRESS_WAIT_TIME 

# Flag to indicate our current state. At power up we start in select mode.
currentMode = MODE_RAD_ZONE_SELECT

# We check when a minute has ticked over and keep it here. When the minute ticks we check zones.
# Initialise with an invalid value to force initial update.
lastMinute = -1

# This is the next zone we are going to check. Set to -1 when no checking in progress. Set to 0 whenever
# we want a zone check to take place. It will then increment through each zone.
checkZone = 0
    


