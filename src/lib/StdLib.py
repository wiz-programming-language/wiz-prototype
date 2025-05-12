from Callable import Callable
from Environment import Environment
from RuntimeError import RuntimeError
from Expr import Call
from language.Language import Language
from lib.StdLibTypes import StdLibTypes
from typing import List, Any, override
from time import time

def defineStdLib(globals: Environment, language: Language):
    global languageName
    languageName = language.languageName

    stdLib: dict[str, Callable] = {
        language.stdLibNames[StdLibTypes.CLOCK]: Clock(),
        language.stdLibNames[StdLibTypes.WRITE]: Write(),
        language.stdLibNames[StdLibTypes.READ]: Read(),
        language.stdLibNames[StdLibTypes.STRING]: String()
    }

    for name, function in stdLib.items():
        globals.define(name, function)

class Clock(Callable):
    def __init__(self) -> None:
        self.startTime = time()

    @override
    def call(self, interpreter, arguments: List[Any]) -> Any:
        return time() - self.startTime

    @override
    def arity(self) -> int:
        return 0

    @override
    def __str__(self) -> str:
        return '<native function "clock">'

class Write(Callable):
    @override
    def call(self, interpreter, arguments: List[Any]) -> Any:
        value = arguments[0]

        match languageName:
            case 'English':
                if value is None: value = 'none'
                if value is True: value = 'true'
                if value is False: value = 'false'

            case 'Português':
                if value is None: value = 'nada'
                if value is True: value = 'verdadeiro'
                if value is False: value = 'falso'

        return print(str(value))

    @override
    def arity(self) -> int:
        return 1

    def __str__(self) -> str:
        return '<native function "write">'

class Read(Callable):
    def __init__(self) -> None:
        self.argument = False

    @override
    def call(self, interpreter, arguments: List[Any]) -> Any:
        if arguments:
            return input(arguments[0])

        return input()

    @override
    def arity(self) -> int:
        if self.argument:
            return 1

        return 0

    def checkArity(self, arguments: List[Any], expr: Call) -> None:
        if len(arguments) == 1:
            self.argument = True

        elif not len(arguments) == 0:
            raise RuntimeError(expr.paren, f'Native function "read" can only take 1 or no arguments but {len(arguments)} were given')

    @override
    def __str__(self) -> str:
        return '<native function "read">'

class String(Callable):
    @override
    def call(self, interpreter, arguments: List[Any]) -> Any:
        return str(arguments[0])
    
    @override
    def arity(self) -> int:
        return 1
    
    @override
    def __str__(self) -> str:
        return '<native function "string">'
