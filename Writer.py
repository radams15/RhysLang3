class Writer:
    def __init__(self, file_name):
        self.ident = 0
        self.ident_char = '\t'

        self.file = open(file_name, 'w')

    def write(self, data):
        print(data, end='', file=self.file)

    def writeln(self, data, ident_inc=0):
        print((self.ident_char*(self.ident+ident_inc)) + data, file=self.file)

    def close(self):
        self.file.close()