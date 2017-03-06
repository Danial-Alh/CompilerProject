# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex
from ply.lex import TOKEN

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
    'and': 'AND',
    'or': 'OR',
    'and then': 'AND_THEN',
    'or else': 'OR_ELSE',
    'not': 'NOT',
}

# List of token names.   This is always required
tokens = [
             'ID', 'NUMCONST', 'CHARCONST', 'WHITE_SPACE', 'COMMENTS'
         ] + list(reserved.values())

letter = r'([a-zA-Z])'
digit = r'([0-9])'
identifier = r'(' + letter + r'+)'

@TOKEN(identifier)
def t_ID(t):
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t

numconst = r'(#' + digit + r'+(\.' + digit + r'+)?)'

@TOKEN(numconst)
def t_NUMCONST(t):
    return t

backslash_const_char = r'(\\(.))'
quoted_const_char = r''
char_const = r'(' + backslash_const_char + '|' + quoted_const_char + r')'

def t_CHARCONST(t):
    return t


def t_WHITE_SPACE(t):
    return t


def t_COMMENTS(t):
    return t