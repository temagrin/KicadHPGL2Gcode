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

    def __str__(self):
        return f'{self.block_type} [{len(self.commands)}]'

    def print_commands(self) -> str:
        """
            Print commands in block
        """
        return f'{self.block_type}\n [{"\n".join([command.__str__() for command in self.commands])}]:'

    def finalize(self):
        """
            Finalize block by setting block type
        """
        mnemonics = [command.mnemonic for command in self.commands]

        if ParsedMnemonic.PD in mnemonics:
            self.block_type = LogicalBlockType.LINE
            return
        if ParsedMnemonic.CI in mnemonics:
            self.block_type = LogicalBlockType.ARC
            return
        if ParsedMnemonic.PM in mnemonics:
            self.block_type = LogicalBlockType.POLYGON
            return

        self.block_type = LogicalBlockType.SET_POSITION


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
                current_block.finalize()
                self.blocks.append(current_block)
                current_block = LogicalBlock()
            current_block.commands.append(command)
        current_block.finalize()
        self.blocks.append(current_block)
