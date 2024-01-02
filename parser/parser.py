import re

from parser.command import Command, Mnemonic

import logging


class Parser:
    parse_regex = r'(?P<mnemonic>\w{2}){1}\s?(?P<arguments>[\d,]+)?'
    commands: [Command]

    def __init__(self, filename: str):
        self.filename = filename
        self.commands = []

    @classmethod
    def _parse_command_line(cls, line: str) -> Command | None:
        # parse line into mnemonic and arguments
        # returns None if line is not a valid command
        parsed = re.match(cls.parse_regex, line)
        if parsed is None:
            return None
        try:
            mnemonic = Mnemonic(parsed.group('mnemonic'))
        except ValueError as e:
            logging.warning(f'Failed to parse command: {line}\n ({e})')
            return None
        arguments = parsed.group('arguments').split(',') if parsed.group('arguments') else []
        return Command(mnemonic, arguments)

    def parse(self):
        with open(self.filename, 'r') as file:
            for line in file:
                for chunk in line.split(';'):
                    if not chunk:
                        continue
                    command = self._parse_command_line(chunk)
                    if command is not None:
                        self.commands.append(command)
                        logging.info(f'Parsed command: {command}')
