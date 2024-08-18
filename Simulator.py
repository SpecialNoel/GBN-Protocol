# Simulator.py

# Usage: python3 Simulator.py mode, where mode is either server or receiver
# Example:  python3 Simulator.py server
# Example2: python3 Simulator.py receiver

from threading import Thread
import os
import sys
import time

def execute_sender():
    os.system('python3 Sender.py -s 127.0.0.1 -p 8888 -t apple.jpg OutputApple.jpg')

def execute_receiver():
    os.system('python3 Receiver.py -s 127.0.0.1 -p 8888')

if __name__=='__main__':
    mode = sys.argv[1]
    
    print('Start simulator\n')
    
    numberOfRun = 100
    
    if mode == 'server':
        for i in range(numberOfRun):
            t = Thread(target=execute_sender)
            t.start()
            time.sleep(1)
    elif mode == 'receiver':
        for i in range(numberOfRun):
            t = Thread(target=execute_receiver)
            t.start()
            time.sleep(1)
        
    print('\nEnd simulator')
    exit(0)