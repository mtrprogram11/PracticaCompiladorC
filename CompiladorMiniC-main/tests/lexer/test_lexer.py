"""Pruebas del analizador léxico de Mini C segun SKILL.md y CLAUDE.md."""

from minic.lexer import Lexer, Token, TokenType
from minic.output import format_diagnostic, format_token


def test_empty_source() -> None:
    tokens, diagnostics = Lexer("").scan()
    assert diagnostics == []
    assert len(tokens) == 1
    assert tokens[0] == Token(TokenType.EOF, "", None, 1, 1)


def test_keywords_and_identifiers() -> None:
    source = "int while int2 whilex _ident"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    expected_types = [
        TokenType.KW_INT,
        TokenType.KW_WHILE,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types
    assert [t.lexeme for t in tokens] == ["int", "while", "int2", "whilex", "_ident", ""]


def test_integer_literals() -> None:
    source = "0 42 007"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    assert len(tokens) == 4
    assert tokens[0] == Token(TokenType.INTEGER_LITERAL, "0", 0, 1, 1)
    assert tokens[1] == Token(TokenType.INTEGER_LITERAL, "42", 42, 1, 3)
    assert tokens[2] == Token(TokenType.INTEGER_LITERAL, "007", 7, 1, 6)
    assert tokens[3] == Token(TokenType.EOF, "", None, 1, 9)


def test_operators_and_symbols() -> None:
    source = "= == != + - ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    expected = [
        (TokenType.ASSIGN, "="),
        (TokenType.EQUAL_EQUAL, "=="),
        (TokenType.NOT_EQUAL, "!="),
        (TokenType.PLUS, "+"),
        (TokenType.MINUS, "-"),
        (TokenType.LPAREN, "("),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACE, "{"),
        (TokenType.RBRACE, "}"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.EOF, ""),
    ]
    assert [(t.type, t.lexeme) for t in tokens] == expected


def test_skill_test_case_1_valid() -> None:
    """Caso de prueba 1 de la sección 7 de SKILL.md."""
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    formatted = [format_token(t) for t in tokens]
    expected = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    assert formatted == expected


def test_skill_test_case_2_with_errors() -> None:
    """Caso de prueba 2 con errores de la sección 7 de SKILL.md."""
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    token_lines = [format_token(t) for t in tokens]
    expected_tokens = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    assert token_lines == expected_tokens

    diag_lines = [format_diagnostic(d) for d in diagnostics]
    expected_diags = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    assert diag_lines == expected_diags


def test_whitespace_and_tab_positions() -> None:
    """Tabs cuentan como 1 columna y no alinean (SKILL.md §9.3)."""
    source = "\tvar\r\n\t\tint"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []
    # Línea 1: '\t' es col 1 -> 'var' en col 2..4 -> '\r' col 5 -> '\n' pasa a línea 2, col 1
    # Línea 2: '\t' col 1 -> '\t' col 2 -> 'int' en col 3
    assert tokens[0].lexeme == "var"
    assert (tokens[0].line, tokens[0].column) == (1, 2)
    assert tokens[1].lexeme == "int"
    assert (tokens[1].line, tokens[1].column) == (2, 3)
