import os
import time
from project.parser import parse
from pprint import pprint

def test_parser():
    folder_path = './hw01_instances'
    log_file = 'parser_speed_log.txt'

    with open(log_file, 'w') as log:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    start_time = time.time()
                    try:
                        parse(content)
                        end_time = time.time()
                        log.write(f"{file_path}: {end_time - start_time} seconds\n")
                    except Exception as e:
                        log.write(f"{file_path}: Error - {str(e)}\n")

def test_parser_on_instance(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    pprint(parse(content))


if __name__ == "__main__":
    test_parser_on_instance("./hw01_instances/easy_test.txt")