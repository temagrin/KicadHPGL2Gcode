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
    _image_origin: Point
    _image_border_extension: Point = Point(2, 2)
    padding: int

    def __init__(self, blocks: [LogicalBlock], scaling_factor: decimal.Decimal = 1, padding: int = 10):
        self.blocks = blocks
        self.scaling_factor = scaling_factor
        self._reset_image_origin()
        self.padding = padding

    def _reset_image_origin(self, point: Point = None):
        """
            reset image origin to 0,0
        """
        self._image_origin = point if point else Point(0, 0)

    def _trim_image_origin(self, point: Point):
        self._image_origin.x = min(self._image_origin.x, point.x)
        self._image_origin.y = min(self._image_origin.y, point.y)

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

        size_x += self._image_border_extension.x
        size_y += self._image_border_extension.y

        return self._apply_scaling(Point(size_x, size_y))

    def _render_line(self, point_from: Point, point_to: Point, draw: ImageDraw):
        point_from = self._apply_scaling(point_from)
        point_to = self._apply_scaling(point_to)
        self._trim_image_origin(point_from)
        self._trim_image_origin(point_to)
        draw.line(
            (
                point_from.as_tuple(),
                point_to.as_tuple()
            ),
            fill='black'
        )

    def _render_circle(self, point: Point, radius: int, draw: ImageDraw):
        point = self._apply_scaling(point)
        radius = int(radius * self.scaling_factor)
        self._trim_image_origin(Point(point.x - radius, point.y - radius))
        draw.ellipse(
            (
                point.x - radius,
                point.y - radius,
                point.x + radius,
                point.y + radius
            ),
            width=1,
            outline='black',
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
                    new_position = Point(0, 0)
                self._render_line(prev_position, new_position, draw)
                prev_position = new_position

            if command.mnemonic == ParsedMnemonic.CI:
                self._render_circle(prev_position, int(command.arguments[0]), draw)

            if command.mnemonic == ParsedMnemonic.PM and command.arguments[0] == '2':
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

    def _apply_crop_and_padding(self, image: Image) -> Image:
        """
            crop image and add padding
        """

        origin_x = (self._image_origin.x - 1) if self._image_origin.x > 0 else 0
        origin_y = (self._image_origin.y - 1) if self._image_origin.y > 0 else 0

        width = (image.width + 1) if self._image_origin.x == image.width else image.width
        height = (image.height + 1) if self._image_origin.y ==  image.height else image.height

        image = image.crop((
            origin_x,
            origin_y,
            width,
            height
        ))

        # add padding
        new_image = Image.new(
            'RGB',
            (
                image.width + self.padding * 2,
                image.height + self.padding * 2
            ),
            color='white'
        )
        new_image.paste(
            image,
            (
                self.padding,
                self.padding
            )
        )

        return new_image

    def render(self, crop: bool = True) -> Image:
        """
        Render image from blocks
        :return: PIL Image
        """
        size = self._get_image_size()
        self._reset_image_origin(size)

        image = Image.new('RGB', (size.x, size.y), color='white')
        draw = ImageDraw.Draw(image)
        last_position = Point(0, 0)
        for block in self.blocks:
            self._render_block(block, draw, last_position)
            last_position = block.last_position

        if crop:
            return self._apply_crop_and_padding(image)
        return image
