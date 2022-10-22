import os

from Lexer import lexer
from Parser import parser
from Writer import Writer

if __name__ == '__main__':
    file = 'test.rl'

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

    os.system(f'nasm -felf64 {out_file} -o out.o && ld out.o -o out')