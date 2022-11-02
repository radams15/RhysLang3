from AstUtils import *

from rply.token import BaseBox, Token

class Program(BaseBox):
    def __init__(self, toplevels):
        if type(toplevels) == list:
            self.toplevels = toplevels
        else:
            self.toplevels = [toplevels]

    def visit(self, visitor):
        visitor.visit_program(self)

    def __repr__(self):
        out = 'Program:\n'

        for toplevel in self.toplevels:
            out += str(toplevel)

        return out

class StructDef(BaseBox):
    def __init__(self, name, memebers, methods):
        self.name = name.value
        self.members = [(memebers[x].value , memebers[x + 1].value) for x in range(0, len(memebers), 2)]
        self.methods: list[Function] = methods

        self.indexes = dict()

    def visit(self, visitor):
        visitor.visit_struct_def(self)

class Function(BaseBox):
    def __init__(self, name, return_val, args, block=None):
        self.name = name.value
        self.return_val = return_val
        self.args = [(args[x].value, args[x+1].value) for x in range(0, len(args), 2)]
        self.arity = len(args)
        self.block = block

    def visit(self, visitor):
        visitor.visit_function(self)

    def __repr__(self):
        return '''Function {} ({}){
    {}
    }'''.format(self.name.value, "\n\t".join([x[0] + ": " + x[1] for x in self.args]), str(self.block))

class Statement(BaseBox):
    pass

class Expression(BaseBox):
    pass

class Return(Statement):
    def __init__(self, expr):
        self.expr = expr

    def visit(self, visitor):
        visitor.visit_return(self)

    def __repr__(self):
        return f'Return {str(self.expr)}'

class Unary(Expression):
    def __init__(self, operator, expr):
        self.operator = operator
        self.expr = expr

    @staticmethod
    def choose(operator, expr):
        if operator.name == 'TILDE':
            return Complement(operator, expr)

        elif operator.name == 'MINUS':
            return Negation(operator, expr)

        elif operator.name == 'EXCLAMATION':
            return LogicalNegation(operator, expr)

        else:
            raise Exception(f'Invalid unary operator: {operator}')
        
class Negation(Unary): # -
    def visit(self, visitor):
        visitor.visit_negation(self)

class Complement(Unary): # ~
    def visit(self, visitor):
        visitor.visit_complement(self)

class LogicalNegation(Unary): # !
    def visit(self, visitor):
        visitor.visit_logical_negation(self)


class Binary(Expression):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    @staticmethod
    def choose(operator, left, right):
        if operator.name == 'MINUS':
            return Subtraction(operator, left, right)

        elif operator.name == 'PLUS':
            return Addition(operator, left, right)

        elif operator.name == 'MULTIPLY':
            return Multiplication(operator, left, right)

        elif operator.name == 'EXPONENT':
            return Exponent(operator, left, right)

        elif operator.name == 'DIVIDE':
            return Division(operator, left, right)

        elif operator.name == 'OR':
            return Or(operator, left, right)

        elif operator.name == 'AND':
            return And(operator, left, right)

        elif operator.name == 'GREATER_THAN':
            return GreaterThan(operator, left, right)

        elif operator.name == 'LESS_THAN':
            return LessThan(operator, left, right)

        elif operator.name == 'GREATER_THAN_EQUAL':
            return LogicalNegation(None, LessThan(operator, left, right))

        elif operator.name == 'LESS_THAN_EQUAL':
            return LogicalNegation(None, GreaterThan(operator, left, right))

        elif operator.name == 'EQUAL_EQUAL':
            return Equal(operator, left, right)

        elif operator.name == 'NOT_EQUAL':
            return LogicalNegation(None, Equal(operator, left, right))

        elif operator.name == 'PIPE':
            return BitwiseOr(operator, left, right)

        elif operator.name == 'XOR':
            return BitwiseAnd(operator, left, right)

        elif operator.name == 'XOR':
            return BitwiseXor(operator, left, right)

        else:
            raise Exception(f'Invalid binary operator: {operator}')

class BitwiseAnd(Binary):
    def visit(self, visitor):
        visitor.visit_bitwise_and(self)


class BitwiseXor(Binary):
    def visit(self, visitor):
        visitor.visit_bitwise_xor(self)


class BitwiseOr(Binary):
    def visit(self, visitor):
        visitor.visit_or(self)

class Or(Binary):
    def visit(self, visitor):
        visitor.visit_or(self)


class And(Binary):
    def visit(self, visitor):
        visitor.visit_and(self)

class Equal(Binary):
    def visit(self, visitor):
        visitor.visit_equal(self)

class GreaterThan(Binary):
    def visit(self, visitor):
        visitor.visit_greater_than(self)

class LessThan(Binary):
    def visit(self, visitor):
        visitor.visit_less_than(self)

class Addition(Binary):
    def visit(self, visitor):
        visitor.visit_addition(self)

class Subtraction(Binary):
    def visit(self, visitor):
        visitor.visit_subtraction(self)

class Multiplication(Binary):
    def visit(self, visitor):
        visitor.visit_multiplication(self)

class Exponent(Binary):
    def visit(self, visitor):
        visitor.visit_exponent(self)

class Division(Binary):
    def visit(self, visitor):
        visitor.visit_division(self)

class Variable(Expression):
    def __init__(self, name):
        self.name = name.value

    def visit(self, visitor):
        visitor.visit_variable(self)

class Constant(Expression):
    def __init__(self, value):
        if type(value) == Token:
            self.value = value.value
        else:
            self.value = value

    def visit(self, visitor):
        visitor.visit_constant(self)

    def size(self):
        return 16

class Global(Expression):
    def __init__(self, name, type, value=None):
        self.name = name
        self.type = type
        self.value = value

    def visit(self, visitor):
        visitor.visit_global(self)

class Char(Constant):
    def __init__(self, data):
        data = ord(data.value[1:-1])

        super().__init__(data)

class String(Expression):
    def __init__(self, data):
        data = data.value[1:-1]

        self.data = unicode_deescape(data)
        self.id = None

    def visit(self, visitor):
        visitor.visit_string(self)

class Declaration(Expression):
    def __init__(self, name, type, initialiser=None):
        self.name = name.value
        self.type = type.value
        self.initialiser = initialiser

    def visit(self, visitor):
        visitor.visit_declaration(self)

class Assignment(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def visit(self, visitor):
        visitor.visit_assignment(self)

class If(Statement):
    def __init__(self, expr, true_stmt, false_stmt=None):
        self.expr = expr
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt

    def visit(self, visitor):
        visitor.visit_if(self)

class Ternary(Expression):
    def __init__(self, expr, true_expr, false_expr=None):
        self.expr = expr
        self.true_expr = true_expr
        self.false_expr = false_expr

    def visit(self, visitor):
        visitor.visit_ternary(self)


class Block(Statement):
    def __init__(self, statements):
        if type(statements) == list:
            self.statements = statements
        else:
            self.statements = [statements]

    def visit(self, visitor):
        for stmt in self.statements:
            stmt.visit(visitor)

class Loop(Statement):
    def __init__(self, expr, body):
        self.expr = expr
        self.body = body

    def visit(self, visitor):
        visitor.visit_loop(self)

class Syscall(Statement):
    def __init__(self, function):
        self.name = function.name
        self.args = function.args

    def visit(self, visitor):
        visitor.visit_syscall(self)

class FunctionCall(Statement):
    def __init__(self, name, args):
        self.name = name.value

        if type(args) == list:
            self.args = args
        else:
            self.args = [args]

    def visit(self, visitor):
        visitor.visit_function_call(self)

class StructGet(Expression):
    def __init__(self, struct_name, item_name):
        self.struct_name = struct_name.value
        self.item_name = item_name.value

    def visit(self, visitor):
        visitor.visit_struct_get(self)

class StructSet(Expression):
    def __init__(self, member, expr):
        self.member = member
        self.expr = expr

    def visit(self, visitor):
        visitor.visit_struct_set(self)

class StructMethodCall(Expression):
    def __init__(self, member, function):
        self.member = member.value
        self.function: FunctionCall = function

    def visit(self, visitor):
        visitor.visit_struct_method_call(self)