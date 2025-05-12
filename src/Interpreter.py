from Expr import Expr, Literal, Unary, Grouping, Binary, Variable, Assign, Call, Get, Set, This, Super
from Stmt import Stmt, Expression, Var, Block, If, While, Function, Return, Class

from Environment import Environment
from Callable import Callable
from FunctionCall import FunctionCall
from Return import Return_
from ClassCall import ClassCall
from Instance import Instance

from TokenType import TokenType
from Token import Token

from ErrorHandler import ErrorHandler
from RuntimeError import RuntimeError

from lib.StdLib import defineStdLib
from language.Language import Language

from typing import Any, List, override

class Interpreter(Expr.Visitor, Stmt.Visitor):
    def __init__(self, errorHandler: ErrorHandler, language: Language) -> None:
        self.globals: Environment = Environment()
        self.environment: Environment = self.globals
        self.locals: dict[Expr, int] = {}

        self.errorHandler = errorHandler
        self.language = language

        defineStdLib(self.globals, self.language)

    def interpret(self, statements: List[Stmt], isREPL: bool) -> None:
        try:
            for statement in statements:
                self.execute(statement)

                if isREPL:
                    if isinstance(statement, Expression):
                        print(self.evaluate(statement.expression))

        except RuntimeError as error:
            self.errorHandler.runtimeError(error)

    # Statements
    
    @override
    def visitExpressionStmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    @override
    def visitIfStmt(self, stmt: If) -> None:
        if self.isTrue(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)

        elif stmt.elseBranch is not None:
            self.execute(stmt.elseBranch)

    @override
    def visitWhileStmt(self, stmt: While):
        while self.isTrue(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

        return None

    @override
    def visitVarStmt(self, stmt: Var) -> None:
        value: Any = None
        
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    @override
    def visitFunctionStmt(self, stmt: Function) -> None:
        function: FunctionCall = FunctionCall(stmt, self.environment, False, self.language)
        self.environment.define(stmt.name.lexeme, function)

    @override
    def visitReturnStmt(self, stmt: Return) -> None:
        value: Any = None

        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise Return_(value)

    @override
    def visitClassStmt(self, stmt: Class) -> None:
        superclass: Any = None

        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)

            if not isinstance(superclass, ClassCall):
                raise RuntimeError(stmt.superclass.name, 'Superclass must be a class')

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define(self.retriveKeyword(TokenType.SUPER), superclass)

        methods: dict[str, FunctionCall] = {}

        for method in stmt.methods:
            function: FunctionCall = FunctionCall(method, self.environment, method.name.lexeme == 'init', self.language)
            methods[method.name.lexeme] = function

        class_ = ClassCall(stmt.name.lexeme, superclass, methods)

        if superclass is not None:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, class_)

    @override
    def visitBlockStmt(self, stmt: Block) -> None:
        self.executeBlock(stmt.statements, Environment(self.environment))

    # Expressions

    @override
    def visitLiteralExpr(self, expr: Literal) -> Any:
        return expr.value

    @override
    def visitUnaryExpr(self, expr: Unary) -> Any:
        right: Any = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.NOT:
                return not self.isTrue(right)

            case TokenType.MINUS:
                if isinstance(right, float):
                    return -right

                raise RuntimeError(expr.operator, 'Operand must be a number')

    @override
    def visitGroupingExpr(self, expr: Grouping) -> Any:
        return self.evaluate(expr.expression)

    @override
    def visitBinaryExpr(self, expr: Binary) -> Any:
        left: Any = self.evaluate(expr.left)

        match expr.operator.type:
            case TokenType.OR:
                if self.isTrue(left):
                    return left
                else:
                    return self.evaluate(expr.right)

            case TokenType.AND:
                if not self.isTrue(left):
                    return left
                else:
                    return self.evaluate(expr.right)

        right: Any = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG_EQUAL: return left != right
            case TokenType.EQUAL_EQUAL: return left == right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float): return left + right
                if isinstance(left, str) and isinstance(right, str): return left + right
                raise RuntimeError(expr.operator, 'Operands must be two numbers or two strings')

        # Number-only (currently) operations

        if not(isinstance(left, float) and isinstance(right, float)):
            raise RuntimeError(expr.operator, 'Operands must be numbers')

        match expr.operator.type:
            case TokenType.MINUS: return left - right
            case TokenType.SLASH: return left / right
            case TokenType.STAR: return left * right
            case TokenType.GREATER: return left > right
            case TokenType.GREATER_EQUAL: return left >= right
            case TokenType.LESS: return left < right
            case TokenType.LESS_EQUAL: return left <= right

    @override
    def visitCallExpr(self, expr: Call) -> Any:
        callee: Any = self.evaluate(expr.callee)

        if not isinstance(callee, Callable):
            raise RuntimeError(expr.paren, 'Can only call functions and classes')

        if hasattr(callee, 'checkArity'):
            callee.checkArity(expr.arguments, expr)

        if len(expr.arguments) != callee.arity():
            raise RuntimeError(expr.paren, f'Expected {callee.arity()} argument(s) but got {len(expr.arguments)}')

        arguments: List[Any] = []

        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        return callee.call(self, arguments)

    @override
    def visitGetExpr(self, expr: Get) -> Any:
        object: Any = self.evaluate(expr.object)

        if isinstance(object, Instance):
            return object.get(expr.name)

        raise RuntimeError(expr.name, 'Only instances have properties')

    @override
    def visitSetExpr(self, expr: Set) -> Any:
        object: Any = self.evaluate(expr.object)

        if not isinstance(object, Instance):
            raise RuntimeError(expr.name, 'Only instances have fields')

        value = self.evaluate(expr.value)
        object.set(expr.name, value)

        return value

    @override
    def visitSuperExpr(self, expr: Super) -> FunctionCall:
        distance: int = self.locals[expr]

        superclass: ClassCall = self.environment.getAt(distance, self.retriveKeyword(TokenType.SUPER))
        object: Instance = self.environment.getAt(distance - 1, self.retriveKeyword(TokenType.THIS))

        method: FunctionCall = superclass.findMethod(expr.method.lexeme)

        if method is None:
            raise RuntimeError(expr.method, f'Undefined property {expr.method.lexeme}')

        return method.bind(object)

    @override
    def visitThisExpr(self, expr: This) -> Any:
        return self.lookUpVariable(expr.keyword, expr)

    @override
    def visitVariableExpr(self, expr: Variable) -> Any:
        return self.lookUpVariable(expr.name, expr)

    @override
    def visitAssignExpr(self, expr: Assign):
        value: Any = self.evaluate(expr.value)

        distance: int = self.locals.get(expr)
        
        if distance is not None:
            self.environment.assignAt(distance, expr.name, value)

        else:
            self.globals.assign(expr.name, value)

        return value

    # Helpers

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def executeBlock(self, statements: List[Stmt], environment: Environment) -> None:
        previous: Environment = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)

        finally:
            self.environment = previous

    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

    def lookUpVariable(self, name: Token, expr: Expr) -> Any:
        distance: int = self.locals.get(expr)
        
        if distance is not None:
            return self.environment.getAt(distance, name.lexeme)

        else:
            return self.globals.get(name)

    def isTrue(self, object: Any) -> bool:
        if object is None:
            return False

        if isinstance(object, bool):
            return bool(object)

        return True

    def retriveKeyword(self, type: TokenType) -> str:
        return next((k for k, v in self.language.keywords.items() if v == type), None)
