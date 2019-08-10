import sys
import os
from collections import defaultdict
from parser import Parser
from codewriter import CodeWriter


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py FileDirectory/FileName.")
        sys.exit(1)
    
    ip_file_path = sys.argv[1]

    ip_file_name = os.path.basename(ip_file_path)

    single_file = True

    directory, filename = os.path.split(ip_file_path)

    if filename not in os.listdir(directory):
        print('Given file/directory does not exist.')
        exit(1)

    if os.path.isdir(ip_file_name):
        ip_file_names = list(filter(lambda x: x[-3:] == '.vm', os.listdir(ip_file_path)))

        ip_file_paths = [os.path.join(ip_file_path, file) for file in ip_file_names]

        op_file_path = os.path.join(ip_file_path, ip_file_name+'.asm')

        single_file = False

    elif ip_file_name[-3:] == '.vm':
        ip_file_paths = [ip_file_path]

        op_file_path = ip_file_path.split('.')[0]+'.asm'

    else:
        print('Improper format: Provide .vm file or directory containing such file.')
        exit(1)

    parser = Parser(ip_file_paths, single_file)
    
    print('Output file: '+op_file_path)
    
    writer = CodeWriter(op_file_path, single_file)

    while parser.has_more_lines():

        parser.advance()

        cmd_type = parser.command_type()

        if cmd_type == 0:
            writer.write_arithmetic(parser.arg1())

        elif cmd_type == 1:
            writer.write_push_pop('push', parser.arg1(), parser.arg2(), parser.get_curr_filename())

        elif cmd_type == 2:
            writer.write_push_pop('pop', parser.arg1(), parser.arg2(), parser.get_curr_filename())

        elif cmd_type == 3:
            writer.write_label(parser.arg1())

        elif cmd_type == 4:
            writer.write_goto(parser.arg1())

        elif cmd_type == 5:
            writer.write_if_goto(parser.arg1())

        elif cmd_type == 6:
            writer.write_function(parser.arg1(), parser.arg2())

        elif cmd_type == 7:
            writer.write_return()

        elif cmd_type == 8:
            writer.write_call(parser.arg1(), parser.arg2())

    parser.close()
    writer.close()

