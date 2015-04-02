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


            
    for i in range(0,5):

        mem_id = chr(0)+chr(int(i));
        packet_data = []; 

        length = int(infile.readline());
        for i in range(0, length):
            data = int(infile.readline());
            if data < 0:
                data = 0xffff + data;

            packet_data.append(encode(data)); 

        dataToSend = "".join(packet_data);
        send(dataToSend, mem_id);


def send(dataToSend, mem_id):

    #determine length
    length_total = len(dataToSend)
    total_packs = length_total/1000 + (length_total % 1000 > 0);
    packet_cnt = encode(total_packs);

    #send packets
    sock = socket(AF_PACKET, SOCK_RAW)
    sock.bind(("eth0", 0))

    for iteration in range(0,total_packs):

            packet_num = encode(iteration);

            start = iteration*1000
            end = start + 1000
            if iteration == (total_packs - 1):
                end = len(dataToSend);

            packet_to_send = dataToSend[start:end];
            length = encode(len(packet_to_send));

            sock.send(dst_addr+src_addr+length+mem_id+packet_num+packet_cnt+packet_to_send)

            print "\n SENT packet %d to CG0" %iteration
    
#encode integer to a byte in bigendian
def encode(num):

    hexStr = hex(num)[2:]; #strip off the '0x'
    
    while len(hexStr) < 4:
        hexStr = "0" + hexStr;

    hi = hexStr[:2];
    hiInt = int(hi,16);
    
    low = hexStr[2:];
    lowInt = int(low,16);

    return chr(hiInt) + chr(lowInt);
    

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


#dst_addr=chr(0x50)+chr(0x55)+chr(0x52)+chr(0x49)+chr(0x53)+chr(0x43)
#src_addr=chr(0x48)+chr(0x4F)+chr(0x53)+chr(0x54)+chr(0x50)+chr(0x43)
dst_addr = 'PURISC';
src_addr = 'HOSTPC';

if __name__ == '__main__':
    main(sys.argv[1:]);
