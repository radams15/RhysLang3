from rply.token import BaseBox

class Program(BaseBox):
    def __init__(self, function):
        self.function = function

    def visit(self, writer):
        self.function.visit(writer)

        writer.ident -= 1

        writer.writeln('')
        writer.writeln('global _start')
        writer.writeln('_start:') # Make start function to call main then exit normally
        writer.ident += 1
        writer.writeln('call main')
        writer.writeln('')
        writer.writeln('mov rdi, rax') # Move main return value into exit syscall arg
        writer.writeln('mov rax, 60') # Move exit syscall code into rax
        writer.writeln('syscall')

class Function(BaseBox):
    def __init__(self, name, return_val, statement):
        self.name = name
        self.return_val = return_val
        self.statement = statement

    def visit(self, writer):
        writer.writeln(f'global {self.name.value}')
        writer.writeln(f'{self.name.value}:')
        writer.ident += 1

        self.statement.visit(writer)


class Statement(BaseBox):
    pass

class Expression(BaseBox):
    pass

class Return(Statement):
    def __init__(self, expr):
        self.expr = expr

    def visit(self, writer):
        self.expr.visit(writer)
        writer.writeln('ret')

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

        elif operator.name == 'DIVIDE':
            return Division(operator, left, right)

        else:
            raise Exception(f'Invalid binary operator: {operator}')

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

class Division(Binary):
    def visit(self, writer):
        self.right.visit(writer)
        writer.writeln('push rax')
        self.left.visit(writer)
        writer.writeln('pop rcx')
        writer.writeln('cdq')

        writer.writeln('idiv rcx')


class Logical(Expression):
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

        elif operator.name == 'DIVIDE':
            return Division(operator, left, right)

        else:
            raise Exception(f'Invalid binary operator: {operator}')

class Constant(Expression):
    def __init__(self, value):
        self.value = value

    def visit(self, writer):
        writer.writeln(f'mov rax, {self.value.value}')