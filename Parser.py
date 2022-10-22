from rply import ParserGenerator
from Lexer import lg

from Ast import *

tokens = [x.name for x in lg.rules]

pg = ParserGenerator(
    tokens,

    precedence=[
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MULTIPLY', 'DIVIDE'])
    ]
)

@pg.production('program : function')
def program(p):
    return Program(p[0])

@pg.production('function : FN IDENTIFIER PAREN_OPEN PAREN_CLOSE SINGLE_ARROW IDENTIFIER BRACE_OPEN statement BRACE_CLOSE')
def function_decl(p):
    return Function(p[1], p[5], p[7])

@pg.production('statement : RETURN expr SEMICOLON')
def statement(p):
    return Return(p[1])

@pg.production('expr : expr binary_op expr | unary_op expr | INT')
def expression(p):
    if len(p) == 1: # Just int
        return Constant(p[0])

    elif len(p) == 2: # Unary
        op, expr = p[:2]
        return Unary.choose(op, expr)

    elif len(p) == 3: # Binary
        left, op, right = p[:3]
        return Binary.choose(op, left, right)


@pg.production('unary_op : EXCLAMATION | TILDE | MINUS')
def unary_op(p):
    return p[0]

@pg.production('binary_op : PLUS | MINUS | MULTIPLY | DIVIDE')
def binary_op(p):
    return p[0]

parser = pg.build()