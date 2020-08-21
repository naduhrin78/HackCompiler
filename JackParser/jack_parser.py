import sys
import os
from JackParser.compilation_engine import CompilationEngine

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jack_parser.py FileDirectory/FileName.")
        sys.exit(1)

    ip_file_path = sys.argv[1]

    ip_file_name = os.path.basename(ip_file_path)

    single_file = True

    directory, filename = os.path.split(ip_file_path)

    if filename not in os.listdir(directory):
        print('Given file/directory does not exist.')
        exit(1)

    ip_file_paths, op_file_paths = None, None

    if os.path.isdir(ip_file_path):
        ip_file_names = list(filter(lambda x: x[-5:] == '.jack', os.listdir(ip_file_path)))

        ip_file_paths = [os.path.join(ip_file_path, file) for file in ip_file_names]

        op_file_paths = [os.path.join(ip_file_path, file[:-5] + '.xml') for file in ip_file_names]

        single_file = False

    elif ip_file_name[-5:] == '.jack':
        ip_file_paths = [ip_file_path]

        op_file_paths = [ip_file_path.split('.')[0] + '.xml']

    else:
        print('Improper format: Provide .jack file or directory containing such file.')
        exit(1)

    for ip_file, op_file in zip(ip_file_paths, op_file_paths):
        ce_instance = CompilationEngine(ip_file, op_file)

        ce_instance.tokenizer.advance()

        ce_instance.compile_class()

        ce_instance.close()
