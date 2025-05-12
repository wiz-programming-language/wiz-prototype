from Token import Token
from RuntimeError import RuntimeError
from typing import Any

class Environment:
    def __init__(self, enclosing: 'Environment' = None) -> None:
        self.values: dict[str, Any] = {}
        self.enclosing: Environment = enclosing
        
    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values.keys():
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(name, f'Undefined variable "{name.lexeme}" on variable call')

    def getAt(self, distance: int, name: str) -> Any:
        return self.ancestor(distance).values.get(name)

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
    
        raise RuntimeError(name, f'Undefined variable "{name.lexeme}" on variable assignment')

    def assignAt(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance: int) -> 'Environment':
        environment: Environment = self
        
        for _ in range(distance):
            environment = environment.enclosing

        return environment
