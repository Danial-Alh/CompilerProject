# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

# List of reserved words
from ply.lex import TOKEN

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
    return


def t_NUMCONST(t):
    r''
    return


def t_WHITE_SPACE(t):
    return


def t_COMMENTS(t):
    return