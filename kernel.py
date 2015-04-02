from copy import deepcopy as copy
import sys
import numpy as np
from subprocess import *
from argument import Argument
from subprocess import Popen, PIPE 

class Kernel:

    def __init__(self, compilerPath, kernelName):
        self.compilerPath = compilerPath;
        self.kernelName = kernelName;
        self.globMem = 10*1024;
        self.globMemOffset = 8*2014;

    def compile(self):
        call(["python", self.compilerPath + "/compiler.py","-i", self.kernelName]); #call the compiler
        self.localMemory, self.indexLocations, self.indexMaxLocations, args, self.dimLocations = readDataFromFile(getNakedName(self.kernelName));
        
        self.arguments = [];
        for i in range(0,len(args)):
            self.arguments.append(Argument(args[i]));
        
    def setArg(self, num, data):
        if num >= len(self.arguments) or num < 0:
            print "error - invalid argument number, max args are: " + self.argLen
            sys.exit(2);

        self.arguments[num].data = data;

    def enqueue(self, dim, offset, size):
        if dim > 11:
            print "error - limit of 11 dimension"
            sys.exit(2);

        globalMemory = np.zeros(self.globMem);

        startIndicies = np.zeros([dim,8]);
        endIndicies = np.zeros([dim,8]);

        for i in range(0,dim):
            for core in range(0,8):
                 startIndicies[i][core] = offset[i] + core*size[i]/8;
                 endIndicies[i][core] = offset[i] + (core+1)*size[i]/8;

        nextGlobal = 0;
        for arg in self.arguments:
            if arg.argType == 0: #local arguments
                self.localMemory[arg.location1] = arg.data;
                self.localMemory[arg.location2] = arg.data;

            else: #global arguments
                self.localMemory[arg.location1] = nextGlobal;
                self.localMemory[arg.location2] = nextGlobal;

                lin = np.reshape(arg.data,np.size(arg.data));
                for i in range(0, len(lin)):
                    globalMemory[nextGlobal] = lin[i];
                

        # sendData(globalmemory)
        sendData(globalMemory);

        for cg in range(0,4): #for each compute group
            localmem = copy(self.localMemory);
            for i in range(0,dim):
                localmem[self.indexLocations[i][0]] = startIndicies[i][cg*2];
                localmem[self.indexLocations[i][1]] = startIndicies[i][cg*2+1];
                localmem[self.indexMaxLocations[i][0]] = endIndicies[i][cg*2];
                localmem[self.indexMaxLocations[i][1]] = endIndicies[i][cg*2+1];

            #sendData(localmem)
            print localmem


#opens the compiled machine code and request files
#creates arrays for the localmem (compiled machine code), index locations
#max index locations and arguments
def readDataFromFile(kernelName):
    inFile = kernelName;
    machineCode = open(inFile + ".machine");

    localMem = np.zeros([8*1024])
    for i,line in enumerate(machineCode):
        localMem[i] = int(line);

    machineCode.close()

    requestFile = open(inFile + ".request");
    argLen = int(requestFile.readline().strip());

    dimLocations = requestFile.readline().strip().split(",");

    indexLocations = np.zeros([11,2]);
    for i in range(0,11):
        indexLocations[i] = requestFile.readline().strip().split(",");

    indexMaxLocations = np.zeros([11,2]);
    for i in range(0,11):
        indexMaxLocations[i] = requestFile.readline().strip().split(",");

    args = np.zeros([argLen,3]);
    for i in range(0,argLen):
        arg = requestFile.readline().strip();
        arg1,arg2 = arg.split(",");
        if "*" in arg:
            args[i][0] = arg1[:-1];
            args[i][1] = arg2[:-1];
            args[i][2] = 1;

        else:
            args[i][0] = arg1;
            args[i][1] = arg2;
            args[i][2] = 1;

    requestFile.close();

    return localMem, indexLocations, indexMaxLocations, args, dimLocations


def getNakedName(kernelName):
    idx = kernelName.rindex(".");
    return kernelName[:idx]

def sendData(data):

    p = Popen(["python","purisc_io.py"], stdin=PIPE);

    dataBufferArr = [];

    for dat in data:
        dataBufferArr.append(str(dat));

    dataBuff = '\n'.join(dataBufferArr);

    p.communicate(dataBuff);



def encode(num):

    hexStr = hex(num)[2:]; #strip off the '0x'

    while len(hexStr) < 4:
        hexStr = "0" + hexStr;

    hi = hexStr[:2];
    hiInt = int(hi,16);

    low = hexStr[2:];
    lowInt = int(low,16);

    return chr(hiInt) + chr(lowInt);
