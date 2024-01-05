import re

from parser.parsedcommand import ParsedCommand
from parser.enums import ParsedMnemonic

import logging


class Parser:
    """
        Parses kicad-produced file into commands
    """
    parse_regex = re.compile(r'\s*(?P<mnemonic>\w{2}){1}\s?(?P<arguments>[\d,]+)?')
    commands: [ParsedCommand]

    def __init__(self, filename: str):
        self.filename = filename
        self.commands = []

    @staticmethod
    def _is_command_valid(command: ParsedCommand) -> bool:
        """
            check if arguments are valid for given mnemonic
        """
        match command.mnemonic:
            case ParsedMnemonic.PA:
                return len(command.arguments) == 2
            case _:
                return True

    @classmethod
    def _parse_command_line(cls, line: str) -> ParsedCommand | None:
        """
            parse line into mnemonic and arguments
            returns None if line is not a valid command
        """
        if not line:
            return None
        parsed = re.match(cls.parse_regex, line)
        if parsed is None:
            logging.warning(f'Failed to parse command: {line}\n (regex failed)')
            return None
        try:
            mnemonic = ParsedMnemonic(parsed.group('mnemonic'))
        except ValueError as e:
            logging.warning(f'Failed to parse command: {line}\n ({e})')
            return None
        arguments = parsed.group('arguments').split(',') if parsed.group('arguments') else []
        if not cls._is_command_valid(ParsedCommand(mnemonic, arguments)):
            logging.warning(f'Invalid command: {line}')
            return None
        return ParsedCommand(mnemonic, arguments)

    def parse(self):
        with open(self.filename, 'r') as file:
            for line in file:
                for chunk in line.split(';'):
                    if not chunk:
                        continue
                    command = self._parse_command_line(chunk.strip())
                    if command is not None:
                        self.commands.append(command)
                        logging.info(f'Parsed command: {command}')
