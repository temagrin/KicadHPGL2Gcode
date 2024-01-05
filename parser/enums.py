import enum


class LogicalBlockType(enum.Enum):
    """
        supported logical block types
    """
    LINE = 'LINE'
    ARC = 'ARC'
    POLYGON = 'POLYGON'
    SET_POSITION = 'SET_POSITION'


class ParsedMnemonic(enum.Enum):
    """
        supported kicad-produced commands
    """
    PU = 'PU'  # pen up
    PA = 'PA'  # pen absolute
    PD = 'PD'  # pen down
    PM = 'PM'  # polygon mode
    EP = 'EP'  # edge polygon
    FP = 'FP'  # fill polygon
    CI = 'CI'  # circle


class GCodeMnemonic(enum.Enum):
    """
        supported gcode commands
    """
    G0 = 'G0'  # idle move
    G1 = 'G1'  # working move
    G2 = 'G2'  # clockwise arc
    M3 = 'M3'  # spindle on
    M4 = 'M4'  # dynamic mode
    M5 = 'M5'  # spindle off
    G28 = 'G28'  # home
    G92 = 'G92'  # set position
