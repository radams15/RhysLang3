from Visitor import Visitor
from Ast import *

ENTRYPOINT = '''\
global _start

_start:
    call main
    mov rdi, rax
    mov rax, 60
    syscall
'''

SYSCALL_TABLE = {
    'read': 0,
    'write': 1,
    'open': 2,
    'close': 3,

    'exit': 60,

    'gettimeofday': 96,
}


class x86_64GlobalGenerator(GlobalGenerator):
    def make(self, size, *data, type='global', name=None):
        if not name:
            name = self._get_name(type)

        if size not in ('db', 'dw', 'dd', 'dq'):
            raise Exception('Error: unknown global size: {}'.format(size))

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


def write_debug(writer, token):
    pass
    # self.writer.writeln(f'%line {token.source_pos.lineno}+0 test.rl')



class x86Visitor(Visitor):
    ARG_REGISTERS = ('rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9')
    PRIMITIVES = ('int', 'char', 'str', 'ptr')
    defined_structs = dict()
    label_generator = LabelGenerator()

    def __init__(self, writer, write_start):
        super().__init__(writer, write_start)

        self.undefined_functions = []
        self.defined_functions = []
        self.globals_gen = x86_64GlobalGenerator()
        self.scope = Scope()

    def sizeof(self, subj):
        if subj in self.PRIMITIVES:
            return 8

        if type(subj) == StructDef:
            return (
                sum(
                    [
                        self.sizeof(data_type)
                        for name, data_type in subj.members
                    ]
                )
            )

        if subj in self.defined_structs.keys():
            return 8  # Pointer
            # return self.defined_structs[type].size()

        else:
            raise Exception('Unknown type: {}'.format(subj))

    def reset_parser(self):
        self.undefined_functions = []
        self.defined_functions = []
        self.globals_gen = x86_64GlobalGenerator()
        self.label_generator = LabelGenerator()
        self.scope = Scope()

    def datasize(self, type):
        return {
            8: 'db',
            16: 'dw',
            32: 'dd',
            64: 'dq',
        }[self.sizeof(type)]


    def visit_program(self, program: Program):
        self.writer.writeln('section .text')

        for toplevel in program.toplevels:
            toplevel.visit(self)

        for undefined_function in set(self.undefined_functions):
            self.writer.writeln('extern {}'.format(undefined_function))

        if self.write_start:
            self.writer.writeln(ENTRYPOINT)

        self.writer.writeln('section .data')

        self.writer.write(self.globals_gen.generate())

    def visit_struct_def(self, struct: StructDef):
        current_index = 0
        for name, type in struct.members:
            size = self.sizeof(type)
            struct.indexes[name] = current_index
            current_index += size

        self.defined_structs[struct.name] = struct
        self.scope.set(struct.name, StaticItem(struct))

        for m in struct.methods:
            m.name = method_hash(struct.name, m.name)
            m.arity += 1
            m.args = [('this', struct.name)] + m.args

            m.visit(self)

        for m in struct.static_methods:
            m.name = method_hash(struct.name, m.name)

            m.visit(self)

    def visit_function(self, func: Function):
        if not func.block:
            self.undefined_functions.append(func.name)
            return

        self.defined_functions.append(func)

        self.writer.writeln(f'global {func.name}')
        write_debug(self.writer, func.name)
        self.writer.writeln(f'{func.name}:')
        self.writer.ident += 1

        self.writer.writeln(f'push rbp')
        self.writer.writeln(f'mov rbp, rsp')

        self.scope = self.scope.child()

        for (arg_name, arg_type), register in zip(func.args, self.ARG_REGISTERS):
            size = self.sizeof(arg_type)

            offset = self.scope.stack_index

            self.writer.writeln(f'push {register}', 'Push argument {} onto stack at position {}'.format(arg_name, offset))

            self.scope.set(arg_name, StackLocation(offset, arg_type))

            self.scope.stack_index -= size

        func.block.visit(self)

        ret_stmt = Return(Constant(Token('INT', 0)))
        ret_stmt.visit(self)

        self.scope = self.scope.parent

        self.writer.writeln('\n')

        self.writer.ident -= 1

    def visit_return(self, ret: Return):
        ret.expr.visit(self)

        self.writer.writeln(f'mov rsp, rbp')
        self.writer.writeln(f'pop rbp')

        self.writer.writeln(f'ret')

    def visit_negation(self, unary: Negation):
        unary.expr.visit(self)
        self.writer.writeln('neg rax')

    def visit_complement(self, unary: Complement):
        unary.expr.visit(self)
        self.writer.writeln('not rax')

    def visit_logical_negation(self, unary: LogicalNegation):
        unary.expr.visit(self)
        self.writer.writeln('cmp rax, 0')
        self.writer.writeln('mov rax, 0')
        self.writer.writeln('sete al')

    def visit_bitwise_and(self, binary: BitwiseAnd):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('and rax, rcx')

    def visit_bitwise_or(self, binary: BitwiseOr):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('or rax, rcx')

    def visit_bitwise_xor(self, binary: BitwiseXor):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('xor rax, rcx')

    def visit_or(self, binary: Or):
        jmp_lbl, end_lbl = self.label_generator.generate_both('or')

        binary.left.visit(self)
        self.writer.writeln('cmp rax, 0')
        self.writer.writeln(f'je {jmp_lbl}')
        self.writer.writeln('mov rax, 1')
        self.writer.writeln(f'jmp {end_lbl}')

        self.writer.writeln(jmp_lbl + ':', ident_inc=-1)
        binary.right.visit(self)
        self.writer.writeln('cmp rax, 0')
        self.writer.writeln('mov rax, 0')
        self.writer.writeln(f'setne al')

        self.writer.writeln(end_lbl + ':', ident_inc=-1)

    def visit_and(self, binary: And):
        jmp_lbl, end_lbl = self.label_generator.generate_both('and')

        binary.left.visit(self)
        self.writer.writeln('cmp rax, 0')
        self.writer.writeln(f'jne {jmp_lbl}')
        self.writer.writeln(f'jmp {end_lbl}')

        self.writer.writeln(jmp_lbl + ':', ident_inc=-1)
        binary.right.visit(self)
        self.writer.writeln('cmp rax, 0')
        self.writer.writeln('mov rax, 0')
        self.writer.writeln(f'setne al')

        self.writer.writeln(end_lbl + ':', ident_inc=-1)

    def visit_equal(self, binary: Equal):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('cmp rcx, rax')
        self.writer.writeln('mov rax, 0')
        self.writer.writeln('sete al')

    def visit_greater_than(self, binary: GreaterThan):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('cmp rcx, rax')
        self.writer.writeln('mov rax, 0')
        self.writer.writeln('setg al')

    def visit_less_than(self, binary: LessThan):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('cmp rcx, rax')
        self.writer.writeln('mov rax, 0')
        self.writer.writeln('setl al')

    def get_resultant_type(self, expr):
        expr_type = type(expr)

        if expr_type == Constant:
            return type(expr.value)
        elif expr_type == Variable:
            pos = self.scope.get(expr.name)
            return pos.type
        elif expr_type == FunctionCall:
            func = [x for x in self.defined_functions if x.name == expr.name][0]
            return func.return_val


    def visit_addition(self, binary: Addition):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('add rax, rcx')

    def visit_subtraction(self, binary: Subtraction):
        binary.right.visit(self)
        self.writer.writeln('push rax')
        binary.left.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('sub rax, rcx')

    def visit_multiplication(self, binary: Multiplication):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('imul rax, rcx')


    def visit_exponent(self, binary: Exponent):
        binary.left.visit(self)
        self.writer.writeln('push rax')
        binary.right.visit(self)
        self.writer.writeln('pop rcx')

        self.writer.writeln('call exponent')

    def visit_division(self, binary: Division):
        binary.right.visit(self)
        self.writer.writeln('push rax')
        binary.left.visit(self)
        self.writer.writeln('pop rcx')
        self.writer.writeln('cdq')

        self.writer.writeln('idiv rcx')

    def visit_variable(self, var: Variable):
        obj = self.scope.get(var.name)

        if type(obj) == StackLocation:
            self.writer.writeln(f'mov rax, [rbp+{obj.index}]')
        elif type(obj) == GlobalLocation:
            self.writer.writeln(f'mov rax, {obj.name}')
        else:
            raise Exception(f'Unknown variable type: {type(obj)}')

    def visit_constant(self, const: Constant):
        self.writer.writeln(f'mov rax, {const.value}')

    def visit_global(self, globl: Global):
        value = globl.value.value

        if globl.type.value == 'str':
            value = unicode_deescape(value[1:-1])
            value = value + [0]
        else:
            value = [value]

        self.globals_gen.make(self.datasize(globl.type.value), *value, name=globl.name.value)
        self.scope.set(globl.name.value, GlobalLocation(globl.name.value, globl.type))

    def visit_string(self, string: String):
        string.id = self.globals_gen.make('dw', *string.data, 0, type='string')

        self.writer.writeln(f'mov rax, {string.id}')

    def visit_declaration(self, decl: Declaration):
        if decl.initialiser:
            decl.initialiser.visit(self)

        write_debug(self.writer, decl.name)

        size = self.sizeof(decl.type)

        offset = self.scope.stack_index

        self.writer.writeln('push rax', 'push variable {} of size {} onto stack'.format(decl.name, size))

        self.scope.set(decl.name, StackLocation(offset, decl.type))

        self.scope.stack_index -= size

    def visit_assignment(self, assign: Assignment):
        assign.expr.visit(self)

        offset = self.scope.get(assign.name).index

        self.writer.writeln(f'mov [rbp+{offset}], rax', 'Assign {} to rax'.format(assign.name))


    def visit_if(self, stmt: If):
        stmt.expr.visit(self)

        start, end = self.label_generator.generate_both('if')

        self.writer.writeln('cmp rax, 0')
        self.writer.writeln('je {}'.format(start), 'Jump to 2nd stmt if expr is false')
        stmt.true_stmt.visit(self)
        self.writer.writeln('jmp {}'.format(end), 'Jump to end after setting rax to 1st stmr')

        self.writer.writeln('{}:'.format(start), ident_inc=-1)

        if stmt.false_stmt:
            stmt.false_stmt.visit(self)

        self.writer.writeln('{}:'.format(end), ident_inc=-1)

    def visit_ternary(self, stmt: Ternary):
        stmt.expr.visit(self)

        start, end = self.label_generator.generate_both('ternary')

        self.writer.writeln('cmp rax, 0')
        self.writer.writeln('je {}'.format(start), 'Jump to 2nd expr if expr is false')
        stmt.true_expr.visit(self)
        self.writer.writeln('jmp {}'.format(end), 'Jump to end after setting rax to 1st expr')

        self.writer.writeln('{}:'.format(start), ident_inc=-1)
        stmt.false_expr.visit(self)

        self.writer.writeln('{}:'.format(end), ident_inc=-1)

    def visit_loop(self, loop: Loop):
        start, end = self.label_generator.generate_both('loop')

        self.writer.writeln('{}:'.format(start), ident_inc=-1)

        loop.expr.visit(self)
        self.writer.writeln('cmp rax, 0')
        self.writer.writeln('je {}'.format(end), 'Jump to end if expr is false')

        loop.body.visit(self)

        self.writer.writeln('jmp {}'.format(start), 'Jump to start again as expr was true last run')

        self.writer.writeln('{}:'.format(end), ident_inc=-1)

    def visit_syscall(self, syscall: Syscall):
        if syscall.name not in SYSCALL_TABLE:
            raise Exception(f'No known syscall: {syscall.name}')

        id = SYSCALL_TABLE[syscall.name]

        for arg in syscall.args:
            arg.visit(self)
            self.writer.writeln('push rax', 'Push arg onto stack to allow using registers multiple times.')

        for register in reversed(self.ARG_REGISTERS[:len(syscall.args)]):
            self.writer.writeln('pop {}'.format(register), 'Pop arg from stack to put in syscall register.')

        self.writer.writeln('mov rax, {}'.format(id), 'Move syscall number {} into rax.'.format(id))

        self.writer.writeln('syscall')

    def visit_function_call(self, func_call: FunctionCall):
        if func_call.name == 'sizeof':
            if func_call.args[0].name in self.PRIMITIVES:
                obj_type = func_call.args[0].name
                obj_name = obj_type
            else:
                obj_type = self.scope.get(func_call.args[0].name).value
                obj_name = obj_type.name

            size = self.sizeof(obj_type)
            self.writer.writeln(f'mov rax, {size}', f'{obj_name} size is {size}')
        else:
            if func_call.name not in [x.name for x in self.defined_functions]:
                self.undefined_functions.append(func_call.name)

            for arg in func_call.args:
                arg.visit(self)
                self.writer.writeln('push rax', 'Push arg onto stack to allow using registers multiple times.')

            for register in reversed(self.ARG_REGISTERS[:len(func_call.args)]):
                self.writer.writeln('pop {}'.format(register), 'Pop arg from stack to put in function call register.')

            self.writer.writeln('call {}'.format(func_call.name))

    def visit_struct_get(self, struct_get: StructGet):
        struct = self.scope.get(struct_get.struct_name)

        struct_type: StructDef = self.defined_structs[struct.type]
        struct_index = struct_type.indexes[struct_get.item_name]

        self.writer.writeln(f'mov rax, [rbp+{struct.index}]', f'Move {struct_type.name} to rax')
        self.writer.writeln(f'mov rax, [rax+{struct_index}]', f'Move member {struct_get.item_name} from rax+{struct_index} to rax')


    def visit_struct_set(self, struct_set: StructSet):
        struct = self.scope.get(struct_set.member.struct_name)

        struct_type: StructDef = self.defined_structs[struct.type]
        struct_index = struct_type.indexes[struct_set.member.item_name]

        struct_set.expr.visit(self)  # Move value into rax
        self.writer.writeln(f'push rax', f'Push target value to stack')
        self.writer.writeln(f'pop rdx', f'Pop target value into rdx')

        self.writer.writeln(f'mov rax, [rbp+{struct.index}]', f'Move {struct_type.name} from stack into rax')
        self.writer.writeln(f'mov [rax+{struct_index}], rdx',
                       f'Move target value into {struct_set.member.item_name} at position {struct_index}')
        self.writer.writeln(f'mov [rbp+{struct.index}], rax', f'Move {struct_type.name} back onto stack')

    def visit_struct_method_call(self, struct_method_call: StructMethodCall):
        if struct_method_call.member in self.defined_structs:
            struct_type = struct_method_call.member

            method_fullname = method_hash(struct_type, struct_method_call.function.name)
        else:
            struct = self.scope.get(struct_method_call.member)

            struct_type: StructDef = self.defined_structs[struct.type]

            method_fullname = method_hash(struct_type.name, struct_method_call.function.name)

            struct_method_call.function.args = [
                                     Variable(
                                         Token(
                                             'VARIABLE',
                                             struct_method_call.member
                                         )
                                     )
                                 ] + struct_method_call.function.args


        struct_method_call.function.name = method_fullname

        if method_fullname not in [x.name for x in self.defined_functions]:
            self.undefined_functions.append(method_fullname)

        struct_method_call.function.visit(self)
