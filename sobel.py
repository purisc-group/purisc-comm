import numpy as np
from subprocess import *
import getopt, sys
import struct
from kernel import Kernel

def main(argv):
    compilerPath, kernelName = parseInput(argv);

    kernel = Kernel(compilerPath, kernelName);
    kernel.compile();

    
    inn = np.zeros([10,20]);
    inn = 100*inn;
    out = np.zeros([10,20]);

    kernel.setArg(0,inn);
    kernel.setOutput(1,out);

    kernel.enqueue(2,[0,0],[10,20]);


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
