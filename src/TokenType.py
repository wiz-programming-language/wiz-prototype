from enum import Enum, auto

class TokenType(Enum):
	# Single-character tokens
	LEFT_PAREN = auto()
	RIGHT_PAREN = auto()
	COMMA = auto()
	DOT = auto()
	MINUS = auto()
	PLUS = auto()
	SLASH = auto()
	STAR = auto()

	# One or two character tokens
	BANG = auto()
	BANG_EQUAL = auto()
	EQUAL = auto()
	EQUAL_EQUAL = auto()
	GREATER = auto()
	GREATER_EQUAL = auto()
	LESS = auto()
	LESS_EQUAL = auto()
	QUOTES = auto()

	# Literals
	IDENTIFIER = auto()
	STRING = auto()
	NUMBER = auto()

	# Keywords
	AND = auto()
	BEGIN = auto()
	CLASS = auto()
	DO = auto()
	ELSE = auto()
	END = auto()
	FALSE = auto()
	FUNCTION = auto()
	FOR = auto()
	IF = auto()
	INHERITS = auto()
	NOT = auto()
	NONE = auto()
	OR = auto()
	RETURN = auto()
	SUPER = auto()
	THIS = auto()
	TRUE = auto()
	VARIABLE = auto()
	WHILE = auto()

	NEWLINE = auto()
	EOF = auto()
