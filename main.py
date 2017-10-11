from compare_ast import match_two_files

def main():
    file1_path = './test1.py'
    file2_path = './test2.py'
    match_two_files(file1_path, file2_path)

if __name__ == '__main__':
    main()
