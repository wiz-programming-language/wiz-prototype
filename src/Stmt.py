from abc import ABC, abstractmethod
from Token import Token
from Expr import Expr, Variable
from typing import List, override

class Stmt(ABC):
    class Visitor(ABC):
        @abstractmethod
        def visitIfStmt(self, stmt: "If"):
            pass

        @abstractmethod
        def visitWhileStmt(self, stmt: "While"):
            pass

        @abstractmethod
        def visitVarStmt(self, stmt: "Var"):
            pass

        @abstractmethod
        def visitFunctionStmt(self, stmt: "Function"):
            pass

        @abstractmethod
        def visitReturnStmt(self, stmt: "Return"):
            pass

        @abstractmethod
        def visitBlockStmt(self, stmt: "Block"):
            pass

        @abstractmethod
        def visitClassStmt(self, stmt: "Class"):
            pass

        @abstractmethod
        def visitExpressionStmt(self, stmt: "Expression"):
            pass

    @abstractmethod
    def accept(self, visitor: Visitor):
        pass

class If(Stmt):
    def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt):
        self.condition: Expr = condition
        self.thenBranch: Stmt = thenBranch
        self.elseBranch: Stmt = elseBranch

    @override
    def accept(self, visitor: Stmt.Visitor):
        return visitor.visitIfStmt(self)

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition: Expr = condition
        self.body: Stmt = body

    @override
    def accept(self, visitor: Stmt.Visitor):
        return visitor.visitWhileStmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name: Token = name
        self.initializer: Expr = initializer

    @override
    def accept(self, visitor: Stmt.Visitor):
        return visitor.visitVarStmt(self)

class Function(Stmt):
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name: Token = name
        self.params: List[Token] = params
        self.body: List[Stmt] = body

    @override
    def accept(self, visitor: Stmt.Visitor):
        return visitor.visitFunctionStmt(self)

class Return(Stmt):
    def __init__(self, keyword: Token, value: Expr):
        self.keyword: Token = keyword
        self.value: Expr = value

    @override
    def accept(self, visitor: Stmt.Visitor):
        return visitor.visitReturnStmt(self)

class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements: List[Stmt] = statements

    @override
    def accept(self, visitor: Stmt.Visitor):
        return visitor.visitBlockStmt(self)

class Class(Stmt):
    def __init__(self, name: Token, superclass: Variable, methods: List["Function"]):
        self.name: Token = name
        self.superclass: Variable = superclass
        self.methods: List["Function"] = methods

    @override
    def accept(self, visitor: Stmt.Visitor):
        return visitor.visitClassStmt(self)

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    @override
    def accept(self, visitor: Stmt.Visitor):
        return visitor.visitExpressionStmt(self)
