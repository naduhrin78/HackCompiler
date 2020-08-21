from JackParser.jack_tokenizer import JackTokenizer
from SymbolTable.symbol_table import SymbolTable
from VMWriter.vm_writer import VMWriter
from xml.dom import minidom

import xml.etree.cElementTree as ET


class CompilationEngine:

    def __init__(self, ip_fname, op_fname):
        self.fp = open(op_fname, 'w')

        self.parsed_code = ""

        self.tokenizer = JackTokenizer(ip_fname)

        self.root = None

        self.class_name = None

        self.class_table = SymbolTable()

        self.subroutine_table = SymbolTable()

        self.vm_writer = VMWriter(op_fname.split('.')[0]+'.vm')

        self.if_else_runner = 0

        self.while_runner = 0

    @staticmethod
    def prettify(elem):
        """Return a pretty-printed XML string for the Element.
        """

        rough_string = ET.tostring(elem, 'utf-8')

        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent="  ")

    def eat(self, token, root, handle_dict=None, id_dict=None, unconditional_eat=False):

        if handle_dict and not handle_dict[0]:
            self.error_handle(handle_dict[1])

        if token != self.tokenizer.token() and not unconditional_eat:
            self.error_handle("Mismatch: Expected {0}, found {1}.".format(token, self.tokenizer.token()))

        token_type = self.tokenizer.token_type(token)

        label_map = {0: 'keyword', 1: 'symbol', 2: 'integerConstant', 3: 'stringConstant', 4: 'identifier'}

        if id_dict:
            aux_root = ET.SubElement(root, 'identifier')

            id_dict['table'].define(token, id_dict['type'], id_dict['kind'])

            ET.SubElement(aux_root, 'name').text = ' ' + token + ' '
            ET.SubElement(aux_root, 'kind').text = ' ' + id_dict['table'].kind_of(token) + ' '
            ET.SubElement(aux_root, 'type').text = ' ' + id_dict['table'].type_of(token) + ' '
            ET.SubElement(aux_root, 'id_x').text = ' ' + str(id_dict['table'].index_of(token)) + ' '

        else:
            ET.SubElement(root, label_map[token_type]).text = ' '+token+' '

        if not unconditional_eat:
            self.tokenizer.advance()

        return token

    def error_handle(self, msg):
        print(msg)

        self.close(1)

    def check_identifier(self):
        return bool(self.tokenizer.token_type() == 4)

    def check_type(self):
        return bool(self.tokenizer.token() in ('int', 'char', 'boolean') or self.check_identifier())

    def compile_class_vardec(self, root):
        class_vd_root = ET.SubElement(root, 'classVarDec')

        kind = self.eat(self.tokenizer.token(), class_vd_root)

        type_ = self.eat(self.tokenizer.token(), class_vd_root, [self.check_type(), "Wrong type for class variable."])

        while True:
            self.eat(self.tokenizer.token(), class_vd_root, [self.check_identifier(),
                                                             "Improper class variable name."],
                     {'kind': kind, 'type': type_, 'table': self.class_table})

            if self.tokenizer.current_token == ';':
                break

            self.eat(',', class_vd_root)

        self.eat(';', class_vd_root)

    def compile_vardec(self, root):
        vardec_root = ET.SubElement(root, 'varDec')

        self.eat('var', vardec_root)

        type_ = self.eat(self.tokenizer.token(), vardec_root, [self.check_type(), "Wrong type for variable."])

        var_count = 0

        while True:
            self.eat(self.tokenizer.token(), vardec_root, [self.check_identifier(), "Improper class variable name."],
                     {'kind': 'local', 'type': type_, 'table': self.subroutine_table})

            var_count += 1

            if self.tokenizer.current_token == ';':
                break

            self.eat(',', vardec_root)

        self.eat(';', vardec_root)

        return var_count

    def compile_param_list(self, root, is_method=False):
        param_root = ET.SubElement(root, 'parameterList')

        if is_method:
            self.eat('this', param_root, id_dict={'kind': 'argument', 'type': self.class_name,
                                                  'table': self.subroutine_table}, unconditional_eat=True)

        if self.tokenizer.token() == ')':
            return

        if is_method:
            self.eat(',', param_root, unconditional_eat=True)

        while True:
            kind = 'argument'

            type_ = self.eat(self.tokenizer.token(), param_root, [self.check_type(), "Wrong type for parameter"])

            self.eat(self.tokenizer.token(), param_root, [self.check_identifier(), "Improper parameter variable name."],
                     {'kind': kind, 'type': type_, 'table': self.subroutine_table})

            if self.tokenizer.token() == ')':
                break

            self.eat(',', param_root)

    def compile_subroutine_body(self, root, curr_func, is_method=False):
        sr_body_root = ET.SubElement(root, 'subroutineBody')

        self.eat('{', sr_body_root)

        var_count = 0

        while self.tokenizer.token() == 'var':
            var_count += self.compile_vardec(sr_body_root)

        self.vm_writer.write_func(self.class_name+'.'+curr_func, var_count)

        if curr_func == 'new':
            self.vm_writer.write_push('constant', self.class_table.var_count('field'))
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)

        if is_method:
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)

        self.compile_statements(sr_body_root)

        self.eat('}', sr_body_root)

    def compile_subroutine_dec(self, root):

        self.subroutine_table.start_subroutine()

        subroutine_root = ET.SubElement(root, 'subroutineDec')

        method = bool(self.eat(self.tokenizer.token(), subroutine_root) == 'method')

        self.eat(self.tokenizer.token(), subroutine_root, [self.tokenizer.token() == 'void' or self.check_type(),
                                                           "Wrong type for subroutine."])

        curr_func = self.eat(self.tokenizer.token(), subroutine_root,
                             [self.check_identifier(), "Improper subroutine name"])

        self.eat('(', subroutine_root)

        self.compile_param_list(subroutine_root, method)

        self.eat(')', subroutine_root)

        self.compile_subroutine_body(subroutine_root, curr_func, method)

    """
        Returns name of sub function of class if it is called by object and number of parameters needed
    """

    def compile_subroutine_call(self, root):

        sr_params = []

        if self.tokenizer.token() == '.':
            self.eat('.', root)

            sr_params.append(self.eat(self.tokenizer.token(), root, [self.check_identifier(),
                                                                     "Mismatch: Term expected, got {0}.".format
                                                                     (self.tokenizer.token())]))

        self.eat('(', root)

        sr_params.append(self.compile_expression_list(root))

        self.eat(')', root)

        return sr_params

    def compile_class(self):
        class_root = ET.Element('class')

        self.root = class_root

        self.eat('class', class_root)

        self.class_name = self.eat(self.tokenizer.token(), class_root, [self.check_identifier(),
                                                                        "Identifier expected after keyword class."])

        self.eat('{', class_root)

        while self.tokenizer.token() in ('static', 'field'):
            self.compile_class_vardec(class_root)

        while self.tokenizer.token() in ('constructor', 'function', 'method'):
            self.compile_subroutine_dec(class_root)

        self.eat('}', class_root)

    def compile_if(self, root):
        if_root = ET.SubElement(root, 'ifStatement')

        self.eat('if', if_root)

        self.eat('(', if_root)

        self.compile_expression(if_root)

        self.eat(')', if_root)

        # If condition passes with not, go to else clause
        self.vm_writer.write_arithmetic('~')

        # Store to avoid disturbing recursion
        if_else_runner = self.if_else_runner

        self.if_else_runner += 1

        self.vm_writer.write_if('IF_END_' + str(if_else_runner))

        self.eat('{', if_root)

        self.compile_statements(if_root)

        self.eat('}', if_root)

        self.vm_writer.write_go_to('IF_ELSE_END_' + str(if_else_runner))

        self.vm_writer.write_label('IF_END_' + str(if_else_runner))

        if self.tokenizer.token() == 'else':
            self.eat('else', if_root)

            self.eat('{', if_root)

            self.compile_statements(if_root)

            self.eat('}', if_root)

        self.vm_writer.write_label('IF_ELSE_END_' + str(if_else_runner))

    def compile_while(self, root):
        while_root = ET.SubElement(root, 'whileStatement')

        self.vm_writer.write_label('WHILE_BEGIN_' + str(self.while_runner))

        self.eat('while', while_root)

        self.eat('(', while_root)

        self.compile_expression(while_root)

        self.vm_writer.write_arithmetic('~')

        while_runner = self.while_runner

        self.while_runner += 1

        self.vm_writer.write_if('WHILE_END_' + str(while_runner))

        self.eat(')', while_root)

        self.eat('{', while_root)

        self.compile_statements(while_root)

        self.eat('}', while_root)

        self.vm_writer.write_go_to('WHILE_BEGIN_' + str(while_runner))

        self.vm_writer.write_label('WHILE_END_' + str(while_runner))

    def compile_let(self, root):
        let_root = ET.SubElement(root, 'letStatement')

        self.eat('let', let_root)

        # temp, to add: a[i]=...
        var_name = self.tokenizer.token()

        self.compile_term(let_root, diff_root=False, rhs=False)

        self.eat('=', let_root)

        self.compile_expression(let_root)

        self.eat(';', let_root)

        if self.subroutine_table.contains(var_name):
            self.vm_writer.write_pop(self.subroutine_table.kind_of(var_name),
                                     self.subroutine_table.index_of(var_name)-1)

        elif self.class_table.contains(var_name):
            self.vm_writer.write_pop(self.class_table.kind_of(var_name),
                                     self.class_table.index_of(var_name)-1)

        else:
            self.error_handle('Variable not defined.')

    def compile_return(self, root):
        return_root = ET.SubElement(root, 'returnStatement')

        self.eat('return', return_root)

        if self.tokenizer.token() != ';':
            self.compile_expression(return_root)

        else:
            self.vm_writer.write_push('constant', 0)

        self.vm_writer.write_return()

        self.eat(';', return_root)

    def compile_do(self, root):
        do_root = ET.SubElement(root, 'doStatement')

        self.eat('do', do_root)

        if self.check_identifier():
            curr_item = self.eat(self.tokenizer.token(), do_root)

            if self.tokenizer.token() in ('.', '('):
                sr_params = self.compile_subroutine_call(do_root)

                if len(sr_params) > 1:
                        sr_params[1] += 1

                        # Pushes calling object as first parameter to method
                        if self.subroutine_table.contains(curr_item):
                            curr_func = self.subroutine_table.type_of(curr_item) + '.' + sr_params[0]

                            self.vm_writer.write_push(self.subroutine_table.kind_of(curr_item),
                                                      self.subroutine_table.index_of(curr_item) - 1)

                        elif self.class_table.contains(curr_item):
                            curr_func = self.class_table.type_of(curr_item) + '.' + sr_params[0]

                            self.vm_writer.write_push(self.class_table.kind_of(curr_item),
                                                      self.class_table.index_of(curr_item) - 1)

                        else:
                            # Builtin or imported function

                            curr_func = curr_item + '.' + sr_params[0]

                            sr_params[1] -= 1

                        self.vm_writer.write_call(curr_func, sr_params[1])

                else:
                    """Check if a function which is not called by object has to be prefixed by classname+."""
                    self.vm_writer.write_push('pointer', 0)

                    self.vm_writer.write_call(self.class_name+'.'+curr_item, sr_params[0]+1)

        else:
            self.error_handle('Improper function call')

        self.eat(';', do_root)

        self.vm_writer.write_pop('temp', 0)

    def compile_statements(self, root):
        statement_root = ET.SubElement(root, 'statements')

        while True:
            curr_token = self.tokenizer.token()

            if curr_token == 'if':
                self.compile_if(statement_root)

            elif curr_token == 'while':
                self.compile_while(statement_root)

            elif curr_token == 'let':
                self.compile_let(statement_root)

            elif curr_token == 'return':
                self.compile_return(statement_root)

            elif curr_token == 'do':
                self.compile_do(statement_root)

            else:
                break

    def compile_term(self, root, diff_root=True, rhs=True):
        token_type = self.tokenizer.token_type()

        if diff_root:
            term_root = ET.SubElement(root, 'term')
        else:
            term_root = root

        if token_type in (0, 2, 3):
            item = self.eat(self.tokenizer.token(), term_root)

            if token_type == 0:
                if item == 'true':
                    self.vm_writer.write_push('constant', 0)
                    self.vm_writer.write_arithmetic('~')

                elif item == 'false':
                    self.vm_writer.write_push('constant', 0)

                elif item == 'this':
                    self.vm_writer.write_push('pointer', 0)

            if token_type == 2:
                self.vm_writer.write_push('constant', item)

        elif token_type == 4:
            curr_item = self.eat(self.tokenizer.token(), term_root)

            if self.tokenizer.token() == '[':
                self.eat('[', term_root)
                self.compile_expression(term_root)
                self.eat(']', term_root)

            elif self.tokenizer.token() in ('.', '('):
                sr_params = self.compile_subroutine_call(term_root)

                if rhs:
                    if len(sr_params) > 1:
                            sr_params[1] += 1

                            # Pushes calling object as first parameter to method
                            if self.subroutine_table.contains(curr_item):
                                curr_func = self.subroutine_table.type_of(curr_item) + '.' + sr_params[0]

                                self.vm_writer.write_push(self.subroutine_table.kind_of(curr_item),
                                                          self.subroutine_table.index_of(curr_item) - 1)

                            elif self.class_table.contains(curr_item):
                                curr_func = self.class_table.type_of(curr_item) + '.' + sr_params[0]

                                self.vm_writer.write_push(self.class_table.kind_of(curr_item),
                                                          self.class_table.index_of(curr_item) - 1)

                            else:
                                # Builtin or imported function
                                sr_params[1] -= 1

                                curr_func = curr_item + '.' + sr_params[0]

                            self.vm_writer.write_call(curr_func, sr_params[1])

                    else:
                        self.vm_writer.write_push('pointer', 0)

                        self.vm_writer.write_call(self.class_name+'.'+curr_item, sr_params[0]+1)

            elif rhs:
                if self.subroutine_table.contains(curr_item):
                    self.vm_writer.write_push(self.subroutine_table.kind_of(curr_item),
                                              self.subroutine_table.index_of(curr_item) - 1)

                elif self.class_table.contains(curr_item):
                    self.vm_writer.write_push(self.class_table.kind_of(curr_item),
                                              self.class_table.index_of(curr_item) - 1)

                else:
                    self.error_handle('Variable not defined.')

        elif token_type == 1:

            token = self.tokenizer.token()

            if token == '(':
                self.eat('(', term_root)
                self.compile_expression(term_root)
                self.eat(')', term_root)

            elif token in ('-', '~'):
                unary_op = self.eat(self.tokenizer.token(), term_root)

                self.compile_term(term_root)

                if unary_op == '-':
                    self.vm_writer.write_arithmetic('unary_neg')

                else:
                    self.vm_writer.write_arithmetic('~')

            # elif token == '&':
            #     self.vm_writer.write_arithmetic('&')

        else:
            self.error_handle('Mismatch: Term expected, got {0}.'.format(self.tokenizer.token()))

    def compile_expression(self, root):
        expr_root = ET.SubElement(root, 'expression')

        self.compile_term(expr_root)

        if self.tokenizer.token() in ('+', '*', '/', '&', '|', '-', '=', '<', '>'):
            operator = self.eat(self.tokenizer.token(), expr_root)

            self.compile_term(expr_root)

            self.vm_writer.write_arithmetic(operator)

    def compile_expression_list(self, root):
        expression_list_root = ET.SubElement(root, 'expressionList')

        if self.tokenizer.token() == ')':
            return 0

        self.compile_expression(expression_list_root)

        arg_count = 1

        while self.tokenizer.token() != ')':
            arg_count += 1

            self.eat(',', expression_list_root)

            self.compile_expression(expression_list_root)

        return arg_count

    def close(self, case=0):
        self.tokenizer.close()

        tree = ET.ElementTree(self.root)
        out = self.prettify(tree.getroot())

        if case == 0:
            self.fp.write(out)
            self.fp.close()

        else:
            print()
            print(out)
            self.fp.close()
            self.vm_writer.close()
            exit(1)
