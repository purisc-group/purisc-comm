import numpy as np
from subprocess import *
import getopt, sys
import struct
from kernel import Kernel

def main(argv):
    compilerPath, kernelName = parseInput(argv);

    kernel = Kernel(compilerPath, kernelName);
    kernel.compile();

    mem = kernel.arguments;
    for i in range(0,len(mem)):
        print mem[i].location1, mem[i].location2, mem[i].argType;
    
    inn = np.zeros([1,100]);
    inn = 100*inn;


def parseInput(argv): 
    compilerPath = "";
    kernelName = "";

#Command line arguments
    try:
        opts, args = getopt.getopt(argv, "c:i:")
    except getopt.GetoptError:
        print usage(); 
        sys.exit(2);

    for opt, arg in opts:
        if opt in ("-c", "--compiler"):
            compilerPath = arg;
        
        elif opt in ("-i", "--kernel"):
            kernelName = arg;

    return compilerPath, kernelName;

def usage():
    return "python " + sys.argv[0] + " -c <compiler-path>"

if __name__ == '__main__':
    main(sys.argv[1:])
