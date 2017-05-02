# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex
from assets import symbol_table
from ply.lex import TOKEN
import copy

# List of reserved words
reserved = {
    'program': 'PROGRAM',
    'main': 'MAIN',
    'int': 'INT',
    'real': 'REAL',
    'char': 'CHAR',
    'boolean': 'BOOLEAN',
    'procedure': 'PROCEDURE',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'do': 'DO',
    'while': 'WHILE',
    'for': 'FOR',
    'switch': 'SWITCH',
    'end': 'END',
    'return': 'RETURN',
    'exit': 'EXIT',
    'when': 'WHEN',
    'upto': 'UPTO',
    'downto': 'DOWNTO',
    'case': 'CASE',
    'default': 'DEFAULT',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
}

# List of token names.   This is always required
tokens = [
             'ID', 'NUMCONST', 'REALCONST', 'BOOLCONST', 'CHARCONST',
             'LT', 'LE', 'GT', 'GE', 'EQ', 'NEQ', 'LPAR', 'RPAR', 'LBRACK', 'RBRACK', 'LBRACE', 'RBRACE',
             'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD', 'ASSIGNMENT_SIGN',
             'SEMICOLON', 'DOUBLE_DOT', 'COMMA', 'COLON'
         ] + list(reserved.values())

letter = r'([a-zA-Z])'
zero = r'(0)'
non_zero_digit = r'([1-9])'
digit = r'([0-9])'
identifier = r'(' + letter + r'+)'
backslash_charconst = r'(\\(.))'
quoted_charconst = r'(\'(.)\')'
charconst = r'(' + backslash_charconst + r'|' + quoted_charconst + r')'
numconst = r'(\#(' + non_zero_digit + digit + r'*|' + zero + r'))'
realconst = r'(\#(' + non_zero_digit + digit + r'*|' + zero + r')\.(' + \
            digit + r'*' + non_zero_digit + r'|' + zero + r'))'
boolconst = r'((true)|(false))'

t_ignore = ' \t'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_EQ = r'='
t_NEQ = r'<>'
t_LPAR = r'\('
t_RPAR = r'\)'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'\/'
t_MOD = r'%'
t_ASSIGNMENT_SIGN = r'\:='
t_SEMICOLON = r';'
t_DOUBLE_DOT = r'\.\.'
t_COLON = r'\:'
t_COMMA = r'\,'


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return


@TOKEN(realconst)
def t_REALCONST(t):
    t.value = {"value": float(t.value[1:]), "type": "real"}
    return t


@TOKEN(numconst)
def t_NUMCONST(t):
    t.value = {"value": int(t.value[1:]), "type": "int"}
    return t


@TOKEN(charconst)
def t_CHARCONST(t):
    if t.value == "\\0":
        t.value = {"value": "NULL", "type": "character"}
    elif t.value[0] == '\'':
        t.value = {"value": "\'" + t.value[1:len(t.value) - 1] + "\'", "type": "character"}
    else:
        t.value = {"value": "\'" + t.value[1:] + "\'", "type": "character"}
    return t


@TOKEN(boolconst)
def t_BOOLCONST(t):
    t.value = {"value": t.value, "type": "boolean"}
    return t


def t_COMMENTS(t):
    r'//.*'
    return


@TOKEN(identifier)
def t_ID(t):
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    if t.type == "ID":
        if t.value in symbol_table:
            index = symbol_table.index(t.value)
            t.value = copy.deepcopy(symbol_table[index])
        else:
            t.value = symbol_table.get_new_variable_dictionary(t.value)
    return t


def t_error(t):
    print("Illegal character " + str(t.value[0]) + " line num: " + str(t.lineno))
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()
# # read input file
# code = None
# with open('./input.dm', 'r') as input_file:
#     code = input_file.read()
# # Give the lexer some input
# lexer.input(code)
#
# # Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break  # No more input
#     print(tok)
