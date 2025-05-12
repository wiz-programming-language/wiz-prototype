from Expr import Expr, Variable, Assign, Binary, Call, Grouping, Literal, Unary, This, Set, Get, Super
from Stmt import Stmt, Block, Var, Function, Expression, If, Return, While, Class
from Interpreter import Interpreter
from Token import Token
from ErrorHandler import ErrorHandler
from language.Language import Language
from TokenType import TokenType
from typing import override, List
from enum import Enum

class FunctionType(Enum):
    NONE = 1
    FUNCTION = 2
    METHOD = 3
    INITIALIZER = 4

class ClassType(Enum):
    NONE = 1
    CLASS = 2
    SUBCLASS = 3

class Resolver(Expr.Visitor, Stmt.Visitor):
    def __init__(self, interpreter: Interpreter, errorHandler: ErrorHandler, language: Language) -> None:
        self.interpreter: Interpreter = interpreter
        self.scopes: List[dict[str, bool]] = []
        self.currentFunction: FunctionType = FunctionType.NONE
        self.currentClass: ClassType = ClassType.NONE

        self.errorHandler: ErrorHandler = errorHandler
        self.language: Language = language

    # Statements

    @override
    def visitBlockStmt(self, stmt: Block) -> None:
        self.beginScope()
        self.resolveStatements(stmt.statements)
        self.endScope()

    @override
    def visitVarStmt(self, stmt: Var) -> None:
        self.declare(stmt.name)

        if stmt.initializer is not None:
            self.resolve(stmt.initializer)

        self.define(stmt.name)

    @override
    def visitFunctionStmt(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolveFunction(stmt, FunctionType.FUNCTION)

    @override
    def visitClassStmt(self, stmt: Class) -> None:
        enclosingClass: ClassType = self.currentClass
        self.currentClass = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme:
            self.errorHandler.error(stmt.superclass.name, 'A class can not inherit from itself')

        if stmt.superclass is not None:
            self.currentClass = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass is not None:
            self.beginScope()
            self.scopes[-1][self.retriveKeyword(TokenType.SUPER)] = True

        self.beginScope()
        
        self.scopes[-1][self.retriveKeyword(TokenType.THIS)] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            
            if method.name.lexeme == 'init':
                declaration = FunctionType.INITIALIZER
            
            self.resolveFunction(method, declaration)

        self.endScope()

        if stmt.superclass is not None:
            self.endScope()

        self.currentClass = enclosingClass

    @override
    def visitExpressionStmt(self, stmt: Expression) -> None:
        self.resolve(stmt.expression)

    @override
    def visitIfStmt(self, stmt: If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)

        if stmt.elseBranch is not None:
            self.resolve(stmt.elseBranch)

    @override
    def visitReturnStmt(self, stmt: Return) -> None:
        if stmt.value is not None:
            if self.currentFunction == FunctionType.INITIALIZER:
                self.errorHandler.error(stmt.keyword, "Can't return a value from an initializer")
            
            self.resolve(stmt.value)

    @override
    def visitWhileStmt(self, stmt: While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    # Expressions

    @override
    def visitVariableExpr(self, expr: Variable) -> None:
        if self.scopes != [] and self.scopes[-1].get(expr.name.lexeme) is False:
            self.errorHandler.error(expr.name, "Can't read local variable in its own initializer")

        self.resolveLocal(expr, expr.name)

    @override
    def visitAssignExpr(self, expr: Assign) -> None:
        self.resolve(expr.value)
        self.resolveLocal(expr, expr.name)

    @override
    def visitBinaryExpr(self, expr: Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    @override
    def visitCallExpr(self, expr: Call) -> None:
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    @override
    def visitGetExpr(self, expr: Get) -> None:
        self.resolve(expr.object)

    @override
    def visitSetExpr(self, expr: Set) -> None:
        self.resolve(expr.value)
        self.resolve(expr.object)

    @override
    def visitSuperExpr(self, expr: Super) -> None:
        if self.currentClass == ClassType.NONE:
            self.errorHandler.error(expr.keyword, 'Can not use "super" outside of a class')

        elif self.currentClass == ClassType.CLASS:
            self.errorHandler.error(expr.keyword, 'Can not use "super" in a class with no super class')

        self.resolveLocal(expr, expr.keyword)

    @override
    def visitThisExpr(self, expr: This) -> None:
        if self.currentClass == ClassType.NONE:
            self.errorHandler.error(expr.keyword, 'Can not use "this" outside of a class')
            return

        self.resolveLocal(expr, expr.keyword)

    @override
    def visitGroupingExpr(self, expr: Grouping) -> None:
        self.resolve(expr.expression)

    @override
    def visitUnaryExpr(self, expr: Unary) -> None:
        self.resolve(expr.right)

    @override
    def visitLiteralExpr(self, expr: Literal) -> None:
        pass

    # Helpers

    def resolve(self, exprOrStmt: Expr | Stmt) -> None:
        exprOrStmt.accept(self)

    def resolveStatements(self, statements: List[Stmt]) -> None:
        for statement in statements:
            self.resolve(statement)

    def resolveLocal(self, expr: Expr, name: Token) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def resolveFunction(self, function: Function, type: FunctionType) -> None:
        enclosingFunction: FunctionType = self.currentFunction
        self.currentFunction = type
        
        self.beginScope()

        for param in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolveStatements(function.body)

        self.endScope()
        
        self.currentFunction = enclosingFunction

    def beginScope(self) -> None:
        scope: dict[str, bool] = {}
        self.scopes.append(scope)

    def endScope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if self.scopes == []:
            return

        scope: dict[str, bool] = self.scopes[-1]

        if name.lexeme in scope:
            raise self.errorHandler.error(name, 'Already a variable with this name in this scope')
        
        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if self.scopes == []:
            return

        self.scopes[-1][name.lexeme] = True

    def retriveKeyword(self, type: TokenType) -> str:
        return next((k for k, v in self.language.keywords.items() if v == type), None)
