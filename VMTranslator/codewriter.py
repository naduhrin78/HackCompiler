from collections import defaultdict
import os


class CodeWriter:

    def __init__(self, filename, single_file):
        self.fp = open(filename, 'w')
        self.translated_code = ""
        self.num_arthm_ops = 0
        self.code_template = defaultdict(str)
        self.call_count = defaultdict(int)

        for _dir in os.listdir('basic_commands'):
            if _dir[0] == '.':
                continue

            if _dir[-4:] == '.txt':
                self.code_template[_dir[:-4]] = open('basic_commands/'+_dir, 'r').read()
                continue

            for file in os.listdir('basic_commands/'+_dir):
                if file[0] == '.':
                    continue
                self.code_template[file[:-4]] = open('basic_commands/'+_dir+'/'+file, 'r').read()

        for _dir in os.listdir('control_commands'):
            if _dir[0] == '.':
                continue

            if _dir[-4:] == '.txt':
                self.code_template[_dir[:-4]] = open('control_commands/'+_dir, 'r').read()
                continue

        for _dir in os.listdir('function_commands'):
            if _dir[0] == '.':
                continue

            if _dir[-4:] == '.txt':
                self.code_template[_dir[:-4]] = open('function_commands/'+_dir, 'r').read()
                continue

        if not single_file:
            self.translated_code = self.code_template['bootstrap']

            self.fp.write(self.translated_code)
            self.write_call('Sys.init', 0)

    def write_arithmetic(self, cmd):
        self.translated_code = self.code_template[cmd.lower()].format(self.num_arthm_ops)

        self.fp.write(self.translated_code)
        self.num_arthm_ops += 1

    def write_push_pop(self, _type, arg1, arg2, file_name):
        cmd_file = _type+'_'+arg1

        if arg1 == 'pointer':
            cmd_file += ('_'+str(arg2))

        self.translated_code = self.code_template[cmd_file.lower()].format(arg2, file_name)

        self.fp.write(self.translated_code)

    def write_label(self, label):
        self.translated_code = self.code_template['label'].format(label)

        self.fp.write(self.translated_code)

    def write_goto(self, label):
        self.translated_code = self.code_template['goto'].format(label)

        self.fp.write(self.translated_code)

    def write_if_goto(self, label):
        self.translated_code = self.code_template['if-goto'].format(label)

        self.fp.write(self.translated_code)

    def write_function(self, name, lcl_cnt):
        self.translated_code = self.code_template['function'].format(name, lcl_cnt)

        self.fp.write(self.translated_code)

    def write_return(self):
        self.translated_code = self.code_template['return']

        self.fp.write(self.translated_code)

    def write_call(self, name, arg_cnt):
    	self.call_count[name] += 1
    	
        self.translated_code = self.code_template['call'].format(name, arg_cnt, self.call_count[name])

        self.fp.write(self.translated_code)

    def close(self):
        self.translated_code = self.code_template['end']

        self.fp.write(self.translated_code)

        self.fp.close()
        