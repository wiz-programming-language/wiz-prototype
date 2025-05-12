from abc import ABC, abstractmethod
from Token import Token
from typing import Any, List, override

class Expr(ABC):
    class Visitor(ABC):
        @abstractmethod
        def visitAssignExpr(self, expr: "Assign"):
            pass

        @abstractmethod
        def visitBinaryExpr(self, expr: "Binary"):
            pass

        @abstractmethod
        def visitCallExpr(self, expr: "Call"):
            pass

        @abstractmethod
        def visitGetExpr(self, expr: "Get"):
            pass

        @abstractmethod
        def visitSetExpr(self, expr: "Set"):
            pass

        @abstractmethod
        def visitSuperExpr(self, expr: "Super"):
            pass

        @abstractmethod
        def visitThisExpr(self, expr: "This"):
            pass

        @abstractmethod
        def visitGroupingExpr(self, expr: "Grouping"):
            pass

        @abstractmethod
        def visitLiteralExpr(self, expr: "Literal"):
            pass

        @abstractmethod
        def visitUnaryExpr(self, expr: "Unary"):
            pass

        @abstractmethod
        def visitVariableExpr(self, expr: "Variable"):
            pass

    @abstractmethod
    def accept(self, visitor: Visitor):
        pass

class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name: Token = name
        self.value: Expr = value

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitAssignExpr(self)

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left: Expr = left
        self.operator: Token = operator
        self.right: Expr = right

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitBinaryExpr(self)

class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee: Expr = callee
        self.paren: Token = paren
        self.arguments: List[Expr] = arguments

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitCallExpr(self)

class Get(Expr):
    def __init__(self, object: Expr, name: Token):
        self.object: Expr = object
        self.name: Token = name

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitGetExpr(self)

class Set(Expr):
    def __init__(self, object: Expr, name: Token, value: Expr):
        self.object: Expr = object
        self.name: Token = name
        self.value: Expr = value

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitSetExpr(self)

class Super(Expr):
    def __init__(self, keyword: Token, method: Token):
        self.keyword: Token = keyword
        self.method: Token = method

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitSuperExpr(self)

class This(Expr):
    def __init__(self, keyword: Token):
        self.keyword: Token = keyword

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitThisExpr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitGroupingExpr(self)

class Literal(Expr):
    def __init__(self, value: Any):
        self.value: Any = value

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitLiteralExpr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator: Token = operator
        self.right: Expr = right

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitUnaryExpr(self)

class Variable(Expr):
    def __init__(self, name: Token):
        self.name: Token = name

    @override
    def accept(self, visitor: Expr.Visitor):
        return visitor.visitVariableExpr(self)
