import logging
from decimal import Decimal

from parser.parser import Parser
from parser.processor import Processor
from parser.render import ImageRenderer


# Посмотреть что там кикад вообще генерировать может
# https://gitlab.com/kicad/code/kicad/-/blob/master/common/plotters/HPGL_plotter.cpp


class HPGL2:
    def __init__(self, filename):
        self.filename = filename
        self.new_commands = set()
        self.x = 0
        self.y = 0
        self.pen = False
        self.absolute = True
        self.polygon_mode = 0

    def move_to(self, command):
        if ',' in command:
            if self.absolute:
                self.x = int(command[3:].split(",")[0])
                self.y = int(command[3:].split(",")[1])
            else:
                self.x += int(command[3:].split(",")[0])
                self.y += int(command[3:].split(",")[1])

    def gen_draw(self, last_x, last_y):
        # тут порисушки
        pass

    def parse_command(self, command):
        last_x = self.x
        last_y = self.y
        command_key = command[:2]
        if command_key in ['IN', 'SP', 'VS', 'PT']:
            return  # Инит, выбор инструмента, скорость - игнорим. в  PT - kicad засовывает толщину пера (что не
            # сходится с докой от HP)
        elif command_key == "PU":
            self.pen = False
            self.move_to(command)
        elif command_key == "PA":
            self.absolute = True
            if "," in command:
                self.x = int(command[3:].split(",")[0])
                self.y = int(command[3:].split(",")[1])
            self.move_to(command)
        elif command_key == "PD":
            self.pen = True
            self.move_to(command)
        elif command_key == "PM":
            self.polygon_mode = int(command[3:])
        elif command_key == "EP":
            pass  # замкнуть и отрисовтаь текущий полигон
        elif command_key == "FP":
            pass  # заполнить полигон - по умолчанию Even/odd fill algorithm . 1 - - Non-zero winding fill algorithm
        elif command_key == "CI":
            pass  # круг - первый аргумент - радиус, второй угол хорды - если не задан - 5 градусов
        else:
            # сюда засовываем новые, нереализованные команды. если они есть - значит надо дописать
            self.new_commands.add(command_key)
        self.gen_draw(last_x, last_y)

    def parse_line(self, line):
        for raw_command in line.split(";"):
            if raw_command: self.parse_command(raw_command.strip())

    def parse_file(self):
        with open(self.filename, 'r') as h:
            for line in h.readlines():
                if ';' in line:
                    self.parse_line(line.strip())


# 1 plu = 0.025 mm (≈ 0.00098 in.)
# 40 plu = 1 mm
# 1016 plu = 1 in.
# 3.39 plu = 1 dot @ 300 dp

if __name__ == '__main__':
    # hpgl = HPGL2("laser-B_Cu.plt")
    # hpgl.parse_file()
    # for c in hpgl.new_commands:
    #     logging.critical(f'Unexpected command: "{c}"')

    logging.basicConfig(level=logging.WARNING)
    parser = Parser("laser-B_Cu.plt")
    # parser = Parser("laser-Edge_Cuts.plt")
    parser.parse()

    processor = Processor(parser.commands)
    processor.process()
    # for block in processor.blocks:
    #     print(block.print_commands())

    ImageRenderer(
        blocks=processor.blocks,
        scaling_factor=Decimal(0.5)
    ).render()