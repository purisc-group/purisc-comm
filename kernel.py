from copy import deepcopy as copy
import sys
import numpy as np
from subprocess import *
from argument import Argument

class Kernel:

    def __init__(self, compilerPath, kernelName):
        self.compilerPath = compilerPath;
        self.kernelName = kernelName;

    def compile(self):
        call(["python", self.compilerPath + "/compiler.py","-i", self.kernelName]); #call the compiler
        self.localMemory, self.indexLocations, self.indexMaxLocations, args = readDataFromFile(getNakedName(self.kernelName));
        
        self.arguments = [];
        for i in range(0,len(args)):
            self.arguments.append(Argument(args[i]));
        
    """def __init__(self, localMemory, indexLocations, indexMaxLocations, argumentLocations, globMem=8*1024, globMemOffset=8*1024):
        self.localmemory = copy(localMemory);
        self.indexLocations = copy(indexLocations);
        self.indexMaxLocations = copy(indexMaxLocations);

        self.arguments = [];
        for i in range(0,len(argumentLocations)):
            self.arguments.append(Argument(argumentLocations[i]));

        self.argLen = len(self.arguments);
        self.globalmemory = [];
        self.globMem = globMem;
        self.globMemOffset = globMemOffset;"""


    def setArg(self, num, data):
        if num >= self.argLen or num < 0:
            print "error - invalid argument number, max args are: " + self.argLen
            sys.exit(2);

        self.arguments[num].data = data;

    def enqueue(dim, offset, size):
        if dim > 11:
            print "error - limit of 11 dimension"
            sys.exit(2);

        startIndicies = zeros([dim,8]);
        endIndicies = zeros([dim,8]);

        for i in range(0,dim):
            for core in range(0,8):
                 startIndicies[core][dim] = offset[i] + core*size[i]/8;
                 endIndicies[core][dim] = offset[i] + (core+1)*size[i]/8;

        nextGlobal = self.globMemOffset;
        for arg in self.arguments:
            if arg.argType == 0: #local arguments
                self.localmemory[arg.location1] = arg.data;
                self.localmemory[arg.location2] = arg.data;

            else: #global arguments
                self.localmemory[arg.location1] = nextGlobal;
                self.localmemory[arg.location2] = nextGlobal;
                
                for i in range(0,len(arg.data)):
                    self.globalmemory[arg.nextGlobal] = arg.data[i];
                    nextGlobal += 1;

        # sendData(globalmemory)
        print globalmemory

        for cg in range(0,4): #for each compute group
            localmem = copy(localmemory);
            for i in range(0,dim):
                localmem[indexLocation[i][0]] = startIndicies[cg*2][i];
                localmem[indexLocation[i][1]] = startIndicies[cg*2+1][i];
                localmem[indexMaxLocations[i][0]] = endIndicies[cg*2][i];
                localmem[indexMaxLocations[i][1]] = endIndicies[cg*2+1][i];

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

    return localMem, indexLocations, indexMaxLocations, args


def getNakedName(kernelName):
    idx = kernelName.rindex(".");
    return kernelName[:idx]
