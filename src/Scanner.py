from Token import Token
from TokenType import TokenType
from ErrorHandler import ErrorHandler
from ErrorType import ErrorType
from typing import List, Any

class Scanner:
    def __init__(self, source: str, keywords: dict[str, TokenType], errorHandler: ErrorHandler) -> None:
        self.keywords: dict[str, TokenType] = keywords
        self.errorHandler = errorHandler
        errorHandler.lines = source.splitlines()
        errorHandler.lines.append('')

        self.source: str = source
        self.tokens: List[Token] = []

        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.column: int = 1
        self.startColumn: int = 1

    def scanTokens(self) -> List[Token]:
        while not self.isAtEnd():
            self.start = self.current
            self.startColumn = self.column
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, '', None, self.line, self.column + 1))
        return self.tokens

    def scanToken(self) -> None:
        char: str = self.advance()
        match char:
            case '(': self.addToken(TokenType.LEFT_PAREN)
            case ')': self.addToken(TokenType.RIGHT_PAREN)
            case ',': self.addToken(TokenType.COMMA)
            case '.': self.addToken(TokenType.DOT)
            case '-': self.addToken(TokenType.MINUS)
            case '+': self.addToken(TokenType.PLUS)
            case '*': self.addToken(TokenType.STAR)
            case '/': self.addToken(TokenType.SLASH)
            case '!': self.addToken(TokenType.BANG_EQUAL if self.match('=') 
                                    else TokenType.BANG)
            case '=': self.addToken(TokenType.EQUAL_EQUAL if self.match('=') 
                                    else TokenType.EQUAL)
            case '<': self.addToken(TokenType.LESS_EQUAL if self.match('=') 
                                    else TokenType.LESS)
            case '>': self.addToken(TokenType.GREATER_EQUAL if self.match('=') 
                                    else TokenType.GREATER)
            case '#' | '@':
                while self.peek() != '\n' and not self.isAtEnd():
                    self.advance()
            case ' ' | '\r' | '\t': pass
            case '\n':
                self.addToken(TokenType.NEWLINE)
                self.line += 1
                self.column = 1
            case "'": self.string("'")
            case '"': self.string('"')
            case _: 
                if self.isDigit(char): self.number()
                elif self.isAlpha(char): self.identifier()
                else:
                    errorToken = Token(TokenType.IDENTIFIER, char, None, self.line, self.column)
                    self.errorHandler.syntaxError(errorToken, ErrorType.UNEXPECTED_CHARACTER, 'Invalid character')

    def addToken(self, type: TokenType, literal: Any = None) -> None:
        text = self.source[self.start : self.current] if type != TokenType.NEWLINE else 'new line'
        self.tokens.append(Token(type, text, literal, self.line, self.startColumn + 1))

    def advance(self) -> str:
        self.current += 1
        self.column += 1
        return self.source[self.current - 1]

    def match(self, expected: str) -> bool:
        if self.isAtEnd() or self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.isAtEnd():
            return '\0'

        return self.source[self.current]

    def peekNext(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'

        return self.source[self.current + 1]

    def isAtEnd(self) -> bool:
        return self.current >= len(self.source)

    def string(self, quotes: str) -> None:
        while self.peek() != quotes and not self.isAtEnd():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.isAtEnd():
            errorToken = Token(TokenType.QUOTES, quotes, None, self.line, self.startColumn+1)
            self.errorHandler.syntaxError(errorToken, ErrorType.UNTERMINATED_STRING, f'Expected another {quotes} at end to close text value')
            return

        self.advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.addToken(TokenType.STRING, value)

    def number(self) -> None:
        while self.isDigit(self.peek()):
            self.advance()

        if self.peek() == '.' and self.isDigit(self.peekNext()):
            self.advance()
            while self.isDigit(self.peek()):
                self.advance()

        self.addToken(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def isDigit(self, char: str) -> bool:
        return char >= '0' and char <= '9'

    def isAlpha(self, char: str) -> bool:
        return (char >= 'a' and char <= 'z' or 
                char >= 'A' and char <= 'Z' or 
                char == '_')

    def isAlphaNumeric(self, char: str) -> bool:
        return self.isAlpha(char) or self.isDigit(char)

    def identifier(self) -> None:
        while self.isAlphaNumeric(self.peek()):
            self.advance()

        text: str = self.source[self.start:self.current]

        potentialKeywords: List[str] = []

        for keyword in self.keywords:
            if keyword.split()[0] == text:
                potentialKeywords.append(keyword)

        if not potentialKeywords:
            self.addToken(TokenType.IDENTIFIER)

        else:
            potentialKeywords.sort(key=len, reverse=True)
            for keyword in potentialKeywords:
                words: List[str] = keyword.split()

                if self.matchSequence(words[1:]):
                    type = self.keywords[keyword]
                    self.addToken(type)
                    return

            errorToken = Token(TokenType.IDENTIFIER, text, None, self.line, self.startColumn+1)
            self.errorHandler.syntaxError(errorToken, ErrorType.INCOMPLETE_KEYWORD, f'Could be {potentialKeywords}')

    def matchSequence(self, words: List[str]) -> bool:
        saveCurrent = self.current
        saveColumn = self.column

        for word in words:
            if self.peek() == ' ': self.advance()
            if not self.matchWord(word):
                self.current = saveCurrent
                self.column = saveColumn
                return False

        return True

    def matchWord(self, word: str) -> bool:
        end = self.current + len(word)
        if end > len(self.source) or self.source[self.current:end] != word:
            return False

        if end < len(self.source) and self.isAlphaNumeric(self.source[end]):
            return False

        self.current = end
        self.column += len(word)
        return True
