import itertools

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

@pg.production('function : FN IDENTIFIER PAREN_OPEN PAREN_CLOSE SINGLE_ARROW type block')
def function_decl(p):
    return Function(p[1], p[5], p[6])

def flatten_list(inp, out):
    for item in inp:
        if isinstance(item, list):
            flatten_list(item, out)
        else:
            out.append(item)

@pg.production('statements : statement | statements statement')
def statements(p):
    if len(p) == 1:
        return p[0]

    stmts = []

    flatten_list(p, stmts)

    return stmts

@pg.production('block : BRACE_OPEN statements BRACE_CLOSE')
def block(p):
    return Block(p[1])

@pg.production('statement : RETURN expr SEMICOLON |' +
               'expr SEMICOLON |' +
               'IF PAREN_OPEN expr PAREN_CLOSE block |' +
               'IF PAREN_OPEN expr PAREN_CLOSE block ELSE block |' +
               'FOR PAREN_OPEN expr SEMICOLON expr SEMICOLON expr PAREN_CLOSE block |' +
               'WHILE PAREN_OPEN expr PAREN_CLOSE block' +
               '')
def statement(p):
    if p[0].name == 'RETURN':
        return Return(p[1])

    if len(p) == 5:
        if p[0].name == 'IF':
            return If(p[2], p[4])
        elif p[0].name == 'WHILE':
            return Loop(p[2], p[4])
        else:
            print('UNKNOWN:', p[0])

    if len(p) == 7:
        return If(p[2], p[4], p[6])

    if len(p) == 9:
        init, constraint, inc, body = p[2], p[4], p[6], p[8]

        body = Block(
            [
                body,
                inc
            ]
        )

        body = Loop(constraint, body)

        body = Block(
            [
                init,
                body
            ]
        )

        return body

    return p[0]

@pg.production('expr : VAR IDENTIFIER COLON type | VAR IDENTIFIER COLON type EQUAL expr | IDENTIFIER EQUAL expr | ternary')
def expression(p):
    if len(p) == 1:  # Just ternary
        return p[0]

    elif len(p) == 4:  # Declaration
        name, type = p[1], p[3]
        return Declaration(name, type)

    elif len(p) == 3: # Assignment
            return Assignment(p[0], p[2])

    elif len(p) == 6:  # Definition
        name, type, expr = p[1], p[3], p[5]
        return Declaration(name, type, expr)

@pg.production('ternary : logical_or | logical_or QUESTION expr COLON ternary')
def ternary(p):
    if len(p) == 1:  # Just or
        return p[0]

    else:
        return Ternary(p[0], p[2], p[4])

@pg.production('logical_or : logical_and | logical_and OR logical_and')
def logical_or(p):
    if len(p) == 1:  # Just term
        return p[0]

    elif len(p) == 3:  # Unary
        left, op, right = p[:3]
        return Binary.choose(op, left, right)

@pg.production('logical_and : equality | equality AND equality')
def logical_and(p):
    if len(p) == 1:  # Just term
        return p[0]

    elif len(p) == 3:  # Unary
        left, op, right = p[:3]
        return Binary.choose(op, left, right)

@pg.production('equality : relational | relational equality_op relational')
def equality(p):
    if len(p) == 1:  # Just relational
        return p[0]

    elif len(p) == 3:  # Unary
        left, op, right = p[:3]
        return Binary.choose(op, left, right)

@pg.production('relational : additive | additive relational_op additive')
def relational(p):
    if len(p) == 1:  # Just term
        return p[0]

    elif len(p) == 3:  # Unary
        left, op, right = p[:3]
        return Binary.choose(op, left, right)

@pg.production('additive : term | term binary_op_1 term')
def additive(p):
    if len(p) == 1: # Just term
        return p[0]

    elif len(p) == 3: # Unary
        left, op, right = p[:3]
        return Binary.choose(op, left, right)

@pg.production('term : term binary_op_2 term | factor')
def term(p):
    if len(p) == 1:  # Just factor
        return p[0]

    elif len(p) == 3:  # term with signs
        left, op, right = p[:3]
        return Binary.choose(op, left, right)

@pg.production('factor : PAREN_OPEN expr PAREN_CLOSE | unary_op factor | INT | IDENTIFIER')
def factor(p):
    if len(p) == 1: # Just int
        if p[0].name in ('INT', 'FLOAT'):
            return Constant(p[0])
        else:
            return Variable(p[0])

    elif len(p) == 2: # Unary
        op, expr = p[:2]
        return Unary.choose(op, expr)

    elif len(p) == 3: # Binary
        return p[1]

@pg.production('unary_op : EXCLAMATION | TILDE | MINUS')
def unary_op(p):
    return p[0]

@pg.production('binary_op_1 : PLUS | MINUS')
def binary_op_1(p):
    return p[0]
@pg.production('binary_op_2 : MULTIPLY | DIVIDE | EXPONENT')
def binary_op_2(p):
    return p[0]

@pg.production('relational_op : LESS_THAN | GREATER_THAN | LESS_THAN_EQUAL | GREATER_THAN_EQUAL')
def relational_op(p):
    return p[0]

@pg.production('equality_op : EQUAL_EQUAL | NOT_EQUAL')
def equality_op(p):
    return p[0]

@pg.production('type : IDENTIFIER')
def type(p):
    return p[0]

parser = pg.build()