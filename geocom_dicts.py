BAP_TARGET_TYPE = {
    "BAP_REFL_USE": 0,  # with reflector
    "BAP_REFL_LESS": 1,  # without reflector
}

PrismType = {
    "BAP_PRISM_ROUND": 0,
    "BAP_PRISM_MINI": 1,
    "BAP_PRISM_TAPE": 2,
    "BAP_PRISM_360": 3,
    "BAP_PRISM_USER1": 4,
    "BAP_PRISM_USER2": 5,
    "BAP_PRISM_USER3": 6,
    "BAP_PRISM_360_MINI": 7,
    "BAP_PRISM_MINI_ZERO": 8,
    "BAP_PRISM_USER": 9,
    "BAP_PRISM_NDS_TAPE": 10,
    "BAP_PRISM_GRZ121_ROUND": 11,
    "BAP_PRISM_MA_MPR122": 12
}


ON_OFF_TYPE = {
    "OFF": 0,
    "ON": 1,
}


AUT_POSMODE = {
   "AUT_NORMAL": 0,  # fast positioning mode
   "AUT_PRECISE": 1,  # exact positioning mode note: can distinctly claim more time for the positioning
   "AUT_Fast": 2,  # for TS30 / TM30 instruments, positions with the last valid inclination and an increased positioning tolerance.
}

AUT_ATRMODE = {
    "AUT_POSITION": 0,  # Positioning to the hz- and v-angle
    "AUT_TARGET": 1,  # Positioning to a target in the environment of the hz- and v-angle.
}

BOOLE = {
    False: 0,
    True: 1,
}

TMC_MEASURE_PRG = {
    "TMC_STOP": 0,  # Stop measurement program
    "TMC_DEF_DIST": 1,  # Default DIST-measurement program
    "TMC_CLEAR": 3,
    "TMC_SIGNAL": 4,
    "TMC_DO_MEASURE": 6,
    "TMC_RTRK_DIST": 8,
    "TMC_RED_TRK_DIST": 10,
    "TMC_FREQUENCY": 11,
}

TMC_INCLINE_PRG = {
    "TMC_MEA_INC": 0,  # Use sensor (apriori sigma)
    "TMC_AUTO_INC": 1,  # Automatic mode (sensor/plane)
    "TMC_PLANE_INC": 2,  # Use plane (apriori sigma)
}


BAP_USER_MEASPRG = {
     "BAP_SINGLE_REF_STANDARD": 0,
     "BAP_SINGLE_REF_FAST": 1,
     "BAP_SINGLE_REF_VISIBL": 2,
     "BAP_SINGLE_RLESS_VISIBLE": 3,
     "BAP_CONT_REF_STANDARD": 4,
     "BAP_CONT_REF_FAST": 5,
     "BAP_CONT_RLESS_VISIBLE": 6,
     "BAP_AVG_REF_STANDARD": 7,
     "BAP_AVG_REF_VISIBLE": 8,
     "BAP_AVG_RLESS_VISIBLE": 9,
     "BAP_CONT_REF_SYNCHRO": 10,
     "BAP_SINGLE_REF_PRECISE": 11,
}


EDM_MODE = {
    "EDM_MODE_NOT_USED": 0,
    "EDM_SINGLE_TAPE": 1,
    "EDM_SINGLE_STANDARD": 2,
    "EDM_SINGLE_FAST": 3,
    "EDM_SINGLE_LRANGE": 4,
    "EDM_SINGLE_SRANGE": 5,
    "EDM_CONT_STANDARD": 6,
    "EDM_CONT_DYNAMIC": 7,
    "EDM_CONT_REFLESS": 8,
    "EDM_CONT_FAST": 9,
    "EDM_AVERAGE_IR": 10,
    "EDM_AVERAGE_SR": 11,
    "EDM_AVERAGE_LR": 12,
    "EDM_PRECISE_IR": 13,
    "EDM_PRECISE_TAPE": 14,
}