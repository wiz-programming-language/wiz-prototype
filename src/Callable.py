from abc import ABC, abstractmethod
from typing import Any, List
# from Interpreter import Interpreter

class Callable(ABC):
    @abstractmethod
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
