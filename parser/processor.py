from typing import Optional

from parser.enums import LogicalBlockType, ParsedMnemonic
from parser.parsedcommand import ParsedCommand
from parser.utils import Point


class LogicalBlock:
    """
        Series of commands that produce gcode for interrupted line
    """
    block_type: Optional[LogicalBlockType]
    commands: Optional[list[ParsedCommand]]
    last_position: Point

    def __init__(self):
        self.block_type = None
        self.commands = []
        self.last_position = Point(0, 0)

    def add_command(self, command: ParsedCommand):
        """
            Add command to block
        """
        self.commands.append(command)
        if command.mnemonic == ParsedMnemonic.PA:
            # TODO: remove index access
            self.last_position = Point(int(command.arguments[0]), int(command.arguments[1]))

    def __str__(self):
        return f'{self.block_type} [{len(self.commands)}]'

    def print_commands(self) -> str:
        """
            Print commands in block
        """
        return f'{self.block_type}\n [{"\n".join([command.__str__() for command in self.commands])}]:'

    def calc_size(self) -> (int, int):
        """
            Calculate size of block
        """
        size_x = 0
        size_y = 0

        for command in self.commands:
            if command.mnemonic == ParsedMnemonic.PA:
                # TODO: remove index access
                size_x = max(size_x, int(command.arguments[0]))
                size_y = max(size_y, int(command.arguments[1]))
            # TODO: circle size?

            # TODO: relative move?

        return size_x, size_y

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
            current_block.add_command(command)
        current_block.finalize()
        self.blocks.append(current_block)
