from rply.token import BaseBox, Token


class LabelGenerator:
    def __init__(self, start=0):
        self.counter = start

    def generate(self, type='label'):
        self.counter += 1
        return '{}_{}'.format(type, self.counter, '_end')

    def generate_both(self, type='label'):
        start = self.generate(type)
        return (start, start+'_end')

class Scope:
    def __init__(self, parent=None, index=0):
        self.values = dict()
        self.parent = parent

        self.index = 0

    def child(self):
        return Scope(self)

    def _set(self, name, value):
        self.values[name] = value

    def set(self, name, value):
        owner = self.find_owner(name)

        if not owner:
            owner = self

        owner._set(name, value)

    def contains(self, name):
        return name in self.values

    def find_owner(self, name):
        if self.contains(name):
            return self

        if self.parent:
            return self.parent.find_owner(name)

    def _get(self, name):
        return self.values[name]

    def get(self, name):
        owner = self.find_owner(name)

        if owner:
            return owner._get(name)

        raise Exception("Unknown variable: {}".format(name))

scope = Scope()

int_size = 8

var_map = dict()
stack_index = -int_size

label_generator = LabelGenerator()

def sizeof(type):
    if type == 'int':
        return 8

    else:
        raise Exception('Unknown type: {}'.format(type))

class Program(BaseBox):
    def __init__(self, function):
        self.function = function

    def visit(self, writer):
        with open('x86_boilerplate.nasm', 'r') as f:
            writer.writeln(f.read() + '\n')

        #writer.ident -= 1

        self.function.visit(writer)

        '''writer.writeln('')
        writer.writeln('global _start')
        writer.writeln('_start:') # Make start function to call main then exit normally
        writer.ident += 1
        writer.writeln('call main')
        writer.writeln('')
        writer.writeln('mov rdi, rax') # Move main return value into exit syscall arg
        writer.writeln('mov rax, 60') # Move exit syscall code into rax
        writer.writeln('syscall')'''

class Function(BaseBox):
    def __init__(self, name, return_val, block):
        self.name = name
        self.return_val = return_val
        self.block = block

    def visit(self, writer):
        global scope

        writer.writeln(f'global {self.name.value}')
        writer.writeln(f'{self.name.value}:')
        writer.ident += 1

        writer.writeln(f'push rbp')
        writer.writeln(f'mov rbp, rsp')

        scope = scope.child()

        self.block.visit(writer)

        ret_stmt = Return(Constant(Token('INT', 0)))
        ret_stmt.visit(writer)

        scope = scope.parent

class Statement(BaseBox):
    pass

class Expression(BaseBox):
    pass

class Return(Statement):
    def __init__(self, expr):
        self.expr = expr

    def visit(self, writer):
        self.expr.visit(writer)

        writer.writeln(f'mov rsp, rbp')
        writer.writeln(f'pop rbp')

        writer.writeln(f'ret')

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
    def visit(self, writer):
        self.expr.visit(writer)
        writer.writeln('neg rax')

class Complement(Unary): # ~
    def visit(self, writer):
        self.expr.visit(writer)
        writer.writeln('not rax')

class LogicalNegation(Unary): # !
    def visit(self, writer):
        self.expr.visit(writer)
        writer.writeln('cmp rax, 0')
        writer.writeln('mov rax, 0')
        writer.writeln('sete al')


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

        else:
            raise Exception(f'Invalid binary operator: {operator}')


class Or(Binary):
    def visit(self, writer):
        jmp_lbl, end_lbl = label_generator.generate_both('or')

        self.left.visit(writer)
        writer.writeln('cmp rax, 0')
        writer.writeln(f'je {jmp_lbl}')
        writer.writeln('mov rax, 1')
        writer.writeln(f'jmp {end_lbl}')

        writer.writeln(jmp_lbl+':', ident_inc=-1)
        self.right.visit(writer)
        writer.writeln('cmp rax, 0')
        writer.writeln('mov rax, 0')
        writer.writeln(f'setne al')

        writer.writeln(end_lbl+':', ident_inc=-1)

class And(Binary):
    def visit(self, writer):
        jmp_lbl, end_lbl = label_generator.generate_both('and')

        self.left.visit(writer)
        writer.writeln('cmp rax, 0')
        writer.writeln(f'jne {jmp_lbl}')
        writer.writeln(f'jmp {end_lbl}')

        writer.writeln(jmp_lbl+':', ident_inc=-1)
        self.right.visit(writer)
        writer.writeln('cmp rax, 0')
        writer.writeln('mov rax, 0')
        writer.writeln(f'setne al')

        writer.writeln(end_lbl+':', ident_inc=-1)
class Equal(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('cmp rcx, rax')
        writer.writeln('mov rax, 0')
        writer.writeln('sete al')

class GreaterThan(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('cmp rcx, rax')
        writer.writeln('mov rax, 0')
        writer.writeln('setg al')
class LessThan(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('cmp rcx, rax')
        writer.writeln('mov rax, 0')
        writer.writeln('setl al')

class Addition(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('add rax, rcx')

class Subtraction(Binary):
    def visit(self, writer):
        self.right.visit(writer)
        writer.writeln('push rax')
        self.left.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('sub rax, rcx')

class Multiplication(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('imul rax, rcx')

class Exponent(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('call exponent')

class Division(Binary):
    def visit(self, writer):
        self.right.visit(writer)
        writer.writeln('push rax')
        self.left.visit(writer)
        writer.writeln('pop rcx')
        writer.writeln('cdq')

        writer.writeln('idiv rcx')

class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def visit(self, writer):
        offset = var_map[self.name.value]

        writer.writeln(f'mov rax, [rbp+{offset}]')

class Constant(Expression):
    def __init__(self, value):
        self.value = value

    def visit(self, writer):
        writer.writeln(f'mov rax, {self.value.value}')

    def size(self):
        return 8

class Declaration(Expression):
    def __init__(self, name, type, initialiser=None):
        self.name = name
        self.type = type
        self.initialiser = initialiser

    def visit(self, writer):
        global stack_index, var_map

        if self.initialiser:
            self.initialiser.visit(writer)

        size = sizeof(self.type.value)

        offset = stack_index

        writer.writeln('push rax', 'push variable {} of size {} onto stack'.format(self.name.value, size))

        var_map[self.name.value] = offset

        stack_index -= size

class Assignment(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def visit(self, writer):
        global var_map

        offset = var_map.get(self.name)

        writer.writeln(f'mov [rbp+{offset}], rax')


class If(Statement):
    def __init__(self, expr, true_stmt, false_stmt=None):
        self.expr = expr
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt

    def visit(self, writer):
        self.expr.visit(writer)

        start, end = label_generator.generate_both('if')

        writer.writeln('cmp rax, 0')
        writer.writeln('je {}'.format(start), 'Jump to 2nd stmt if expr is false')
        self.true_stmt.visit(writer)
        writer.writeln('jmp {}'.format(end), 'Jump to end after setting rax to 1st stmr')

        writer.writeln('{}:'.format(start), ident_inc=-1)
        self.false_stmt.visit(writer)

        writer.writeln('{}:'.format(end), ident_inc=-1)


class Ternary(Expression):
    def __init__(self, expr, true_expr, false_expr=None):
        self.expr = expr
        self.true_expr = true_expr
        self.false_expr = false_expr

    def visit(self, writer):
        self.expr.visit(writer)

        start, end = label_generator.generate_both('ternary')

        writer.writeln('cmp rax, 0')
        writer.writeln('je {}'.format(start), 'Jump to 2nd expr if expr is false')
        self.true_expr.visit(writer)
        writer.writeln('jmp {}'.format(end), 'Jump to end after setting rax to 1st expr')

        writer.writeln('{}:'.format(start), ident_inc=-1)
        self.false_expr.visit(writer)

        writer.writeln('{}:'.format(end), ident_inc=-1)


class Block(Statement):
    def __init__(self, statements):
        if type(statements) == list:
            self.statements = statements
        else:
            self.statements = [statements]

    def visit(self, writer):
        for stmt in self.statements:
            stmt.visit(writer)