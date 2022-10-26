import re

from rply.token import BaseBox, Token

ENTRYPOINT = '''\
global _start

_start:
    call main
    mov rdi, rbp
    mov rax, 60
    syscall
'''

class LabelGenerator:
    def __init__(self, start=0):
        self.counter = start

    def generate(self, type='label'):
        self.counter += 1
        return '{}_{}'.format(type, self.counter, '_end')

    def generate_both(self, type='label'):
        start = self.generate(type)
        return (start, start+'_end')

class StackLocation:
    def __init__(self, index):
        self.index = index

class GlobalLocation:
    def __init__(self, name):
        self.name = name

class Scope:
    def __init__(self, parent=None, index=0):
        self.values = dict()
        self.parent = parent

        self.stack_index = -8

        self.index = index

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

class GlobalGenerator:
    def __init__(self):
        self.globals = dict()
        self.counter = 0

    def _get_name(self, type):
        self.counter += 1
        return '{}_{}'.format(type, self.counter)

    def make(self, size, *data, type='global', name=None):
        if not name:
            name = self._get_name(type)

        if size not in ('db', 'dw', 'dd', 'dq'):
            print('Error: unknown global size: {}'.format(size))
            size = 'dq'


        normalised_data = []
        for x in data:
            if isinstance(x, Token):
                x = x.value

            normalised_data.append(x)

        self.globals[name] = (size, normalised_data)

        return name

    def generate(self):
        out = ''

        for name, (size, data) in self.globals.items():
            out += '\t{}: {} {}\n'.format(name, size, ', '.join([str(x) for x in data]))

        return out


scope = None
globals_gen = None
label_generator = None
undefined_functions = None
defined_functions = None

int_size = 8

ARG_REGISTERS = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']

def sizeof(type):
    if type in ('int', 'char', 'str'):
        return 8

    else:
        raise Exception('Unknown type: {}'.format(type))

def datasize(type):
    return {
        8: 'db',
        16: 'dw',
        32: 'dd',
        64: 'dq',
    }[sizeof(type)]

def write_debug(writer, token):
    writer.writeln(f'%line {token.source_pos.lineno}+0 test.rl')

def init_parser(def_start=True):
    global undefined_functions, defined_functions, globals_gen, label_generator, scope, define_start

    undefined_functions = []
    defined_functions = []
    globals_gen = GlobalGenerator()
    label_generator = LabelGenerator()
    scope = Scope()
    define_start = def_start


class Program(BaseBox):
    def __init__(self, functions, globals):
        if type(functions) == list:
            self.functions = functions
        else:
            self.functions = [functions]

        if type(globals) == list:
            self.globals = globals
        else:
            self.globals = [globals]

    def visit(self, writer):
        global undefined_functions, globals_gen, define_start

        for global_var in self.globals:
            global_var.visit(writer)

        writer.writeln('section .text')

        for function in self.functions:
            function.visit(writer)

        for undefined_function in undefined_functions:
            writer.writeln('extern {}'.format(undefined_function))

        if define_start:
            writer.writeln(ENTRYPOINT)

        writer.writeln('section .data')

        writer.write(globals_gen.generate())

class Function(BaseBox):
    def __init__(self, name, return_val, args, block=None):
        self.name = name
        self.return_val = return_val
        self.args = [(args[x],args[x+1]) for x in range(0, len(args), 2)]
        self.arity = len(args)
        self.block = block

    def visit(self, writer):
        global scope

        if not self.block:
            undefined_functions.append(self.name.value)
            return

        defined_functions.append(self.name.value)

        writer.writeln(f'global {self.name.value}')
        write_debug(writer, self.name)
        writer.writeln(f'{self.name.value}:')
        writer.ident += 1

        writer.writeln(f'push rbp')
        writer.writeln(f'mov rbp, rsp')

        scope = scope.child()

        for (arg_name, arg_type), register in zip(self.args, ARG_REGISTERS):
            size = sizeof(arg_type.value)

            offset = scope.stack_index

            writer.writeln(f'push {register}', 'Push argument {} onto stack at position {}'.format(arg_name.value, offset))

            scope.set(arg_name.value, StackLocation(offset))

            scope.stack_index -= size

        self.block.visit(writer)

        ret_stmt = Return(Constant(Token('INT', 0)))
        ret_stmt.visit(writer)

        scope = scope.parent

        writer.writeln('\n')

        writer.ident -= 1

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

        elif operator.name == 'PIPE':
            return BitwiseOr(operator, left, right)

        elif operator.name == 'XOR':
            return BitwiseAnd(operator, left, right)

        elif operator.name == 'XOR':
            return BitwiseXor(operator, left, right)

        else:
            raise Exception(f'Invalid binary operator: {operator}')

class BitwiseAnd(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('and rax, rcx')

class BitwiseXor(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('xor rax, rcx')

class BitwiseOr(Binary):
    def visit(self, writer):
        self.left.visit(writer)
        writer.writeln('push rax')
        self.right.visit(writer)
        writer.writeln('pop rcx')

        writer.writeln('or rax, rcx')

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
        obj = scope.get(self.name.value)

        if type(obj) == StackLocation:
            writer.writeln(f'mov rax, [rbp+{obj.index}]')
        elif type(obj) == GlobalLocation:
            writer.writeln(f'mov rax, {obj.name}')
        else:
            raise Exception(f'Unknown variable type: {type(obj)}')

class Constant(Expression):
    def __init__(self, value):
        if type(value) == Token:
            self.value = value.value
        else:
            self.value = value

    def visit(self, writer):
        writer.writeln(f'mov rax, {self.value}')

    def size(self):
        return 8

class Global(Expression):
    def __init__(self, name, type, value=None):
        self.name = name
        self.type = type
        self.value = value

    def visit(self, writer):
        value = self.value.value

        if self.type.value == 'str':
            value = "'"+value[1:-1]+"'"
            value = [value, 0]
        else:
            value = [value]

        globals_gen.make(datasize(self.type.value), *value, name=self.name.value)
        scope.set(self.name.value, GlobalLocation(self.name.value))

class Char(Constant):
    def __init__(self, data):
        data = ord(data.value[1:-1])

        super().__init__(data)


class String(Constant):
    def __init__(self, data):
        data = data.value[1:-1]

        sects = re.split(r'\\(\w)', data)

        data = []
        for x in sects:
            if not x: continue
            elif x == 'n': data.append(ord('\n'))
            elif x == 't': data.append(ord('\t'))
            else: data.append(f'"{x}"')

        id = globals_gen.make('dw', *data, 0, type='string')
        super().__init__(id)

    def visit(self, writer):
        writer.writeln(f'mov rax, {self.value}')

class Declaration(Expression):
    def __init__(self, name, type, initialiser=None):
        self.name = name
        self.type = type
        self.initialiser = initialiser

    def visit(self, writer):
        global scope

        if self.initialiser:
            self.initialiser.visit(writer)

        write_debug(writer, self.name)

        size = sizeof(self.type.value)

        offset = scope.stack_index

        writer.writeln('push rax', 'push variable {} of size {} onto stack'.format(self.name.value, size))

        scope.set(self.name.value, StackLocation(offset))

        scope.stack_index -= size

class Assignment(Expression):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def visit(self, writer):
        self.expr.visit(writer)

        offset = scope.get(self.name.value).index

        writer.writeln(f'mov [rbp+{offset}], rax', 'Assign {} to rax'.format(self.name.value))


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

        if self.false_stmt:
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

class Loop(Statement):
    def __init__(self, expr, body):
        self.expr = expr
        self.body = body

    def visit(self, writer):
        start, end = label_generator.generate_both('loop')

        writer.writeln('{}:'.format(start), ident_inc=-1)

        self.expr.visit(writer)
        writer.writeln('cmp rax, 0')
        writer.writeln('je {}'.format(end), 'Jump to end if expr is false')

        self.body.visit(writer)

        writer.writeln('jmp {}'.format(start), 'Jump to start again as expr was true last run')

        writer.writeln('{}:'.format(end), ident_inc=-1)

class Syscall(Statement):
    def __init__(self, id, args):
        self.id = id.value

        if type(args) == list:
            self.args = args
        else:
            self.args = [args]

    def visit(self, writer):
        for arg in self.args:
            arg.visit(writer)
            writer.writeln('push rax', 'Push arg onto stack to allow using registers multiple times.')

        for register in reversed(ARG_REGISTERS[:len(self.args)]):
            writer.writeln('pop {}'.format(register), 'Pop arg from stack to put in syscall register.')

        writer.writeln('mov rax, {}'.format(self.id), 'Move syscall number {} into rax.'.format(self.id))

        writer.writeln('syscall')


class FunctionCall(Statement):
    def __init__(self, name, args):
        self.name = name

        if type(args) == list:
            self.args = args
        else:
            self.args = [args]

    def visit(self, writer):
        global undefined_functions
        if self.name.value not in defined_functions:
            undefined_functions.append(self.name.value)

        for arg in self.args:
            arg.visit(writer)
            writer.writeln('push rax', 'Push arg onto stack to allow using registers multiple times.')

        for register in reversed(ARG_REGISTERS[:len(self.args)]):
            writer.writeln('pop {}'.format(register), 'Pop arg from stack to put in function call register.')

        writer.writeln('call {}'.format(self.name.value))