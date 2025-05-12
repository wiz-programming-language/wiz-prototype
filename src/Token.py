from TokenType import TokenType
from typing import Any

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: Any, line: int, column: int) -> None:
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f'<{self.type} | {self.lexeme} | {self.literal} | line {self.line} | column {self.column}>'
