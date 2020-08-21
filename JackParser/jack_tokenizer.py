import os


class JackTokenizer:
    """
                    Command Type Table
        Token:                      Returned Constant
        Keyword:                    0
        Symbol:                     1
        Integer:                    2
        String:                     3
        Identifier:                 4
    """
    keywords = ['class', 'constructor', 'function', 'method', 'field', 'static',
                'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
                'this', 'let', 'do', 'if', 'else', 'while', 'return']

    symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
               '&', '|', '<', '>', '=', '~'}

    def __init__(self, file_path):
        self.file_name = os.path.basename(file_path)[:-3]
        self.fp = open(file_path, 'r')
        self.current_token = None

    def get_curr_filename(self):
        return self.file_name

    def has_more_tokens(self):
        pos = self.fp.tell()
        does_it = bool(self.fp.read(1))
        self.fp.seek(pos)

        return does_it

    def advance(self):
        token = ''
        while True:
            if not self.has_more_tokens():
                break

            pos = self.fp.tell()
            c = self.fp.read(1)

            # If seen a /
            if c == '/':
                pos2 = self.fp.tell()
                next_token = self.fp.read(1)

                # If next char is /, ignore till end of line
                if next_token == '/':
                    while c != '\n':
                        c = self.fp.read(1)

                    continue

                # Else if next char is #, ignore till */
                elif next_token == '*':
                    while True:
                        c = self.fp.read(1)
                        if c == '*' and self.fp.read(1) == '/':
                            break
                    continue

                # Else it is division symbol, reposition to next operand
                else:
                    self.fp.seek(pos2)

            if c == "\"":
                token = ""
                while True:
                    c = self.fp.read(1)
                    if c == "\"":
                        break
                    token += c

                self.current_token = token
                break
            
            # If seen a space or next line char
            if c == ' ' or c == '\n':

                # If token size > 0, assign token
                if len(token.strip()) > 0:
                    self.current_token = token.strip()
                    break

                # Else if token size is 0, and character is \n
                elif c == '\n':

                    # If has more token continue
                    if self.has_more_tokens():
                        continue

                    # Probably end of file
                    break

                # If consume character is space, look for next token in line
                else:
                    continue

            # If symbol encountered, left operand is token
            if c in self.symbols:
                self.current_token = token.strip()

                # If no left operand, token is symbol
                if len(token.strip()) == 0:
                    self.current_token = c

                # Else reposition for next token
                else:
                    self.fp.seek(pos)
                break

            token += c

    def token_type(self, provided=None):
        """ Refer token type table """

        if provided:
            token = provided
        else:
            token = self.current_token

        if token in self.keywords:
            return 0

        elif token in self.symbols:
            return 1

        elif token.isdigit():
            return 2

        elif token.isidentifier():
            return 4

        else:
            return 3

    def token(self):
        return self.current_token
    
    def close(self):
        self.fp.close()

