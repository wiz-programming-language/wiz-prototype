from language.Language import Language
from Scanner import Scanner
from Parser import Parser
from Interpreter import Interpreter
from Resolver import Resolver
from ErrorHandler import ErrorHandler
from Stmt import Stmt
from Token import Token
from typing import List
from sys import argv, exit
from re import search
import keyboard

class Wiz:
    def __init__(self) -> None:
        self.language: Language
        self.errorHandler: ErrorHandler
        self.interpreter: Interpreter

    def main(self) -> None:
        if len(argv) > 2:
            print('Usage: wiz [script].wiz')
            exit(64)

        elif len(argv) == 2:
            if not argv[1].endswith('.wiz'):
                print('Can only run files ending with ".wiz" extension')
                exit(64)

            self.runFile(argv[1])

        else:
            self.runPrompt()

    def runFile(self, path: str) -> None:
        try:
            with open(path, 'r') as file:
                source = file.read()
                self.findLanguage(source)
                self.run(source, False)

        except FileNotFoundError as error:
            print(f'\033[31mError: File not found\033[0m\n')
            print(f' {error.filename}\n')
            print(f' Verify if the path name is correct')
            exit(64)

        if self.errorHandler.hadError: exit(65)
        if self.errorHandler.hadRuntimeError: exit(70)

    def runPrompt(self) -> None:
        try:
            print('Wiz v0.0.1')
            self.selectLanguage()

            while True:
                self.run(input('> '), True)
                self.errorHandler.hadError = False

        except KeyboardInterrupt:
            print('\nExiting...')
            exit(0)

    def run(self, source: str, isREPL: bool) -> None:
        scanner = Scanner(source, self.language.keywords, self.errorHandler)
        tokens: List[Token] = scanner.scanTokens()
        if self.errorHandler.hadError: return

        parser = Parser(tokens, self.errorHandler)
        statements: List[Stmt] = parser.parse()
        if self.errorHandler.hadError: return

        resolver = Resolver(self.interpreter, self.errorHandler, self.language)
        resolver.resolveStatements(statements)
        if self.errorHandler.hadError: return

        self.interpreter.interpret(statements, isREPL)

    def findLanguage(self, source: str) -> None:
        matchLanguage = search(r'^\s*@\s*(\w+)', source)

        if not matchLanguage:
            lines: List[str] = source.splitlines()

            for lineNumber, line in enumerate(lines, start=1):
                if line.strip():
                    print(f'\033[31mError: Language not defined\033[0m\n')
                    print(f' {lineNumber} | {line}\n')
                    print(f' Language must be defined before code')
                    exit(64)

        language = matchLanguage.group(1)

        if language not in ['English', 'Português', 'PortuguÃªs']:
            print('Incorrect language')
            exit(64)
        if language == 'PortuguÃªs': language = 'Português'

        self.language = Language(language)
        self.errorHandler = ErrorHandler(self.language.errors)
        self.interpreter = Interpreter(self.errorHandler, self.language)

    def selectLanguage(self) -> None:
        languages = ['English', 'Português']
        current = 0

        print('Select language')

        def displayMenu():
            for i, language in enumerate(languages):
                if i == current:
                    print(f'> {language}')

                else:
                    print(f'  {language}')

        displayMenu()

        while True:
            key = keyboard.read_event(suppress=True)

            if key.event_type == keyboard.KEY_DOWN and key.name in ['up', 'down']:
                if key.name == 'down':
                    current = (current + 1) % len(languages)

                elif key.name == 'up':
                    current = (current - 1) % len(languages)

                print('\033[F' * len(languages), end='')
                displayMenu()

            elif key.event_type == keyboard.KEY_DOWN and key.name == 'enter':
                languageName: str = languages[current]
                print('\033[F\033[K' * (len(languages) + 1), end='')
                print(f'\033[34mSelected language: {languageName}\033[0m')

                self.language = Language(languageName)
                self.errorHandler = ErrorHandler(self.language.errors)
                self.interpreter = Interpreter(self.errorHandler, self.language)
                break

if __name__ == '__main__':
    Wiz().main()
