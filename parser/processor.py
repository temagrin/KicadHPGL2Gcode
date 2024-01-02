import enum
from typing import Optional

from parser.parsedcommand import ParsedCommand, ParsedMnemonic


class LogicalBlockType(enum.Enum):
    """
        supported logical block types
    """
    LINE = 'LINE'
    ARC = 'ARC'
    POLYGON = 'POLYGON'
    CIRCLE = 'CIRCLE'
    HOME = 'HOME'
    SET_POSITION = 'SET_POSITION'


class LogicalBlock:
    """
        Series of commands that produce gcode for interrupted line
    """
    block_type: Optional[LogicalBlockType]
    commands: Optional[list[ParsedCommand]]

    def __init__(self, block_type: LogicalBlockType = None, commands: [ParsedCommand] = None):
        self.block_type = block_type
        self.commands = commands if commands is not None else []


class Processor:
    """
        Processes parsed commands into logical blocks
    """
    commands: [ParsedCommand]
    blocks: [LogicalBlock]

    def __init__(self, commands: [ParsedCommand]):
        self.commands = commands
        self.blocks = []

    @staticmethod
    def _is_start_new_block(command) -> bool:
        """
            Return true if it's required to start new block based on command mnemonic
        """
        match command.mnemonic:
            case ParsedMnemonic.PU:
                return False
            case ParsedMnemonic.PD:
                return True
            case ParsedMnemonic.PA:
                return False
            case ParsedMnemonic.CI:
                return True
            case ParsedMnemonic.EP:
                return True
            case ParsedMnemonic.FP:
                return False
            case ParsedMnemonic.PM:
                match command.arguments[0]:
                    case '0':  # start new polygon
                        return True
                    case '2':  # close current polygon
                        return True
                    case _:
                        return False
            case _:
                return False

    def process(self):
        current_block = LogicalBlock()
        for command in self.commands:
            if self._is_start_new_block(command):
                self.blocks.append(current_block)
                current_block = LogicalBlock()
            current_block.commands.append(command)
