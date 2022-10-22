from rply import LexerGenerator

lg = LexerGenerator()

lg.add('FLOAT', r'\d+\.\d+')
lg.add('INT', r'\d+')

lg.add('AND', r'and')
lg.add('OR', r'or')
lg.add('EQUAL', r'==')
lg.add('NOT_EQUAL', r'!=')


lg.add('SINGLE_ARROW', r'->')
lg.add('DOUBLE_ARROW', r'=>')

lg.add('PLUS', r'\+')
lg.add('MINUS', r'\-')
lg.add('TILDE', r'\~')
lg.add('EXCLAMATION', r'\!')
lg.add('MULTIPLY', r'\*')
lg.add('DIVIDE', r'/')
lg.add('LESS_THAN_EQUAL', r'<=')
lg.add('GREATER_THAN_EQUAL', r'>=')
lg.add('LESS_THAN', r'<')
lg.add('GREATER_THAN', r'>')
lg.add('ASSIGN', r'=')

lg.add('SEMICOLON', r';')
lg.add('COLON', r':')

lg.add('FN', r'fn')
lg.add('RETURN', r'return')
lg.add('VAR', r'var')

lg.add('PAREN_OPEN', r'\(')
lg.add('PAREN_CLOSE', r'\)')
lg.add('BRACE_OPEN', r'\{')
lg.add('BRACE_CLOSE', r'\}')
lg.add('BRACKET_OPEN', r'\[')
lg.add('BRACKET_CLOSE', r'\]')

lg.add('IDENTIFIER', r'[a-zA-Z][a-zA-Z0-9_]*')

lg.ignore(r'\s+')

lexer = lg.build()