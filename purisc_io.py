from socket import socket, AF_PACKET, SOCK_RAW
import getopt
import sys

def main(argv):
    infileStr = parseInput(argv);

    if infileStr == '':
        infile = sys.stdin;
    else:
        infile = open(infileStr, 'w');


    #dst_addr=chr(0x50)+chr(0x55)+chr(0x52)+chr(0x49)+chr(0x53)+chr(0x43)
    #src_addr=chr(0x48)+chr(0x4F)+chr(0x53)+chr(0x54)+chr(0x50)+chr(0x43)
    dst_addr = 'PURISC';
    src_addr = 'HOSTPC';
    mem_id_0 = 0x00
    mem_id_1 = 0x01
    mem_id = chr(mem_id_0)+chr(mem_id_1)	
            

    #read packet data
    packet_data = []; 

    for line in infile:
        print line;
        data = int(line.strip())
        if data < 0:
            hex_dat = 0xffff + data;

        packet_data.append(encode(hex_dat)); 

    print packet_data;

    #determine length
    length_total = len(packet_data)
    total_packs = length_total/1000 + (length_total % 1000 > 0);
    packet_cnt = encode(total_packs);

    #send packets
    sock = socket(AF_PACKET, SOCK_RAW)
    sock.bind(("eth0", 0))

    for iteration in range(0,number_of_packs):

            packet_num = encode(iteration);

            start = iteration*1000
            end = start + 1000
            if (iteration < number_of_packs):
                    packet_to_send = packet_data[start:end]
                    length = 1000;
            
            else:
                    packet_to_send = packet_data[start:]
                    length = len(packet_to_send);

            length = encode(length);

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

if __name__ == '__main__':
    main(sys.argv[1:]);
