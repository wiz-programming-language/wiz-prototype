from ErrorType import ErrorType

english = {
    ErrorType.UNEXPECTED_CHARACTER: 'Invalid character',
    ErrorType.UNTERMINATED_STRING: '',
    ErrorType.INCOMPLETE_KEYWORD: ''
}

portuguese = {
    ErrorType.UNEXPECTED_CHARACTER: '',
    ErrorType.UNTERMINATED_STRING: '',
    ErrorType.INCOMPLETE_KEYWORD: ''
}


errorsMessages: dict[ErrorType, str] = {
    'English': english,
    'Português': portuguese,
}
