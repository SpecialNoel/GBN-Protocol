# Sender.py

# python3 Sender.py -s 127.0.0.1 -p 8888 -t apple.jpg OutputApple.jpg

from pathlib import Path
from socket import *
import math
import secrets
import struct
import sys
import threading
import time
import zlib

# ------------------------------------  Handle Files  ------------------------------------

# Get the size (int) of a string file
def get_file_size(filename):
    return Path(filename).stat().st_size

# Read message from a byte file
def read_file_content(filename):
    message = ''
    
    # Read all bytes from the input file
    with open(filename, 'rb') as bf:
        message = bf.read()

    return message

# Get a payload from the input file. Mostly it has 1024 bytes, but the last payload could have less
def get_current_payload(segmentIndex, numOfTotalSegments):
    global inputFileContent, payloadBufferSize
    
    # Get the current segment, call it payload
    startingIndex = segmentIndex * payloadBufferSize

    if segmentIndex != numOfTotalSegments - 1:
        endingIndex = startingIndex + payloadBufferSize
        payload = inputFileContent[startingIndex:endingIndex]
    else:
        payload = inputFileContent[startingIndex:]
    
    return payload

# ------------------------------------  Handle Some Basic Operations  ------------------------------------ 

# Get senderName, senderPortNumber, filename1 and filename2 based on sys.argv
# If received sys.argv does not include [5], [6] and [7], use default values on [6] and [7].
def setup_arguments():
    '''
    sys.argv[0]: Sender.py;            sys.argv[1]: -s
    sys.argv[2]: <senderName>;         sys.argv[3]: -p
    sys.argv[4]: <senderPortNumber>;   sys.argv[5]: -t
    sys.argv[6]: <filename1>;           sys.argv[7]: <filename2>
    '''
    senderName = sys.argv[2]
    senderPortNumber = (int)(sys.argv[4])
    filename1 = sys.argv[6]
    filename2 = sys.argv[7]

    return (senderName, senderPortNumber, filename1, filename2)

# Create a new UDP socket
def create_udp_socket():
    UDPSocket = socket(AF_INET, SOCK_DGRAM)
    
    return UDPSocket

# Bind UDP socket with tuple <senderName, senderPortNumber>
def bind_socket_to_address_and_port():
    global UDPSocket, senderName, senderPortNumber
    
    UDPSocket.bind((senderName, senderPortNumber))
    
    return

# ------------------------------------  Handle Timer  ------------------------------------ 

def in_timer():
    print('in timer')
    
    return

# Start a new timer that will timeout 5 seconds
def start_timer():
    timer = threading.Timer(0, in_timer)
    
    timer.start()
    timer.join(timeout=5)
    
    return timer

# Stop an existing timer
def stop_timer(timer):
    timer.cancel()
    
    return

# ------------------------------------  Handle Packets  ------------------------------------ 

# Send message
def udt_send(packet):
    global UDPSocket, receiverName, receiverPortNumber
    
    UDPSocket.sendto(packet, (receiverName, receiverPortNumber))
    
    return

# Receive response
def udt_rcv():
    global UDPSocket, messageBufferSize
    
    response, (socketServer, socketPort) = UDPSocket.recvfrom(messageBufferSize)
        
    return response, (socketServer, socketPort)

# Generate a random ISN for sender from range [0, 2^32)
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
    print(f'Payload: {payload} \n') # up to 1024 bytes
    
    return 

# Generate a header and make a packet for payload. Header size: (1-byte * 3) + (4-byte * 3) = 15 bytes
def make_pkt(payload):
    global senderSeqNum, senderAckNum, synBit, ackBit, finBit, pktFormat
    
    checksum = generate_checksum(payload)
        
    print('Sender Packet Info:')
    print_pkt_info(synBit, ackBit, finBit, senderSeqNum, senderAckNum, checksum, payload)
    
    pkt = struct.pack('!BBBIII', synBit, ackBit, finBit, senderSeqNum, senderAckNum, checksum) + payload

    return pkt

# Decompose the pkt into header and payload parts
def decompose_pkt(pkt):
    global pktFormat
    
    receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum = struct.unpack('!BBBIII', pkt[:15])
    payload = pkt[15:]
    
    print('Sender received from Receiver:')
    print_pkt_info(receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload)
    
    return receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload

# Check checksum to ensure the content of payload is not corrupted during transmission
def corrupt(payload, providedChecksum):    
    return generate_checksum(payload) != providedChecksum

# ------------------------------------  Handle Relaying Packets  ------------------------------------ 

def perform_three_way_handshake():
    global UDPSocket, messageBufferSize, synBit, ackBit, senderSeqNum, senderAckNum, receiverName, receiverPortNumber
        
    # Sender receives SYN packet sent by Receiver
    response, (address, port) = udt_rcv()
    
    # Accept Receiver socket's address name and port number
    receiverName, receiverPortNumber = address, port
    
    seqNum = decompose_pkt(response)[3]
    senderAckNum = seqNum + 1 # set sender ack num to be receiver seq num
        
    # Sender sends SYN/ACK packet with its ISN (Y) and Receiver's ISN+1 (X+1) to Receiver  
    synBit, ackBit = 1, 1
    synAckPacket = make_pkt(b'SYN/ACK')
    udt_send(synAckPacket)
    senderSeqNum += 1 # Increment sender seq num b/c of the phantom byte
        
    # Sender receives ACK packet sent by Receiver
    response = udt_rcv()[0]
    decompose_pkt(response)
    
    synBit, ackBit = 0, 0
    
    return

# Sender initiates connection termination upon transmitting every segment in input file
def perform_connection_termination():
    global ackBit, finBit, senderSeqNum, senderAckNum
    
    # Sender sends FIN packet to Receiver
    finBit = 1
    finPacket = make_pkt(b'FIN')
    udt_send(finPacket)
    senderSeqNum += 1
    
    # Sender receives ACK packet sent by Receiver
    response = udt_rcv()[0]
    decompose_pkt(response)
    senderAckNum += 1
    
    # Sender sends ACK packet to Receiver
    ackBit = 1
    finPacket = make_pkt(b'ACK')
    udt_send(finPacket)
    senderSeqNum += 1
    
    ackBit, finBit = 0, 0
    
    return

def perform_sender_operation():
    global UDPSocket, sendBase, senderSeqNum, senderWindowSize, sndpkt, fileSize, payloadBufferSize, numOfTimesTimedout
    
    # Calculate the number of segments we'll be dividing the input file, each segment is up to 1024 bytes
    segmentIndex = 0
    numOfTotalSegments = 0
    if fileSize % payloadBufferSize == 0:
        numOfTotalSegments = math.floor(fileSize / payloadBufferSize)        
    else: 
        numOfTotalSegments = math.floor(fileSize / payloadBufferSize) + 1
    
    # Server should do the following operation endlessly, until all packets have been sent to Receiver
    while True:
        # Every in input file was sent. Now send FIN packet to Receiver
        if segmentIndex == numOfTotalSegments:
            perform_connection_termination()
            break
        
        # Event: Send packet to Receiver
        if senderSeqNum < sendBase + senderWindowSize:
            # Get current segment
            sendPayload = get_current_payload(segmentIndex, numOfTotalSegments)
            segmentIndex += 1
            
            # Make the segment a packet
            sndpkt[senderSeqNum] = make_pkt(sendPayload)
            
            # Send the packet
            udt_send(sndpkt[senderSeqNum])

            # Start timer for the oldest on-flight packet
            if sendBase == senderSeqNum:
                timer = start_timer()
            
            # Increment senderSeqNum since we just sent a packet
            senderSeqNum += 1
        
        # Event: Receive packet from Receiver
        rcvpkt = udt_rcv()[0]
        if rcvpkt:
            receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload = decompose_pkt(rcvpkt)
            if not corrupt(payload, checksum):
                # Sender correctly acknowledged that Receiver has correctly received the packet, increment sendBase
                sendBase = ackNum + 1
                
                # Stop or start timer accordingly
                if sendBase == senderSeqNum:
                    stop_timer(timer)
                else:
                    timer = start_timer()

        # Event: Timeout
        if not timer.is_alive():
            # Restart timer upon timeout
            timer = start_timer()
            
            numOfTimesTimedout += 1
            
            # Retransmit N packets (all packets in the sender window)
            for i in range(sendBase, senderSeqNum):
                udt_send(sndpkt[i])
                
    return
            
# ------------------------------------  Main  ------------------------------------ 

if __name__ == '__main__':
    startTime = time.time()
    
    numOfTimesTimedout = 0
    
    # ------------------------------------  Variables  ------------------------------------ 
    
    # Buffer size of a packet 
    # 99 bits (but we count for 1-byte * 3 + 4-byte * 3 = 15 bytes) for header
    # Up to 1024 bytes for payload
    headerBufferSize = 15 # 15 bytes
    payloadBufferSize = 1024 # 1024 bytes
    messageBufferSize = headerBufferSize + payloadBufferSize # 1039 bytes
    
    # Sender SYN, ACK and FIN flag bits
    synBit, ackBit, finBit = 0, 0, 0
    
    sndpkt = {}
    
    # Initialization of sender seq num and ack num
    # Assume senderSeqNum = Y, senderAckNum = 0
    senderSeqNum = generate_random_initial_sequence_number()
    senderAckNum = 0
    
    # ------------------------------------  Basic Setup  ------------------------------------ 
    
    # Get global values from sys.argv
    senderName, senderPortNumber, filename1, filename2 = setup_arguments()
    
    receiverName, receiverPortNumber = '', 0
    
    # Create sender UDP socket
    UDPSocket = create_udp_socket()
    
    bind_socket_to_address_and_port()
    
    # Get the size of input file
    fileSize = get_file_size(filename1)
    
    # Read byte message of content from input file
    inputFileContent = read_file_content(filename1)
    
    # ------------------------------------  Handshake  ------------------------------------ 
    
    print('senderSeqNum:', senderSeqNum)
    print(f'senderAckNum: {senderAckNum} \n')
    
    perform_three_way_handshake()
    
    # After performing three-way handshake:
    #   senderSeqNum should be Y + 1
    #   senderAckNum should be X + 1
    print(f'\nsenderSeqNum: {senderSeqNum}')
    print(f'senderAckNum: {senderAckNum} \n')
    
    # ------------------------------------  Sender Operation  ------------------------------------ 
    
    # Sender send base
    sendBase = senderSeqNum
    # Sender window size N
    senderWindowSize = 16
    
    perform_sender_operation()
    
    # Close UDP socket
    UDPSocket.close()
    
    endTime = time.time()

    print('Time lapsed in seconds: {:0.2f}'.format(endTime - startTime))
    
    print('Number of time timed out:', numOfTimesTimedout)