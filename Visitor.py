from Ast import *

class Visitor:
    def __init__(self, writer, write_start):
        self.writer = writer
        self.write_start = write_start

    def sizeof(self, item): pass

    def visit_program(self, program: Program): pass
    def visit_struct_def(self, struct: StructDef): pass
    def visit_function(self, func: Function): pass
    def visit_return(self, ret: Return): pass

    def visit_negation(self, unary: Negation): pass
    def visit_complement(self, unary: Complement): pass
    def visit_logical_negation(self, unary: LogicalNegation): pass


    def visit_bitwise_and(self, binary: BitwiseAnd): pass
    def visit_bitwise_or(self, binary: BitwiseOr): pass
    def visit_bitwise_xor(self, binary: BitwiseXor): pass
    def visit_or(self, binary: Or): pass
    def visit_and(self, binary: And): pass
    def visit_equal(self, binary: Equal): pass
    def visit_greater_than(self, binary: GreaterThan): pass
    def visit_less_than(self, binary: LessThan): pass
    def visit_addition(self, binary: Addition): pass
    def visit_subtraction(self, binary: Subtraction): pass
    def visit_multiplication(self, binary: Multiplication): pass
    def visit_exponent(self, binary: Exponent): pass
    def visit_division(self, binary: Division): pass


    def visit_variable(self, var: Variable): pass
    def visit_constant(self, const: Constant): pass
    def visit_global(self, globl: Global): pass
    def visit_string(self, string: String): pass
    def visit_declaration(self, decl: Declaration): pass
    def visit_assignment(self, assign: Assignment): pass
    def visit_if(self, stmt: If): pass
    def visit_ternary(self, stmt: Ternary): pass
    def visit_loop(self, loop: Loop): pass
    def visit_syscall(self, syscall: Syscall): pass
    def visit_function_call(self, func_call: FunctionCall): pass
    def visit_struct_get(self, struct_get: StructGet): pass
    def visit_struct_set(self, struct_set: StructSet): pass
    def visit_struct_method_call(self, struct_method_cal: StructMethodCall): pass
