from parser.enums import ParsedMnemonic


class ParsedCommand:
    """
        parsed kicad command
    """
    mnemonic: ParsedMnemonic
    arguments: list

    def __init__(self, mnemonic: ParsedMnemonic, arguments: list):
        self.mnemonic = mnemonic
        self.arguments = arguments

    def __str__(self):
        return f'{self.mnemonic.value} {", ".join(self.arguments)}'


