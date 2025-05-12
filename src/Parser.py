from TokenType import TokenType
from Token import Token
from Expr import Expr, Binary, Unary, Literal, Grouping, Variable, Assign, Call, Get, Set, This, Super
from Stmt import Stmt, Var, Expression, Block, If, While, Function, Return, Class
from ErrorHandler import ErrorHandler
from ErrorType import ErrorType
from typing import List

class Parser:
    class ParseError(RuntimeError):
        pass

    def __init__(self, tokens: List[Token], errorHandler: ErrorHandler) -> None:
        self.errorHandler = errorHandler

        self.tokens: List[Token] = tokens
        self.current: int = 0

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []

        while not self.isAtEnd():
            statements.append(self.declaration())
            while self.match(TokenType.NEWLINE): pass

        return statements

    # Statement grammar rules

    def declaration(self) -> Stmt:
        try:
            while self.match(TokenType.NEWLINE): pass
            if self.match(TokenType.VARIABLE): return self.variableDeclaration()
            if self.match(TokenType.FUNCTION): return self.functionDeclaration('function')
            if self.match(TokenType.CLASS): return self.classDeclaration()
            return self.statement()

        except self.ParseError:
            self.synchronize()

    def statement(self) -> Stmt:
        while self.match(TokenType.NEWLINE): pass
        if self.match(TokenType.IF): return self.ifStatement()
        if self.match(TokenType.WHILE): return self.whileStatement()
        if self.match(TokenType.FOR): return self.forStatement()
        if self.match(TokenType.RETURN): return self.returnStatement()
        if self.match(TokenType.BEGIN): return Block(self.blockStatement())
        return self.expressionStatement()

    def variableDeclaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, 'Expect variable name')

        initializer: Expr = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.NEWLINE, 'Expect new line after variable declaration')

        return Var(name, initializer)

    def functionDeclaration(self, kind: str) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, f'Expect {kind} name')

        self.consume(TokenType.LEFT_PAREN, f'Expect "(" after {kind} name')

        parameters: List[Token] = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                parameters.append(self.consume(TokenType.IDENTIFIER, 'Expect parameter name'))

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after parameters')
        self.consume(TokenType.BEGIN, 'Expect "begin" before '+f'{kind}'+' body')

        body: List[Stmt] = self.blockStatement()

        return Function(name, parameters, body)

    def classDeclaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, 'Expect class name')
        superclass: Variable = None
        
        if self.match(TokenType.INHERITS):
            self.consume(TokenType.IDENTIFIER, 'Expect superclass name')
            superclass = Variable(self.previous())

        self.consume(TokenType.BEGIN, 'Expect "begin" before class body')

        methods: List[Function] = []

        while not self.check(TokenType.END) and not self.isAtEnd():
            while self.match(TokenType.NEWLINE): pass
            methods.append(self.functionDeclaration('method'))
            while self.match(TokenType.NEWLINE): pass

        self.consume(TokenType.END, 'Expect "end" after class body')

        return Class(name, superclass, methods)

    def ifStatement(self) -> Stmt:
        condition: Expr = self.expression()

        self.consume(TokenType.BEGIN, 'Expect "begin" after the condition of an "if" statement')

        thenBranch: Stmt = Block(self.blockStatement())
        elseBranch: Stmt = None

        while self.match(TokenType.NEWLINE): pass
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()

        return If(condition, thenBranch, elseBranch)

    def whileStatement(self) -> Stmt:
        condition: Expr = self.expression()

        self.consume(TokenType.BEGIN, 'Expect "begin" after the condition of a "while" statement')

        body: Stmt = Block(self.blockStatement())

        return While(condition, body)

    def returnStatement(self) -> Stmt:
        keyword: Token = self.previous()
        value: Expr = None

        if not self.check(TokenType.NEWLINE):
            value = self.expression()

        self.consume(TokenType.NEWLINE, 'Expect new line after return value')            
        return Return(keyword, value)

    def blockStatement(self) -> List[Stmt]:
        statements: List[Stmt] = []

        while not self.check(TokenType.END) and not self.isAtEnd():
            statements.append(self.declaration())
            while self.match(TokenType.NEWLINE): pass

        self.consume(TokenType.END, 'Expect "end" after block')

        return statements

    def expressionStatement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.NEWLINE, 'Expect new line after expression statement') # Cannot start expression although one is expected here
        return Expression(expr)

    # Expression grammar rules

    def expression(self) -> Expr:
        while self.match(TokenType.NEWLINE): pass
        return self.assignment()

    def assignment(self) -> Expr:
        expr: Expr = self.or_()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()

            if isinstance(expr, Variable):
                return Assign(expr.name, value)

            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)

            raise self.errorHandler.error(equals, 'Invalid assignment target')

        return expr

    def or_(self) -> Expr:
        expr: Expr = self.and_()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.and_()
            expr = Binary(expr, operator, right)

        return expr

    def and_(self) -> Expr:
        expr: Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right = self.equality()
            expr = Binary(expr, operator, right)

        return expr

    def equality(self) -> Expr:
        expr: Expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr: Expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL,
                         TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr: Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr: Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self) -> Expr:
        expr: Expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)

            elif self.match(TokenType.DOT):
                name: Token = self.consume(TokenType.IDENTIFIER, 'Expect property after "."')
                expr = Get(expr, name)

            else:
                break

        return expr

    def finishCall(self, callee: Expr) -> Expr:
        arguments: List[Expr] = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break

        paren: Token = self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after arguments')

        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NONE): return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING): return Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER): return Variable(self.previous())
        if self.match(TokenType.THIS): return This(self.previous())
        if self.match(TokenType.SUPER):
            keyword: Token = self.previous()

            self.consume(TokenType.DOT, 'Expect "." after "super"')

            method: Token = self.consume(TokenType.IDENTIFIER, 'Expect superclass method name')

            return Super(keyword, method)

        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after expression')
            return Grouping(expr)

        raise self.error(self.peek(), 'Expect expression')

    # Helpers

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def check(self, type: TokenType) -> bool:
        if self.isAtEnd():
            return False

        return self.peek().type == type

    def advance(self) -> Token:
        if not self.isAtEnd():
            self.current += 1

        return self.previous()

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def isAtEnd(self) -> bool:
        return self.peek().type == TokenType.EOF

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        if type == TokenType.NEWLINE and self.peek().type == TokenType.EOF: return # Allows end of file as statement terminator
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        self.errorHandler.error(token, message)
        return self.ParseError

    def newError(self, token: Token, errorType: ErrorType, message: str) -> ParseError:
        self.errorHandler.newError(token, errorType, message)
        return self.ParseError

    def synchronize(self) -> None:
        self.advance()

        while not self.isAtEnd():
            if self.previous().type == TokenType.NEWLINE:
                return

            match self.peek().type:
                case TokenType.CLASS: return
                case TokenType.FUNCTION: return
                case TokenType.VARIABLE: return
                case TokenType.FOR: return
                case TokenType.IF: return
                case TokenType.WHILE: return
                case TokenType.RETURN: return

            self.advance()
