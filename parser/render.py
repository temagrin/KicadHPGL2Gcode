import decimal
from PIL import Image, ImageDraw

from parser.parsedcommand import ParsedCommand
from parser.processor import LogicalBlock
from parser.enums import LogicalBlockType, ParsedMnemonic
from parser.utils import Point


class ImageRenderer:
    """
        renders image from logical blocks using pillow
    """
    blocks: [LogicalBlock]
    scaling_factor: decimal.Decimal

    def __init__(self, blocks: [LogicalBlock], scaling_factor: decimal.Decimal = 1):
        self.blocks = blocks
        self.scaling_factor = scaling_factor

    def _apply_scaling(self, point: Point) -> Point:
        return Point(
            int(point.x * self.scaling_factor),
            int(point.y * self.scaling_factor)
        )

    def _get_image_size(self) -> Point:
        """
            calculate image size from blocks
        """
        size_x = 0
        size_y = 0

        for block in self.blocks:
            block_size_x, block_size_y = block.calc_size()
            size_x = max(size_x, block_size_x)
            size_y = max(size_y, block_size_y)

        return self._apply_scaling(Point(size_x, size_y))

    def _render_line(self, point_from: Point, point_to: Point, draw: ImageDraw):
        draw.line(
            (
                self._apply_scaling(point_from).as_tuple(),
                self._apply_scaling(point_to).as_tuple()
            ),
            fill='black'
        )

    def _render_commands_as_lines(self, commands: [ParsedCommand], draw: ImageDraw, prev_position: Point = Point(0, 0)):
        pen_down = False
        for command in commands:
            if command.mnemonic == ParsedMnemonic.PU:
                pen_down = False
            if command.mnemonic == ParsedMnemonic.PA:
                new_position = Point(int(command.arguments[0]), int(command.arguments[1]))
                if pen_down:
                    self._render_line(prev_position, new_position, draw)
                prev_position = new_position
            if command.mnemonic == ParsedMnemonic.PD:
                pen_down = True

    def _render_polygon(self, commands: [ParsedCommand], draw: ImageDraw, prev_position: Point = Point(0, 0)):
        polygon_start_position = prev_position
        for command in commands:
            if command.mnemonic == ParsedMnemonic.PA:
                if len(command.arguments) == 2:
                    new_position = Point(int(command.arguments[0]), int(command.arguments[1]))
                else:
                    new_position =  Point(0, 0)
                self._render_line(prev_position, new_position, draw)
                prev_position = new_position
            if command.mnemonic == ParsedMnemonic.EP and command.arguments[0] == '2':

                self._render_line(prev_position, polygon_start_position, draw)
                prev_position = polygon_start_position

    def _render_block(self, block: LogicalBlock, draw: ImageDraw, last_position: Point = Point(0, 0)):
        match block.block_type:
            case LogicalBlockType.LINE:
                self._render_commands_as_lines(block.commands, draw, last_position)
            case LogicalBlockType.ARC:
                pass
                # raise NotImplementedError("Arc rendering is not implemented")
            case LogicalBlockType.POLYGON:
                self._render_polygon(block.commands, draw, last_position)
            case LogicalBlockType.SET_POSITION:
                pass
            case _:
                raise ValueError(f'Unknown block type: {block.block_type}')

    def render(self):
        size = self._get_image_size()

        image = Image.new('RGB', (size.x, size.y), color='white')
        draw = ImageDraw.Draw(image)
        last_position = Point(0, 0)
        for block in self.blocks:
            self._render_block(block, draw, last_position)
            last_position = block.last_position

        image = image.rotate(180)
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

        image.show()
