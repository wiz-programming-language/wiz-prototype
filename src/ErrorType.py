from enum import Enum, auto

class ErrorType(Enum):
    # Lexer errors
    UNTERMINATED_STRING = auto()
    UNEXPECTED_CHARACTER = auto()
    INCOMPLETE_KEYWORD = auto()

    # Parser errors
    UNTERMINATED_STATEMENT = auto()
    UNTERMINATED_BLOCK = auto()
    EXPECT_VARIABLE_NAME = auto()
    
    
    
    SYNTAX_ERROR = auto()
    TYPE_ERROR = auto()
    NAME_ERROR = auto()
    RUNTIME_ERROR = auto()
    PARSE_ERROR = auto() # Compilation error
