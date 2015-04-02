from copy import deepcopy as copy
import sys
import numpy as np
from subprocess import *
from argument import Argument
from subprocess import Popen, PIPE 

GLOB_MEM_LENGTH = 32*1024;
GLOB_MEM_OFFSET = 8*1024;

class Kernel:

    def __init__(self, compilerPath, kernelName):
        self.compilerPath = compilerPath;
        self.kernelName = kernelName;

    def compile(self):
        call(["python", self.compilerPath + "/compiler.py","-i", self.kernelName]); #call the compiler
        self.localMemory, self.indexLocations, self.indexMaxLocations, args, self.dimLocations, self.flagLocations = readDataFromFile(getNakedName(self.kernelName));
        
        self.arguments = [];
        for i in range(0,len(args)):
            self.arguments.append(Argument(args[i]));
        
    def setArg(self, num, data):
        if num >= len(self.arguments) or num < 0:
            print "error - invalid argument number, max args are: " + self.argLen
            sys.exit(2);

        self.arguments[num].data = data;

    def setOutput(self, num, data):
        if num > len(self.arguments) or num < 0:
            print 'error - invalid argument number, max args are: ' + self.argLen
            sys.exit(2);

        elif hasattr(self.arguments[num], 'data'):
            print 'error - trying to set an input arg as the output!';
            sys.exit(2);

        else:
            self.output = num;
            self.outputLen = len(np.reshape(data,np.size(data)));

    def enqueue(self, dim, offset, size):
        if dim > 11:
            print "error - limit of 11 dimension"
            sys.exit(2);

        globalMemory = np.zeros(GLOB_MEM_LENGTH, dtype=np.int);
        globalMemory[8] = self.outputLen;

        startIndicies = np.zeros([dim,8], dtype=np.int);
        endIndicies = np.zeros([dim,8], dtype=np.int);

        for i in range(0,dim):
            for core in range(0,8):
                 startIndicies[i][core] = offset[i] + core*size[i]/8;
                 endIndicies[i][core] = offset[i] + (core+1)*size[i]/8;

        nextGlobal = 10;
        for i,arg in enumerate(self.arguments):
            if arg.argType == 0: #local arguments
                self.localMemory[arg.location1] = arg.data;
                self.localMemory[arg.location2] = arg.data;

            else: #global arguments
                self.localMemory[arg.location1] = nextGlobal;
                self.localMemory[arg.location2] = nextGlobal;

                if hasattr(arg, 'data'):
                    lin = np.reshape(arg.data,np.size(arg.data));
                    for i in range(0, len(lin)):
                        globalMemory[nextGlobal] = lin[i];
                        nextGlobal += 1;
                elif i == self.output:
                    globalMemory[9] = nextGlobal;
                    nextGlobal += self.outputLen;

        p = Popen(["python","purisc_io_noarq.py"], stdin=PIPE, stdout=PIPE);
        dataBufferArr = [];


        for cg in range(0,4): #for each compute group
            localmem = copy(self.localMemory);
            for i in range(0,dim):
                localmem[self.indexLocations[i][0]] = startIndicies[i][cg*2];
                localmem[self.indexLocations[i][1]] = startIndicies[i][cg*2+1];
                localmem[self.indexMaxLocations[i][0]] = endIndicies[i][cg*2];
                localmem[self.indexMaxLocations[i][1]] = endIndicies[i][cg*2+1];
                localmem[int(self.dimLocations[0])] = dim;
                localmem[int(self.dimLocations[1])] = dim;

            localmem[int(self.flagLocations[0])] = cg*2;
            localmem[int(self.flagLocations[1])] = cg*2 + 1;

            dataBufferArr.append(str(len(localmem)));
            if cg == 2:
                for dat in localmem:
                    dataBufferArr.append(str(dat));
                    print dat


        dataBufferArr.append(str(len(globalMemory)));
        for dat in globalMemory:
            dataBufferArr.append(str(dat));

        dataBuff = '\n'.join(dataBufferArr);
        
        retStr =  p.communicate(dataBuff)[0];
        retBuff = retStr.split("\n");

        output = np.zeros(len(retBuff),np.int);
        for i,val in enumerate(retBuff):
            output[i] = int(val);

        return output;



#opens the compiled machine code and request files
#creates arrays for the localmem (compiled machine code), index locations
#max index locations and arguments
def readDataFromFile(kernelName):
    inFile = kernelName;
    machineCode = open(inFile + ".machine");

    localMem = np.zeros([8*1024], dtype=np.int)
    for i,line in enumerate(machineCode):
        localMem[i] = int(line);

    machineCode.close()

    requestFile = open(inFile + ".request");
    argLen = int(requestFile.readline().strip());

    dimLocations = requestFile.readline().strip().split(",");

    indexLocations = np.zeros([11,2],dtype=np.int);
    for i in range(0,11):
        indexLocations[i] = requestFile.readline().strip().split(",");

    indexMaxLocations = np.zeros([11,2],dtype=np.int);
    for i in range(0,11):
        indexMaxLocations[i] = requestFile.readline().strip().split(",");

    args = np.zeros([argLen,3],dtype=np.int);
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

    flagLocations = requestFile.readline().strip().split(",");

    requestFile.close();

    return localMem, indexLocations, indexMaxLocations, args, dimLocations, flagLocations


def getNakedName(kernelName):
    idx = kernelName.rindex(".");
    return kernelName[:idx]

