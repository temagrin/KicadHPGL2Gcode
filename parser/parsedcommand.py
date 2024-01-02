import enum


class ParsedMnemonic(enum.Enum):
    """
        supported kicad-produced commands
    """
    PU = 'PU'  # pen up
    PA = 'PA'  # pen absolute
    PD = 'PD'  # pen down
    PM = 'PM'  # polygon mode
    EP = 'EP'  # end polygon
    FP = 'FP'  # fill polygon
    CI = 'CI'  # circle


class ParsedCommand:
    """
        parsed kicad command
    """
    mnemonic: ParsedMnemonic
    arguments: list

    def __init__(self, mnemonic: ParsedMnemonic, arguments: list):
        self.mnemonic = mnemonic
        self.arguments = arguments

    def __str__(self):
        return f'{self.mnemonic.value} {", ".join(self.arguments)}'


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
