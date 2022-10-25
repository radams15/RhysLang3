import io
import os
from glob import glob

import argparse

from Lexer import lexer
from Parser import parser
from Writer import Writer

LIB_DIR = 'lib'
EXT_DIR = 'ext'
FILE_EXT = '.rl'

LIBS = [x.replace(LIB_DIR+os.sep, '').replace(FILE_EXT, '') for x in glob(f'{LIB_DIR}/*{FILE_EXT}')]
EXT_FILES = list(glob(f'{EXT_DIR}/*.c'))

LINK_LIBS = ['c']

def compile_lib(name):
    path = os.path.join(LIB_DIR, name) + FILE_EXT

    with open(path, 'r') as f:
        tokens = lexer.lex(f.read())

    program = parser.parse(tokens)

    with io.StringIO() as stream:
        writer = Writer(stream)

        program.visit(writer)

        asm = stream.getvalue()

    return asm


def compile_libs():
    libs = {
        x : compile_lib(x)
        for x in LIBS
    }

    return libs

if __name__ == '__main__':
    file = 'test.rl'

    linked_libs = ' '.join(["-l"+x for x in LINK_LIBS])

    libs = compile_libs()

    with open(file, 'r') as f:
        data = f.read()

    tokens = lexer.lex(data)

    program = parser.parse(tokens)

    out_file = 'out.nasm'

    with open(out_file, 'w') as f:
        writer = Writer(f)

        program.visit(writer)

        for lib, asm in libs.items():
            f.write('\n\n')
            f.write(asm)

    print('\n')

    with open(out_file, 'r') as f:
        print(f.read())

    cmd = 'nasm -felf64 {} -o out.o && gcc {} out.o {} -o out'.format(out_file, linked_libs, ' '.join(EXT_FILES))

    print(cmd)
    os.system(cmd)