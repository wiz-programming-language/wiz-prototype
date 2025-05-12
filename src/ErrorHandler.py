from Token import Token
from TokenType import TokenType
from RuntimeError import RuntimeError
from ErrorType import ErrorType
from typing import List

class ErrorHandler:
    def __init__(self, errors: dict[ErrorType, str]) -> None:
        self.errors: dict[ErrorType, str] = errors
        self.hadError: bool = False
        self.hadRuntimeError: bool = False
        self.lines: List[str] = []

    def error(self, token: Token, message: str) -> None:
        if token.type == TokenType.NEWLINE: where = 'end of line'
        elif token.type == TokenType.EOF: where = 'end of program'
        else: where = f'"{token.lexeme}"'

        RED = '\033[31m'
        RESET = '\033[0m'

        print(f'{RED}Error at {where}: {message}{RESET}\n')
        print(f' {token.line} | {self.lines[token.line - 1]}')
        print(f' {self.underlineErrorToken(token)} Error message\n')

        self.hadError = True

    def report(self, origin: str, token: Token, errorType: ErrorType, message: str) -> None:
        if token.type == TokenType.NEWLINE: where = 'end of line'
        elif token.type == TokenType.EOF: where = 'end of program'
        elif token.type == TokenType.QUOTES: where = token.lexeme
        else: where = f'"{token.lexeme}"'

        RED = '\033[31m'
        RESET = '\033[0m'

        print(f'{RED}{origin} error at {where}: {self.errors[errorType]}{RESET}\n')
        print(f' {token.line} | {self.lines[token.line - 1]}')
        print(f' {self.underlineErrorToken(token)} {message}\n')

    def syntaxError(self, token: Token, errorType: ErrorType, message: str) -> None:
        self.report('Syntax', token, errorType, message)
        self.hadError = True

    def runtimeError(self, error: RuntimeError) -> None:
        # print(f'[line {error.token.line}] Runtime error: {error.message}')
        self.error(error.token, error.message)
        self.hadRuntimeError = True

    def underlineErrorToken(self, token: Token) -> str:
        underline: str = " " * (token.column + 1 + len(str(token.line)))
        for _ in token.lexeme:
            underline += '^'
        return underline if token.lexeme else '^'
