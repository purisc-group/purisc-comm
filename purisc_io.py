from socket import socket, AF_PACKET, SOCK_RAW

import getopt
import sys

def main(argv):
    print "Opening..."
    infileStr = parseInput(argv);

    if infileStr == '':
        infile = sys.stdin;
    else:
        infile = open(infileStr, 'w');

    sock = socket(AF_PACKET, SOCK_RAW)
    sock.bind(("eth0", 0))
            
    for i in range(0,5):

        mem_id = chr(0)+chr(int(i));
        packet_data = []; 

        length = int(infile.readline());
        for i in range(0, length):
            data = int(infile.readline());
            if data < 0:
                data = 0xffff + data;

            packet_data.append(encode(data,4)); 

        dataToSend = "".join(packet_data);
        n = len(dataToSend)/1024 + (len(dataToSend) % 1024 > 0);
        goBack = n;
        while goBack > 0: 
            send(dataToSend, mem_id, sock, goBack);
            resp = recv(sock);
            goBack = int(resp[:2]);

        #receive result

def recvData(sock):
    message = '';
    while len(message) < 1024:
        message += sock.recv(1024);

    return message;

def recvArq(sock):
    message = '';
    while len(message) < 64:
        message += sock.recv(64);

    return message;


def send(dataToSend, mem_id, sock, goBack):

    #determine length
    length_total = len(dataToSend)
    total_packs = length_total/1024 + (length_total % 1024 > 0);
    
    startnum = total_packs - goBack;
    packet_cnt = encode(goBack,2);


    for iteration in range(0,total_packs):

            packet_num = encode(iteration,2);

            start = startnum*1024 + iteration*1024
            end = start + 1024
            if iteration == (total_packs - 1):
                end = len(dataToSend);

            packet_to_send = dataToSend[start:end];
            length = encode(len(packet_to_send),2);
            print len(packet_to_send)

            aTalk = encode(0x809B,2);
            ppType = encode(01,2);
             
            #print dst_addr+src_addr+aTalk+ppType+length+mem_id+packet_num+packet_cnt+packet_to_send
            sock.send(dst_addr+src_addr+aTalk+ppType+length+mem_id+packet_num+packet_cnt+packet_to_send);

            print "\n SENT packet %d to CG0" %iteration
    
#encode integer to a byte in bigendian
def encode(num, nbytes):

    hexStr = hex(num)[2:]; #strip off the '0x'
    
    while len(hexStr) < 2*nbytes:
        hexStr = "0" + hexStr;

    arr = [];
    for i in range(0,nbytes):
        num = int(hexStr[i*2:(i+1)*2],16);
        arr.append(chr(num));

    return ''.join(arr);
    

def parseInput(argv):
    infile = '';

    try:
        opts, args = getopt.getopt(argv, "i:h")
    except getopt.GetoptError:
        print usage();
        sys.exit(2);

    for opt, arg in opts:
        if opt in ("-i", "--file"):
            infile = arg;

        elif opt in ("-h", "--help"):
            print usage();
            sys.exit(0);

    return infile;

def usage():
    return "python " + sys.argv[0] + " [-i <infile>]";


dst_addr = 'PURISC';
src_addr = 'HOSTPC';

if __name__ == '__main__':
    main(sys.argv[1:]);
