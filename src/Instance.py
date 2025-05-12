from Token import Token
from RuntimeError import RuntimeError
# from ClassCall import ClassCall
from FunctionCall import FunctionCall
from typing import Any

class Instance:
    def __init__(self, class_: 'ClassCall') -> None:
        self.class_: 'ClassCall' = class_
        self.fields: dict[str, Any] = {}

    def get(self, name: Token) -> Any:
        if name.lexeme in  self.fields:
            return self.fields[name.lexeme]

        method: FunctionCall = self.class_.findMethod(name.lexeme)

        if method is not None:
            return method.bind(self)

        raise RuntimeError(name, f'Undefined property "{name.lexeme}"')

    def set(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return self.class_.name + ' instance'
