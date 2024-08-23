# NewReceiver.py

# Usage: python3 NewReceiver.py -s serverIPAddress -p serverPortNumber
# Example: python3 NewReceiver.py -s 127.0.0.1 -p 8888

# To execute NewReceiver.py, run the Sender side program (NewSender.py) first.

from socket import *
import secrets
import struct
import sys
import time
import zlib

import os

# ------------------------------------  Handle Files  ------------------------------------

# Append content to a byte file
def deliver_data(payload, filename):
    with open(filename, 'ab') as bf:
        bf.write(payload)

    return

# ------------------------------------  Handle Basic Operations  ------------------------------------ 

# Get senderIPAddress and senderPortNumber based on sys.argv
def setup_arguments():
    '''
    sys.argv[0]: Receiver.py;           sys.argv[1]: -s
    sys.argv[2]: <senderIPAddress>;     sys.argv[3]: -p
    sys.argv[4]: <senderPortNumber>
    '''
    senderIPAddress = sys.argv[2]
    senderPortNumber = (int)(sys.argv[4])
        
    return (senderIPAddress, senderPortNumber)

# Create a new UDP socket
def create_udp_socket():
    UDPSocket = socket(AF_INET, SOCK_DGRAM)
    
    return UDPSocket

# ------------------------------------  Handle Packets  ------------------------------------ 

# Send message
def udt_send(packet):
    global UDPSocket, senderIPAddress, senderPortNumber
    
    UDPSocket.sendto(packet, (senderIPAddress, senderPortNumber))
    
    return

# Receive response
def udt_rcv():
    global UDPSocket, messageBufferSize
    
    response, (socketServer, socketPort) = UDPSocket.recvfrom(messageBufferSize)
        
    return response, (socketServer, socketPort)

# Generate a random ISN for Receiver from range [0, 2^32)
def generate_random_initial_sequence_number():
    return secrets.randbelow(2 ** 32)

# Generate an unsigned int of 32-bit (or 4 bytes) checksum for the payload
def generate_checksum(payload):
    return zlib.crc32(payload)

# Print every information about a packet
def print_pkt_info(synBit, ackBit, finBit, seqNum, ackNum, checksum, payload):
    print('Seq Num:', seqNum) # 4 bytes
    print('Ack Num:', ackNum) # 4 bytes
    print('Checksum:', checksum) # 4 bytes
    #print(f'Payload: {payload} \n') # up to 1024 bytes
    
    return 

# Generate a header and make a packet for payload. Header size: (1-byte * 3) + (4-byte * 3) = 15 bytes
def make_pkt(payload):
    global receiverSeqNum, receiverAckNum, synBit, ackBit, finBit, pktFormat
    
    checksum = generate_checksum(payload)
        
    print('Receiver Packet Info:')
    print_pkt_info(synBit, ackBit, finBit, receiverSeqNum, receiverAckNum, checksum, payload)
    
    pkt = struct.pack(pktFormat, synBit, ackBit, finBit, receiverSeqNum, receiverAckNum, checksum) + payload
    
    return pkt

# Decompose the pkt into header and payload parts
def decompose_pkt(pkt):
    global pktFormat
    
    receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum = struct.unpack(pktFormat, pkt[:15])
    payload = pkt[15:]
    
    print('Receiver received from Sender:')
    print_pkt_info(receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload)
    
    return receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload

# Check checksum to ensure the content of payload is not corrupted during transmission
def is_corrupted(payload, providedChecksum):    
    return generate_checksum(payload) != providedChecksum

# ------------------------------------  Handle Relaying Packets  ------------------------------------ 

def perform_three_way_handshake():
    global UDPSocket, messageBufferSize, synBit, ackBit, receiverSeqNum, receiverAckNum
        
    # Receiver sends SYN packet with its ISN (X) to Sender
    synBit, ackBit = 1, 0
    synPacket = make_pkt(b'SYN')
    udt_send(synPacket)
    receiverSeqNum += 1 # Increment Receiver seq num b/c of the phantom byte
        
    # Receiver receives SYN/ACK packet sent by Sender
    response = udt_rcv()[0]
    seqNum = decompose_pkt(response)[3]
    receiverAckNum = seqNum + 1 # set Receiver ack num to be Sender seq num
        
    # Receiver sends ACK packet with Sender's ISN + 1 (Y+1) to Sender
    synBit, ackBit = 0, 1
    ackPacket = make_pkt(b'ACK')
    udt_send(ackPacket)
    
    synBit, ackBit = 0, 0
       
    return

# Receiver receives connection termination upon receiving every segment in input file
def perform_connection_termination():
    global ackBit, finBit, receiverSeqNum, receiverAckNum
    
    receiverAckNum += 1
    
    # Receiver sends FIN/ACK packet to Sender
    ackBit, finBit = 1, 1
    ackFinPacket = make_pkt(b'ACK/FIN')
    udt_send(ackFinPacket)
    receiverSeqNum += 1
    
    # Receiver receives ACK packet sent by Sender
    response = udt_rcv()[0]
    decompose_pkt(response)
    receiverAckNum += 1
    
    ackBit, finBit = 0, 0
    
    return

def perform_receiver_operation():
    global UDPSocket, receiverAckNum, sndpkt, fileSize, payloadBufferSize, filename
    
    # Used to keep track of whether filename is already receiver by Receiver or not
    filenameReceived = False
    
    # Receiver should do the following operation endlessly, until receiving FIN packet from Sender
    while True:
        # Event: Receive packet from Receiver
        rcvpkt = udt_rcv()[0]
        if rcvpkt:
            receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload = decompose_pkt(rcvpkt)
            if not is_corrupted(payload, checksum) and receivedFinBit == 1:
                # Every in input file was received. Now receive FIN packet from Sender
                print('Hello, world')
                perform_connection_termination()
                break
            elif not is_corrupted(payload, checksum) and receiverAckNum == seqNum:
                # Received in-order packet correctly from Sender
                if not filenameReceived:
                    # Received filename from Sender
                    filename = payload.decode()
                    filenameReceived = True
                else: 
                    # Received file content from Sender 
                    # Now send an acknowledgement packet with current ack number (receiverAckNum) back to Sender.
                    # Then, increment current ack number by one
                    deliver_data(payload, filename)
                sndpkt = make_pkt(b'')
                udt_send(sndpkt)
                receiverAckNum += 1
            else:
                # Received out-of-order packet. 
                # Now send a acknowledgement packet with largest correct ack number (receiverAckNum - 1) to Sender.
                receiverAckNum -= 1
                sndpkt = make_pkt(b'')
                udt_send(sndpkt)
                # Revert current ack number back to receievrAckNum
                receiverAckNum += 1
                
    return
            
# ------------------------------------  Main  ------------------------------------ 

if __name__ == '__main__':
    startTime = time.time()
    
    # ------------------------------------  Values  ------------------------------------ 
    
    # Buffer size of a packet 
    # 15 bytes for header (1-byte for each SYN, ACK and FIN bit, 4-byte for each seqNum, ackNum, checksum)
    # Up to 1009 bytes for payload
    headerBufferSize = 15 # 15 bytes
    payloadBufferSize = 1009 # 1009 bytes
    messageBufferSize = headerBufferSize + payloadBufferSize # 1024 bytes
    
    # Receiver SYN, ACK and FIN flag bits
    synBit, ackBit, finBit = 0, 0, 0
    
    pktFormat = '!BBBIII'
        
    # Initialization of Receiver seq num and ack num
    # Assume receiverSeqNum = X, receiverAckNum = 0
    receiverSeqNum = generate_random_initial_sequence_number()
    receiverAckNum = 0
    
    # ------------------------------------  Basic Setup  ------------------------------------ 
    
    # Get global values from sys.argv
    senderIPAddress, senderPortNumber = setup_arguments()
    
    # Create Receiver UDP socket
    UDPSocket = create_udp_socket()
    
    # The filename used to store the requested file from Sender
    # It will have the exact name as Sender's filename2
    filename = ''
    
    # ------------------------------------  Handshake  ------------------------------------ 
    
    # Before performing three-way handshake:
    #   receiverSeqNum should be X
    #   receiverAckNum should be 0
    print('receiverSeqNum:', receiverSeqNum)
    print(f'receiverAckNum: {receiverAckNum} \n')
    
    perform_three_way_handshake()
    
    # After performing three-way handshake:
    #   receiverSeqNum should be X + 1
    #   receiverAckNum should be Y + 1, where Y is Sender's seq num
    print(f'\nreceiverSeqNum: {receiverSeqNum}')
    print(f'receiverAckNum: {receiverAckNum} \n')
    
    # ------------------------------------  Receiver Operation  ------------------------------------ 
        
    perform_receiver_operation()
    
    # Close UDP socket
    UDPSocket.close()
    
    # Print out the amount of time used for executing this program
    endTime = time.time()
    print('Time lapsed in seconds: {:0.2f}'.format(endTime - startTime))
    
    # For testing with Simulator
    os.system('python3 FileComparer.py apple.jpg OutputApple.jpg')
    
    