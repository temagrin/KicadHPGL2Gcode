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

    def is_not_empty(self) -> bool:
        """
            Check if block is not empty
        """
        return len(self.commands) > 0

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

        max_radius = 0

        for command in self.commands:
            if command.mnemonic == ParsedMnemonic.PA:
                # TODO: remove index access
                size_x = max(size_x, int(command.arguments[0]))
                size_y = max(size_y, int(command.arguments[1]))
            if command.mnemonic == ParsedMnemonic.CI:
                max_radius = max(max_radius, int(command.arguments[0]))

            # TODO: relative move?

        return size_x + max_radius, size_y+max_radius

    def finalize(self):
        """
            Finalize block by setting block type
        """
        mnemonics = [command.mnemonic for command in self.commands]

        # warning: order matters!

        if ParsedMnemonic.PD in mnemonics:
            self.block_type = LogicalBlockType.LINE
            return

        if ParsedMnemonic.PM in mnemonics:
            self.block_type = LogicalBlockType.POLYGON
            return

        if ParsedMnemonic.CI in mnemonics:
            self.block_type = LogicalBlockType.ARC
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

    def append_block(self, block: LogicalBlock):
        """
            Append block to list of blocks
        """
        if block.is_not_empty():
            self.blocks.append(block)

    @staticmethod
    def _is_start_new_block(command) -> bool:
        """
            Return true if it's required to start new block based on command mnemonic
        """
        match command.mnemonic:
            case ParsedMnemonic.PU:
                return True
            case ParsedMnemonic.PD:
                return False
            case ParsedMnemonic.PA:
                return False
            case ParsedMnemonic.CI:
                return False
            case ParsedMnemonic.EP:
                return False
            case ParsedMnemonic.FP:
                return False
            case ParsedMnemonic.PM:
                match command.arguments[0]:
                    case '0':  # start new polygon
                        return True
                    case '2':  # close current polygon
                        return False
                    case _:
                        return False
            case _:
                return False

    def process(self):
        current_block = LogicalBlock()
        for command in self.commands:
            if self._is_start_new_block(command):
                current_block.finalize()
                self.append_block(current_block)
                current_block = LogicalBlock()

            current_block.add_command(command)

        current_block.finalize()
        self.append_block(current_block)
