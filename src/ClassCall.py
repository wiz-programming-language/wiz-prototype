from Callable import Callable
from Instance import Instance
from FunctionCall import FunctionCall
from typing import Any, List, override

class ClassCall(Callable):
    def __init__(self, name: str, superclass: 'ClassCall', methods: dict[str, FunctionCall]) -> None:
        self.name: str = name
        self.superclass: ClassCall = superclass
        self.methods = methods

    def findMethod(self, name: str) -> FunctionCall:
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass is not None:
            return self.superclass.findMethod(name)

    @override
    def call(self, interpreter, arguments: List[Any]) -> Any:
        instance: Instance = Instance(self)        
        initializer: FunctionCall = self.findMethod('init')

        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        
        return instance

    @override
    def arity(self) -> int:
        initializer: FunctionCall = self.findMethod('init')
        
        if initializer is None:
            return 0

        return initializer.arity()

    @override
    def __str__(self) -> str:
        return f'<class "{self.name}">'
