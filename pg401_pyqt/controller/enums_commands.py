from enum import Enum

class List(Enum):
    SEQUENCES = "LIST/SEQUENCES" 
    SEQUENCES_DISTINCT = "LIST/SEQUENCES/DISTINCT SEQUENCES"
    CLOG = "LIST/CLOG"
    CLOG_WHERE = "LIST/CLOG WHERE TIME > "
    MSG = "LIST/MSG"

class Exe(Enum):
    STOP = "EXE/Stop"
    FIRE = "EXE/Fire"
    AMPLIFICATION = "EXE/Amplification/"

class Rdvar(Enum):
    STATE = "RDVAR/State"
    LOGBLAB = "RDVAR/LogBlab"
    PRODUCT_ID = "RDVAR/ProductID"
    PRODUCT_SN = "RDVAR/ProductSN"

