import enum


class Mnemonic(enum.Enum):
    # known commands
    PU = 'PU'  # pen up
    PA = 'PA'  # pen absolute
    PD = 'PD'  # pen down
    PM = 'PM'  # polygon mode
    EP = 'EP'  # end polygon
    FP = 'FP'  # fill polygon
    CI = 'CI'  # circle


class Command:
    # parsed command
    mnemonic: Mnemonic
    arguments: list

    def __init__(self, mnemonic: Mnemonic, arguments: list):
        self.mnemonic = mnemonic
        self.arguments = arguments

    def __str__(self):
        return f'{self.mnemonic.value} {", ".join(self.arguments)}'
