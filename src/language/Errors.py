from ErrorType import ErrorType

english = {
    ErrorType.UNEXPECTED_CHARACTER: 'Unexpected character',
    ErrorType.UNTERMINATED_STRING: 'Unterminated text value (string)',
    ErrorType.INCOMPLETE_KEYWORD: 'Incomplete keyword'
}

portuguese = {
    ErrorType.UNEXPECTED_CHARACTER: 'Caráter inesperado',
    ErrorType.UNTERMINATED_STRING: 'Valor de texto Unterminated text value (string)',
    ErrorType.INCOMPLETE_KEYWORD: 'Palavra-chave incompleto'
}

errors: dict[ErrorType, str] = {
    'English': english,
    'Português': portuguese,
}
