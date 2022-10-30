import re

def unicode_deescape(inp):
    sects = re.split(r'\\(\w)', inp)

    data = []
    for x in sects:
        if not x:
            continue
        elif x == 'n':
            data.append(ord('\n'))
        elif x == 't':
            data.append(ord('\t'))
        else:
            data.append(f'"{x}"')

    return data


def next_power_of_2(x):
    return 2 if x <= 2 else 2**(x - 1).bit_length()

def method_hash(struct_name, method_name):
    return f'{struct_name}___{method_name}'

def method_unhash(hashed_name):
    return hashed_name.split('___')

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
    def __init__(self, index, type):
        self.index = index
        self.type = type

class GlobalLocation:
    def __init__(self, name, type):
        self.name = name
        self.type = type

class StaticItem:
    def __init__(self, value):
        self.value = value

class Scope:
    def __init__(self, parent=None, index=0):
        self.values = dict()
        self.parent = parent

        self.stack_index = -8

        self.index = index

    def child(self):
        return Scope(self)

    def _set(self, name, value):
        #print(f'Set {name} = {value}')
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
        pass

    def generate(self):
        pass