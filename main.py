#!/usr/bin/env python3

import io
import os
from glob import glob

import argparse

from Lexer import lexer
from Parser import parser
from x86Visitor import x86Visitor
from Writer import Writer

LIB_DIR = 'lib'
EXT_DIR = 'ext'
FILE_EXT = '.rl'

LIBS = [x.replace(LIB_DIR+os.sep, '').replace(FILE_EXT, '') for x in glob(f'{LIB_DIR}/*{FILE_EXT}')]
EXT_FILES = list(glob(f'{EXT_DIR}/*.c'))

LINK_LIBS = [
#   'c'
]

def compile_lib(name):
    path = os.path.join(LIB_DIR, name) + FILE_EXT

    with open(path, 'r') as f:
        tokens = lexer.lex(f.read())

    program = parser.parse(tokens)

    with io.StringIO() as stream:
        writer = Writer(stream)
        visitor = x86Visitor(writer, False)

        program.visit(visitor)

        asm = stream.getvalue()

    return asm


def compile_libs():
    libs = {
        x : compile_lib(x)
        for x in LIBS
    }

    return libs

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('file', type=str, help='File to compile')
    arg_parser.add_argument('-e', '--noextensions', action='store_true', help='Compile without extensions')
    arg_parser.add_argument('-s', '--nostdlib', action='store_true', help='Compile without standard library')
    arg_parser.add_argument('-g', '--debug', action='store_true', help='Compile with DWARF support')
    arg_parser.add_argument('-d', '--dump', action='store_true', help='Dump assembly source to stdout.')
    arg_parser.add_argument('-o', '--output', type=str, default='a.out', help='File to write final output to.')

    args = arg_parser.parse_args()

    if not args.noextensions:
        linked_libs = ' '.join(["-l"+x for x in LINK_LIBS])
    else:
        linked_libs = ''

    if not args.nostdlib:
        libs = compile_libs()
    else:
        libs = {}



    ### Create build directories

    build_dir = 'build/'
    lib_build_dir = os.path.join(build_dir, 'lib')
    ext_build_dir = os.path.join(build_dir, 'ext')

    if not os.path.exists(lib_build_dir): os.makedirs(lib_build_dir)
    if not os.path.exists(ext_build_dir): os.makedirs(ext_build_dir)

    ### Compile source file.

    with open(args.file, 'r') as f:
        data = f.read()

    tokens = lexer.lex(data)

    program = parser.parse(tokens)

    out_file = f'{build_dir}/out.nasm'

    with open(out_file, 'w') as f:
        writer = Writer(f)
        visitor = x86Visitor(writer, args.noextensions)

        program.visit(visitor)

    if args.dump:
        print('\n')

        with open(out_file, 'r') as f:
            print(f.read())

    if args.debug:
        debug_args = '-g -F stabs'
    else:
        debug_args = ''


    if not args.nostdlib:
        ### Assemble stdlib

        all_asm = '\n\n'.join([asm for name, asm in libs.items()])

        asm_file = os.path.join(lib_build_dir, 'librl.nasm')
        with open(asm_file, 'w') as f:
            f.write(all_asm)

        librl_object = f'{lib_build_dir}/librl.o'

        cmd = f'nasm -Fstabs -felf64 {debug_args} {asm_file} -o {librl_object}'
        print(cmd)
        os.system(cmd)
    else:
        librl_object = ''

    if not args.noextensions:
        ### Compile extensions

        ext_objects = []
        for ext_file in EXT_FILES:
            obj_file = os.path.basename(ext_file).replace('.c', '.o')
            obj_path = os.path.join(ext_build_dir, obj_file)

            cmd = f'gcc -c {ext_file} -o {obj_path}'
            print(cmd)
            os.system(cmd)

            ext_objects.append(obj_path)
    else:
        ext_objects = []

    ### Assemble source file

    source_object = os.path.join(build_dir, 'out.o')

    cmd = 'nasm -Fstabs -felf64 {} {} -o {}'.format(debug_args, out_file, source_object)
    print(cmd)
    os.system(cmd)

    ### Link source files

    if not args.noextensions:
        ld = 'gcc'
    else:
        ld = 'ld'

    cmd = '{} {} {} {} -o {}'.format(ld, ' '.join(ext_objects), librl_object, source_object, args.output)
    print(cmd)
    os.system(cmd)
