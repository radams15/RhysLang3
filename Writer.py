class Writer:
    def __init__(self, stream):
        self.ident = 0
        self.ident_char = '\t'

        self.stream = stream

    def write(self, data):
        print(data, end='', file=self.stream)

    def writeln(self, data, comment='', ident_inc=0):
        print((self.ident_char*(self.ident+ident_inc)) + data + ('\t; {}'.format(comment) if comment else ''), file=self.stream)