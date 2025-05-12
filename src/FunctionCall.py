from Callable import Callable
import Stmt
from Environment import Environment
from Return import Return_
from language.Language import Language
from TokenType import TokenType
# from Instance import Instance
from typing import Any, List, override

class FunctionCall(Callable):
    def __init__(self, declaration: Stmt.Function, closure: Environment, isInitializer: bool, language: Language) -> None:
        self.declaration: Stmt.Function = declaration
        self.closure: Environment = closure
        self.isInitializer: bool = isInitializer
        self.language: Language = language

    def bind(self, instance: 'Instance') -> 'FunctionCall':
        environment: Environment = Environment(self.closure)
        environment.define(self.retriveKeyword(TokenType.THIS), instance)
        
        return FunctionCall(self.declaration, environment, self.isInitializer, self.language)

    @override
    def call(self, interpreter, arguments: List[Any]) -> Any:
        environment: Environment = Environment(self.closure)

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.executeBlock(self.declaration.body, environment)
  
        except Return_ as returnValue:
            if self.isInitializer:
                return self.closure.getAt(0, self.retriveKeyword(TokenType.THIS))
            
            return returnValue.value
  
        if self.isInitializer:
            return self.closure.getAt(0, self.retriveKeyword(TokenType.THIS))
  
        return None

    @override
    def arity(self) -> int:
        return len(self.declaration.params)

    @override
    def __str__(self) -> str:
        return f'<function "{self.declaration.name.lexeme}">'

    def retriveKeyword(self, type: TokenType) -> str:
        return next((k for k, v in self.language.keywords.items() if v == type), None)
