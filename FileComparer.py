# FileComparer.py

# python3 FileComparer.py

import filecmp
import os

if __name__=='__main__':
    filename1 = 'apple.jpg'
    filename2 = 'OutputApple.jpg'
    
    # Compare with two files have the exact same content
    try:
        print(f'{filename1} and {filename2} have the same content:', filecmp.cmp(filename1, filename2, shallow=False))
    except FileNotFoundError as e:
        print('Error: %s - %s.' % (e.filename, e.strerror))
        exit()
    
    # Delete the second file (program generated file)
    try:
        os.remove(filename2)
        print(f'Deleted {filename2}')
    except OSError as e:
        print('Error: %s - %s.' % (e.filename, e.strerror))