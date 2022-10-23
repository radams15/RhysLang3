import os

from Lexer import lexer
from Parser import parser
from Writer import Writer

if __name__ == '__main__':
    file = 'test.rl'

    linked_libs = 'c'

    with open(file, 'r') as f:
        data = f.read()

    tokens = lexer.lex(data)

    program = parser.parse(tokens)

    out_file = 'out.nasm'

    writer = Writer(out_file)

    program.visit(writer)

    writer.close()

    print('\n')

    with open(out_file, 'r') as f:
        print(f.read())

    cmd = 'nasm -felf64 {} -o out.o && gcc {} out.o lib.c -o out'.format(out_file, ' '.join(["-l"+x for x in linked_libs]))
    print(cmd)
    os.system(cmd)