from language.Keywords import keywords
from language.Errors import errors
from language.StdLibNames import stdLibNames
from TokenType import TokenType
from ErrorType import ErrorType
from lib.StdLibTypes import StdLibTypes

class Language:
    def __init__(self, languageName: str) -> None:
        self.languageName: str = languageName
        self.keywords: dict[str, TokenType] = keywords[languageName]
        self.errors: dict[ErrorType, str] = errors[languageName]
        self.stdLibNames: dict[StdLibTypes, str] = stdLibNames[languageName]
        # self.messages = messages[languageName]
