# FileComparer.py

# Usage: python3 FileComparer.py filename1 filename2
# Example: python3 FileComparer.py apple.jpg OutputApple.jpg

import filecmp
import os
import sys

if __name__=='__main__':
    # Get filename1 and filename 2 from command arguments
    try:
        filename1 = sys.argv[1]
        filename2 = sys.argv[2]
    except SyntaxError as e:
        print(f'Error: Invalid arguments. Syntax: FileComparer.py <filename1> <filename2>')
        exit(0)
    
    # Compare the files to see whether they have the exact same content
    try:
        print(f'{filename1} and {filename2} have the same content:', filecmp.cmp(filename1, filename2, shallow=False))
    except FileNotFoundError as e:
        print('Error: %s - %s.' % (e.filename, e.strerror))
        exit(0)
    
    # Delete the second file (the output file that is generated by program generated)
    try:
        os.remove(filename2)
        print(f'Deleted {filename2}')
    except OSError as e:
        print('Error: %s - %s.' % (e.filename, e.strerror))
        
    exit(0)