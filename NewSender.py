# NewSender.py

# Usage: python3 NewSender.py -s senderIPAddress -p senderPortNumber -t filename1 filename2
# Example: python3 NewSender.py -s 127.0.0.1 -p 8888 -t Apple.jpg OutputApple.jpg

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

# Get the size (int) of the string file
def get_file_size(filename):
    return Path(filename).stat().st_size

# Read content in bytes from the string file
def read_file_content(filename):
    content = b''
    
    # Read all bytes from the file
    with open(filename, 'rb') as bf:
        content = bf.read()

    return content

# Get a payload from the input file. Mostly it is 1009 bytes, but the last payload could have less
def get_one_payload_from_input_file(segmentIndex, numOfTotalSegments):
    global fileContent, payloadBufferSize
    
    startingIndex = segmentIndex * payloadBufferSize

    if segmentIndex != numOfTotalSegments - 1:
        # Regular segment; have 1009 bytes of payload
        endingIndex = startingIndex + payloadBufferSize
        payload = fileContent[startingIndex:endingIndex]
    else:
        # Last segment; might have less than 1009 bytes of payload
        payload = fileContent[startingIndex:]
    
    return payload

# ------------------------------------  Handle Basic Operations  ------------------------------------ 

# Get senderIPAddress, senderPortNumber, filename1 and filename2 based on sys.argv
# If received sys.argv does not include [5], [6] and [7], use default values on [6] and [7].
def setup_arguments():
    '''
    sys.argv[0]: Sender.py;            sys.argv[1]: -s
    sys.argv[2]: <senderIPAddress>;    sys.argv[3]: -p
    sys.argv[4]: <senderPortNumber>;   sys.argv[5]: -t
    sys.argv[6]: <filename1>;           sys.argv[7]: <filename2>
    '''
    senderIPAddress = sys.argv[2]
    senderPortNumber = (int)(sys.argv[4])
    filename1 = sys.argv[6]
    filename2 = sys.argv[7]

    return (senderIPAddress, senderPortNumber, filename1, filename2)

# Create a new UDP socket
def create_udp_socket():
    UDPSocket = socket(AF_INET, SOCK_DGRAM)
    
    return UDPSocket

# Bind UDP socket with tuple <senderIPAddress, senderPortNumber>
def bind_socket_to_address_and_port():
    global UDPSocket, senderIPAddress, senderPortNumber
    
    # Bind Sender IP and port to this UDP socekt
    UDPSocket.bind((senderIPAddress, senderPortNumber))
    
    return

# ------------------------------------  Handle Timer  ------------------------------------ 

# Provide feedback of being in timer while spinning
def in_timer():
    print('in timer')
    
    return

# Start a new timer that will timeout after 5 seconds
def start_timer():
    timer = threading.Timer(0, in_timer)
    
    # Start timer
    timer.start()
    timer.join(timeout=5)
    
    return timer

# Stop an existing timer
def stop_timer(timer):    
    # Cancel current timer
    timer.cancel()
        
    return

# ------------------------------------  Handle Packets  ------------------------------------ 

# Send message
def udt_send(packet):
    global UDPSocket, receiverIPAddress, receiverPortNumber
    
    # Send packet to Receiver with the specified Receiver IP and port
    UDPSocket.sendto(packet, (receiverIPAddress, receiverPortNumber))
    
    return

# Receive response
def udt_rcv():
    global UDPSocket, messageBufferSize

    # Receive packet of up to 1024 bytes, along with specified Receiver IP and port, from Receiver
    response, (socketIPAddress, socketPortNumber) = UDPSocket.recvfrom(messageBufferSize)
        
    return response, (socketIPAddress, socketPortNumber)

# Generate a random ISN for Sender from range [0, 2^32)
def generate_random_initial_sequence_number():
    return secrets.randbelow(2 ** 32)

# Generate an unsigned int of 32-bit (or 4 bytes) checksum for the payload
def generate_checksum(payload):
    return zlib.crc32(payload)

# Print every information about a packet
def print_pkt_info(synBit, ackBit, finBit, seqNum, ackNum, checksum, payload):
    print('Seq Num:', seqNum)       # 4 bytes
    print('Ack Num:', ackNum)       # 4 bytes
    print('Checksum:', checksum)    # 4 bytes
    print(f'Payload: {payload} \n') # up to 1009 bytes
    
    return 

# Generate a header and make a packet for payload. Each header is 15 bytes
def make_pkt(payload):
    global senderSeqNum, senderAckNum, synBit, ackBit, finBit
    
    # Calculate the checksum for payload
    checksum = generate_checksum(payload)
        
    # Print out info about this pkt
    print('Sender Packet Info:')
    print_pkt_info(synBit, ackBit, finBit, senderSeqNum, senderAckNum, checksum, payload)
    
    # Generate pkt with pack(header, checksum) and payload
    pkt = struct.pack(pktFormat, synBit, ackBit, finBit, senderSeqNum, senderAckNum, checksum) + payload

    return pkt

# Decompose the pkt into header and payload parts
def decompose_pkt(pkt):    
    # fields in the 15-byte Header of the rcvpkt
    receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum = struct.unpack(pktFormat, pkt[:15])
    payload = pkt[15:]
    
    # Print out info about this pkt
    print('Sender received from Receiver:')
    print_pkt_info(receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload)
    
    return receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload

# Check checksum to ensure the content of payload is not corrupted during transmission
def is_corrupted(payload, providedChecksum):    
    return generate_checksum(payload) != providedChecksum

# ------------------------------------  Handle Relaying Packets  ------------------------------------ 

def perform_three_way_handshake():
    global UDPSocket, messageBufferSize, synBit, ackBit, senderSeqNum, senderAckNum, receiverIPAddress, receiverPortNumber
        
    # Sender receives SYN packet sent by Receiver
    response, (address, port) = udt_rcv()
    
    # Record Receiver IP address name and port number
    receiverIPAddress, receiverPortNumber = address, port
    
    # Set Sender ack num to be Receiver seq num + 1
    seqNum = decompose_pkt(response)[3]
    senderAckNum = seqNum + 1
        
    # Sender sends SYN/ACK packet with its ISN (Y) and Receiver's ISN+1 (X+1) to Receiver  
    synBit, ackBit = 1, 1
    synAckPacket = make_pkt(b'SYN/ACK')
    udt_send(synAckPacket)
    senderSeqNum += 1 # Increment Sender seq num because of the phantom byte
        
    # Sender receives ACK packet sent by Receiver
    response = udt_rcv()[0]
    decompose_pkt(response)
    
    # Reset SYN and ACK bits to 0
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
    
    # Reset ACK and FIN bits to 0
    ackBit, finBit = 0, 0
    
    return

# Perform Sender side GBN operations
def perform_sender_operation():
    global UDPSocket, sendBase, senderSeqNum, senderWindowSize, sndpkt, fileSize, payloadBufferSize, filename2
    
    # Used to keep track of whether filename2 is already sent by Sender or not
    filenameSent = False
        
    # Calculate the amount of segments we'll be dividing the input file; each segment is up to 1009 bytes
    segmentIndex = 0
    numOfTotalSegments = 0
    if fileSize % payloadBufferSize == 0:
        numOfTotalSegments = math.floor(fileSize / payloadBufferSize)        
    else: 
        numOfTotalSegments = math.floor(fileSize / payloadBufferSize) + 1
        
    # Sender should do the following operation endlessly, 
    #   until Sender knows that all packets have been correctly sent to Receiver
    while True:
        # Every in input file was sent. Now send FIN packet to Receiver
        if segmentIndex == numOfTotalSegments:
            perform_connection_termination()
            break
        
        # Event: Send packet to Receiver
        if senderSeqNum < sendBase + senderWindowSize:
            # Send filename to Receiver
            if not filenameSent:
                sendPayload = filename2.encode()
                filenameSent = True
            else:
                # Send filecontent to Receiver
                # Get current segment, then increment segment index by 1
                sendPayload = get_one_payload_from_input_file(segmentIndex, numOfTotalSegments)
                segmentIndex += 1
            
            # Make the segment a packet by adding a header to it
            sndpkt[senderSeqNum] = make_pkt(sendPayload)
            
            # Send the packet to Receiver
            udt_send(sndpkt[senderSeqNum])

            # Start timer for the oldest on-flight packet
            if sendBase == senderSeqNum:
                timer = start_timer()
            
            # Increment senderSeqNum by 1 since we just sent a packet
            senderSeqNum += 1
        
        # Event: Receive packet from Receiver
        rcvpkt = udt_rcv()[0]
        if rcvpkt:
            receivedSynBit, receivedAckBit, receivedFinBit, seqNum, ackNum, checksum, payload = decompose_pkt(rcvpkt)
            if not is_corrupted(payload, checksum):
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
                        
            # Retransmit N packets (i.e. all packets in the Sender window)
            for i in range(sendBase, senderSeqNum):
                udt_send(sndpkt[i])
                
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
    
    # Sender SYN, ACK and FIN flag bits
    synBit, ackBit, finBit = 0, 0, 0
    
    pktFormat = '!BBBIII'
    
    # Any packet (segment with header) that is sent by Sender will be added to sndpkt
    # sndpkt is used for retransmitting unacknowledged packets upon timeout of the timer
    sndpkt = {}
    
    # Initialization of Sender seq num and ack num
    # Assume senderSeqNum = Y, senderAckNum = 0
    senderSeqNum = generate_random_initial_sequence_number()
    senderAckNum = 0
     
    # ------------------------------------  Basic Setup  ------------------------------------ 
    
    # Get global values from sys.argv
    senderIPAddress, senderPortNumber, filename1, filename2 = setup_arguments()
    
    # Initialize Receiver IP and port number
    receiverIPAddress, receiverPortNumber = '', 0
    
    # Create Sender UDP socket
    UDPSocket = create_udp_socket()
    
    # Bind Sender IP and port to the UDP socket
    bind_socket_to_address_and_port()
    
    # Get the size of input file
    try:
        fileSize = get_file_size(filename1)
    except FileNotFoundError as e:
        print('Error: %s - %s.' % (e.filename, e.strerror))
        exit(0)
    
    # Read byte message of content from input file
    fileContent = read_file_content(filename1)
    
    # ------------------------------------  Handshake  ------------------------------------ 
    
    # Before performing three-way handshake:
    #   senderSeqNum should be Y
    #   senderAckNum should be 0
    print('senderSeqNum:', senderSeqNum)
    print(f'senderAckNum: {senderAckNum} \n')
    
    # Perform handshake with Receiver
    perform_three_way_handshake()
    
    # After performing three-way handshake:
    #   senderSeqNum should be Y + 1
    #   senderAckNum should be X + 1, where X is Receiver's seq num
    print(f'\nsenderSeqNum: {senderSeqNum}')
    print(f'senderAckNum: {senderAckNum} \n')
    
    # ------------------------------------  Sender Operation  ------------------------------------ 
    
    # Sender send base
    sendBase = senderSeqNum
    # Sender window size N=16
    senderWindowSize = 16
    
    perform_sender_operation()
    
    # Close UDP socket
    UDPSocket.close()
    
    # Print out the amount of time used for executing this program
    endTime = time.time()
    print('Time lapsed in seconds: {:0.2f}'.format(endTime - startTime))
