class VMWriter:
    def __init__(self, op_fname):
        self.fp = open(op_fname, 'w')
        self.vm_code = ""

    def write(self, line):
        self.fp.write(line)
        self.fp.write('\n\n')

    def write_push(self, segment, index):
        if segment == 'field':
            segment = 'this'

        self.write('push {0} {1}'.format(segment, index))

    def write_pop(self, segment, index):
        if segment == 'field':
            segment = 'this'

        self.write('pop {0} {1}'.format(segment, index))

    def write_arithmetic(self, command):
        if command == '+':
            self.write('add')

        elif command == '-':
            self.write('sub')

        elif command == '=':
            self.write('eq')

        elif command == '>':
            self.write('gt')

        elif command == '<':
            self.write('lt')

        elif command == '&':
            self.write('and')

        elif command == '|':
            self.write('or')

        elif command == '~':
            print(1)
            self.write('not')

        elif command == '*':
            self.write_call('Math.multiply', 2)

        elif command == '/':
            self.write_call('Math.divide', 2)

        else:
            self.write('neg')

    def write_label(self, label):
        self.write('label {0}'.format(label))

    def write_go_to(self, label):
        self.write('goto {0}'.format(label))

    def write_if(self, label):
        self.write('if-goto {0}'.format(label))

    def write_call(self, name, nargs):
        if not nargs:
            nargs = 0

        self.write('call {0} {1}'.format(name, nargs))

    def write_func(self, name, nlocals):
        self.write('function {0} {1}'.format(name, nlocals))

    def write_return(self):
        self.write('return')

    def close(self):
        self.fp.close()
