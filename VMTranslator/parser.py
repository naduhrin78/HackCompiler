import os


class Parser:
    """
                    Command Type Table
        Command:                    Returned Constant
        Arithmetic/Logic commands:  0
        Push:                       1
        Pop:                        2
        Label:                      3
        Goto:                       4
        If:                         5
        Function:                   6
        Return:                     7
        Call:                       8
    """
    arithmetic_logic_commands = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
    cmd_map = {'push': 1, 'pop': 2, 'label': 3, 'goto': 4, 'if-goto': 5,
               'function': 6, 'return': 7, 'call': 8}

    def __init__(self, file_paths, single_file):
        if not single_file:
            try:
                search_dir = os.path.dirname(file_paths[0])
                sys_index = file_paths.index(search_dir+'/Sys.vm')
                file_paths.insert(0, file_paths[sys_index])
                file_paths.pop(sys_index+1)

            except ValueError:
                print('No Entry File: Sys.vm not found.')
                exit(1)

        self.file_list = file_paths[1:]
        self.file_count = len(file_paths)-1
        self.file_name = os.path.basename(file_paths[0])[:-3]
        self.fp = open(file_paths[0], 'r')

        self.current_command = None

    def get_curr_filename(self):
        return self.file_name

    def has_more_lines(self):
        cur_pos = self.fp.tell()
        does_it = bool(self.fp.readline())
        self.fp.seek(cur_pos)
        
        if not does_it:
            if self.file_count == 0:
                return False

            self.file_count -= 1
            
            self.file_name = os.path.basename(self.file_list[0])[:-3]

            self.fp = open(self.file_list[0])

            self.file_list.pop(0)

            does_it = True
        
        return does_it

    def advance(self):
        line = self.fp.readline().strip()

        # Removes comments and whitespaces
        if line.find('//') > -1:
            line = line[:line.index('//')].strip()
            
        self.current_command = line

    def command_type(self):
        """ Refer command type table """

        if self.current_command.lower() in self.arithmetic_logic_commands:
            return 0

        cmd = self.current_command.lower().split(' ')[0]
        if cmd not in self.cmd_map.keys():
            return -1

        return self.cmd_map[cmd]

    def arg1(self):
        if self.command_type() == 0:
            return self.current_command.split()[0]

        return self.current_command.split(' ')[1]

    def arg2(self):
        if self.command_type() not in [1, 2, 6, 8]:
            print("{0} command has no second argument.".format(self.current_command.split()[0]))
            return

        return int(self.current_command.split(' ')[-1])

    def close(self):
        self.fp.close()
