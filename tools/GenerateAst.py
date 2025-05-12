from sys import argv, exit
from typing import List

def main():
    if len(argv) != 2:
        print('Usage: py generateast.py [output directory]')
        exit(64)

    outputDir:str = argv[1]

    defineAst(
        outputDir, 
        'Expr',
        [
            'Assign | name: Token, value: Expr',
            'Binary | left: Expr, operator: Token, right: Expr',
            'Call | callee: Expr, paren: Token, arguments: List[Expr]',
            'Get | object: Expr, name: Token',
            'Set | object: Expr, name: Token, value: Expr',
            'Super | keyword: Token, method: Token',
            'This | keyword: Token',
            'Grouping | expression: Expr',
            'Literal | value: Any',
            'Unary | operator: Token, right: Expr',
            'Variable | name: Token',
        ]
    )
    
    defineAst(
        outputDir,
        'Stmt',
        [
            'If | condition: Expr, thenBranch: Stmt, elseBranch: Stmt',
            'While | condition: Expr, body: Stmt',
            'Var | name: Token, initializer: Expr',
            'Function | name: Token, params: List[Token], body: List[Stmt]',
            'Return | keyword: Token, value: Expr',
            'Block | statements: List[Stmt]',
            'Class | name: Token, superclass: Variable, methods: List["Function"]',
            'Expression | expression: Expr',
        ]
    )

def defineAst(outpurDir:str, baseName:str, types:List[str]):
    path = f'{outpurDir}/{baseName}.py'
    outputFile:str = open(path, 'w', encoding='UTF-8')

    # Imports
    outputFile.write('from abc import ABC, abstractmethod\n')
    outputFile.write('from Token import Token\n')
    if baseName == 'Expr': outputFile.write('from typing import Any, List, override\n')
    if baseName == 'Stmt': outputFile.write('from Expr import Expr, Variable\n'
                                            'from typing import List, override\n')

    # Base class
    outputFile.write(f'\nclass {baseName}(ABC):\n')
    outputFile.write(f'    class Visitor(ABC):\n')

    for type in types:
        typeName = type.split('|')[0].strip()
        outputFile.write(f'        @abstractmethod\n')
        outputFile.write(f'        def visit{typeName}{baseName}(self, {baseName.lower()}: "{typeName}"):\n')
        outputFile.write(f'            pass\n\n')

    outputFile.write(f'    @abstractmethod\n')
    outputFile.write(f'    def accept(self, visitor: Visitor):\n')
    outputFile.write(f'        pass\n')

    # The AST classes
    for type in types:
        className = type.split('|')[0].strip()
        fields = type.split('|')[1].strip()
        defineType(outputFile, baseName, className, fields)

def defineType(outputFile:str, baseName:str, className:str, fieldList:str):
    outputFile.write(f'\nclass {className}({baseName}):\n')
    outputFile.write(f'    def __init__(self, {fieldList}):\n')

    # Store parameters in fields
    fields:List[str] = fieldList.split(', ')
    for field in fields:
        nameAnnotation = field.strip()
        name = nameAnnotation.split(':')[0].strip()
        outputFile.write(f'        self.{nameAnnotation} = {name}\n')

    # Visitor pattern
    outputFile.write(f'\n    @override')
    outputFile.write(f'\n    def accept(self, visitor: {baseName}.Visitor):\n')
    outputFile.write(f'        return visitor.visit{className}{baseName}(self)\n')

if __name__ == '__main__':
    main()
