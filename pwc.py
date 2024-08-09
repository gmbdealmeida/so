import sys, os, signal, time, pickle
from multiprocessing import Process, Value, Array, Lock
from datetime import datetime

start = datetime.now()
start.time()

startTime = time.time()

startExecutionDateTime = datetime.now().strftime("%d/%B/%Y, %H:%M:%S:%f")


args = sys.argv[1:]
command = []
optional = []
previousArg = ""
numProcesses = 1
timeInterval = 0
binaryFileName = ""
files = []
mutex = Lock()


for i in range(len(args)):
    if args[i] == "-c" or args[i] == "-w" \
       or args[i] == "-l" or args[i] == "-L":
        command.append(args[i])

    elif args[i] == "-f" or args[i] == "-a":
        optional.append(args[i])

    elif previousArg == "-p":
        try:
            numProcesses = int(args[i])
        except ValueError:
            raise ValueError("O número de processos não é um inteiro.")

    elif previousArg == "-a":
        try:
            timeInterval = int(args[i])
        except ValueError:
            raise ValueError("O intervalo de tempo não é um inteiro.")

    elif previousArg == "-f":
        binaryFileName = args[i]

    elif args[i] == "-p" or args[i] == "-a" or args[i] == "-f":
        pass

    else:
        files.append(args[i])
        
    previousArg = args[i]

    
if len(command) == 0:
    raise ValueError("Não foi inserido qualquer comando.")

elif len(command) > 1:
    if command[0] != "-l" or command[1] != "-L":
        raise ValueError("O comando inserido não é válido.")

    elif len(command) > 2:
        raise ValueError("O comando inserido não é válido.")

elif command[0] != "-c" and command[0] != "-w" and command[0] != "-l":
    raise ValueError("O comando inserido não é válido.")

#Verifica se foram passados ficheiros na linha de comandos
#Em caso negativo, lê-os a partir de stdin
if len(files) == 0:
    files = sys.stdin.readline().split(" ")
    #Retira o caracter "\n" resultante da introdução de ficheiros através de stdin
    files[-1] = files[-1].strip()

for file in files:
    try:
        open(file, "r")
    except:
        raise FileNotFoundError("O ficheiro " + file + " não foi encontrado.")
    

def interrupt(sig, NULL):
    interruptState.value = 1


def current(sig, NULL):
    currentTime = time.time()
    timePassed = (currentTime - startTime) * 1000000
    
    if "-c" in command:
        print("Número total de caracteres contados até ao momento: " + str(totalSum.value) + ".")

    elif "-w" in command:
        print("Número total de palavras contadas até ao momento: " + str(totalSum.value) + ".")

    else:
        print("Número total de linhas contadas até ao momento: " + str(totalSum.value) + ".")

    print("Número total de ficheiros processados até ao momento: " + str(numFilesCounted.value) + ".")
    print("Tempo decorrido desde o começo do programa em micro-segundos: " + str(timePassed) + ".\n")


signal.signal(signal.SIGINT, interrupt)

if "-a" in optional:
    signal.signal(signal.SIGALRM, current)
    signal.setitimer(signal.ITIMER_REAL, timeInterval, timeInterval)


def otherFilesWC(processFile, originalFile, processPosition):
    processRunTime = time.time()
    numCounted = 0
    
    with open(processFile, "r") as file:
        if "-c" in command:
            for line in file:
                encodedLine = bytes(line, encoding = "utf-8")
                numCounted = numCounted + len(encodedLine)
                mutex.acquire()
                totalSum.value = totalSum.value + len(encodedLine)
                mutex.release()

            mutex.acquire()
            print("O processo " + str(os.getpid()) + " leu o ficheiro " + originalFile\
                  + " e contou " + str(numCounted) + " caracteres.")
            processesIDOrder[numFilesCounted.value] = os.getpid()
            runTime = time.time()
            processesRunTime[numFilesCounted.value] = runTime - processRunTime
            filesDimensions[numFilesCounted.value] = os.path.getsize(originalFile)
            filesCounts[numFilesCounted.value] = numCounted
                
            for j in range(len(files)):
                if(i == files[j]):
                    fileCountOrder[numFilesCounted.value] = j
                    
            numFilesCounted.value = numFilesCounted.value + 1
            mutex.release()
            

        elif "-w" in command:
            for line in file:
                splittedLine = line.split()
                numCounted = numCounted + len(splittedLine)
                mutex.acquire()
                totalSum.value = totalSum.value + len(splittedLine)
                mutex.release()

            mutex.acquire()
            print("O processo " + str(os.getpid()) + " leu o ficheiro " + originalFile\
                  + " e contou " + str(numCounted) + " palavras.")
            processesIDOrder[numFilesCounted.value] = os.getpid()
            runTime = time.time()
            processesRunTime[numFilesCounted.value] = runTime - processRunTime
            filesDimensions[numFilesCounted.value] = os.path.getsize(originalFile)
            filesCounts[numFilesCounted.value] = numCounted
                
            for j in range(len(files)):
                if(i == files[j]):
                    fileCountOrder[numFilesCounted.value] = j
                    
            numFilesCounted.value = numFilesCounted.value + 1
            mutex.release()

        elif "-l" in command and "-L" in command:
            mostChars = 0

            for line in file:
                rStrippedLine = line.rstrip()
                lineChars = len(rStrippedLine)

                if "\n" in line:
                    numCounted = numCounted + 1
                    mutex.acquire()
                    totalSum.value = totalSum.value + 1
                    mutex.release()

                if lineChars > mostChars:
                    mostChars = lineChars

            mutex.acquire()
            print("O processo " + str(os.getpid()) + " leu o ficheiro " + originalFile\
                  + " e contou " + str(numCounted) + " linhas. Das linhas que contou a"\
                  + " maior linha continha " + str(mostChars) + " caracteres.")
            processesIDOrder[numFilesCounted.value] = os.getpid()
            runTime = time.time()
            processesRunTime[numFilesCounted.value] = runTime - processRunTime
            filesDimensions[numFilesCounted.value] = os.path.getsize(originalFile)
            filesCounts[numFilesCounted.value] = numCounted
                
            for j in range(len(files)):
                if(i == files[j]):
                    fileCountOrder[numFilesCounted.value] = j
                    
            numFilesCounted.value = numFilesCounted.value + 1
            mutex.release()

        else:
            for line in file:
                if "\n" in line:
                    numCounted = numCounted + 1
                    mutex.acquire()
                    totalSum.value = totalSum.value + 1
                    mutex.release()
                    
            mutex.acquire()
            print("O processo " + str(os.getpid()) + " leu o ficheiro " + originalFile\
                  + " e contou " + str(numCounted) + " linhas.")
            processesIDOrder[numFilesCounted.value] = os.getpid()
            runTime = time.time()
            processesRunTime[numFilesCounted.value] = runTime - processRunTime
            filesDimensions[numFilesCounted.value] = os.path.getsize(originalFile)
            filesCounts[numFilesCounted.value] = numCounted
                
            for j in range(len(files)):
                if(i == files[j]):
                    fileCountOrder[numFilesCounted.value] = j
                    
            numFilesCounted.value = numFilesCounted.value + 1
            mutex.release()
            

def filesWC(processFiles, processPosition):
    for i in processFiles:
        if interruptState.value == 1:
            return

        processRunTime = time.time()
        numCounted = 0
        
        with open(i, "r") as file:
            if "-c" in command:
                for line in file:
                    encodedLine = bytes(line, encoding = "utf-8")
                    numCounted = numCounted + len(encodedLine)
                    mutex.acquire()
                    totalSum.value = totalSum.value + len(encodedLine)
                    mutex.release()

                mutex.acquire()
                print("O processo " + str(os.getpid()) + " leu o ficheiro " + i\
                      + " e determinou que este tem " + str(numCounted) + " caracteres.")
                processesIDOrder[numFilesCounted.value] = os.getpid()
                runTime = time.time()
                processesRunTime[numFilesCounted.value] = runTime - processRunTime
                filesDimensions[numFilesCounted.value] = os.path.getsize(i)
                filesCounts[numFilesCounted.value] = numCounted
                
                for j in range(len(files)):
                    if(i == files[j]):
                        fileCountOrder[numFilesCounted.value] = j
       
                numFilesCounted.value = numFilesCounted.value + 1
                mutex.release()

            elif "-w" in command:
                for line in file:
                    splittedLine = line.split()
                    numCounted = numCounted + len(splittedLine)
                    mutex.acquire()
                    totalSum.value = totalSum.value + len(splittedLine)
                    mutex.release()

                mutex.acquire()
                print("O processo " + str(os.getpid()) + " leu o ficheiro " + i\
                      + " e determinou que este tem " + str(numCounted) + " palavras.")
                processesIDOrder[numFilesCounted.value] = os.getpid()
                runTime = time.time()
                processesRunTime[numFilesCounted.value] = runTime - processRunTime
                filesDimensions[numFilesCounted.value] = os.path.getsize(i)
                filesCounts[numFilesCounted.value] = numCounted
                
                for j in range(len(files)):
                    if(i == files[j]):
                        fileCountOrder[numFilesCounted.value] = j
       
                numFilesCounted.value = numFilesCounted.value + 1
                mutex.release()

            elif "-l" in command and "-L" in command:
                mostChars = 0

                for line in file:
                    rStrippedLine = line.rstrip()
                    lineChars = len(rStrippedLine)

                    if "\n" in line:
                        numCounted = numCounted + 1
                        mutex.acquire()
                        totalSum.value = totalSum.value + 1
                        mutex.release()

                    if lineChars > mostChars:
                        mostChars = lineChars

                mutex.acquire()
                print("O processo " + str(os.getpid()) + " leu o ficheiro " + i\
                      + " e determinou que este tem " + str(numCounted)\
                      + " e que a maior linha contém " + str(mostChars) + " caracteres.")
                processesIDOrder[numFilesCounted.value] = os.getpid()
                runTime = time.time()
                processesRunTime[numFilesCounted.value] = runTime - processRunTime
                filesDimensions[numFilesCounted.value] = os.path.getsize(i)
                filesCounts[numFilesCounted.value] = numCounted
                
                for j in range(len(files)):
                    if(i == files[j]):
                        fileCountOrder[numFilesCounted.value] = j
       
                numFilesCounted.value = numFilesCounted.value + 1
                mutex.release()

            else:
                for line in file:
                    if "\n" in line:
                        numCounted = numCounted + 1
                        mutex.acquire()
                        totalSum.value = totalSum.value + 1
                        mutex.release()
                        
                mutex.acquire()
                print("O processo " + str(os.getpid()) + " leu o ficheiro " + i\
                      + " e determinou que este tem " + str(numCounted) + " linhas.")
                processesIDOrder[numFilesCounted.value] = os.getpid()
                runTime = time.time()
                processesRunTime[numFilesCounted.value] = runTime - processRunTime
                filesDimensions[numFilesCounted.value] = os.path.getsize(i)
                filesCounts[numFilesCounted.value] = numCounted
                
                for j in range(len(files)):
                    if(i == files[j]):
                        fileCountOrder[numFilesCounted.value] = j
       
                numFilesCounted.value = numFilesCounted.value + 1
                mutex.release()
                

totalSum = Value("i", 0)
interruptState = Value("i", 0)
numFilesCounted = Value("i", 0)

if numProcesses > len(files):
    processesIDOrder = Array("i", numProcesses)
    processesRunTime = Array("f", numProcesses)
    filesDimensions = Array("i", numProcesses)
    filesCounts = Array("i", numProcesses)
    fileCountOrder = Array("i", numProcesses)

else:                            
    processesIDOrder = Array("i", len(files))
    processesRunTime = Array("f", len(files))
    filesDimensions = Array("i", len(files))
    filesCounts = Array("i", len(files))
    fileCountOrder = Array("i", len(files))
    
    
processes = []


if numProcesses != 0:
    if numProcesses > len(files):
        numProcessesPerFile = numProcesses // len(files)
        equalitarian = numProcesses % len(files)
        currentProcess = 0
        createdFiles = []

        for i in range(len(files)):
            if equalitarian > 0:
                thisFileNumProcesses = numProcessesPerFile + 1
                equalitarian = equalitarian - 1
                currentPosition = 0

                with open(files[i], "r") as originalFile:
                    originalFileText = originalFile.readlines()

                numLinesPerProcess = len(originalFileText) // thisFileNumProcesses
                lineEqualitarian = len(originalFileText) // thisFileNumProcesses

                for j in range(thisFileNumProcesses):
                    newFileName = "file" + str(i) + str(j) + ".txt"

                    if lineEqualitarian > 0:
                        thisProcessNumLines = numLinesPerProcess + 1
                        
                        textToWrite = originalFileText[currentPosition:\
                                                       currentPosition + thisProcessNumLines]
                        currentPosition = currentPosition + thisProcessNumLines

                        with open(newFileName, "w") as newFile:
                            for lineOfText in textToWrite:
                                newFile.write(lineOfText)

                        createdFiles.append(newFileName)

                        lineEqualitarian = lineEqualitarian - 1


                    else:
                        thisProcessNumLines = numLinesPerProcess

                        textToWrite = originalFileText[currentPosition:\
                                                       currentPosition + thisProcessNumLines]
                        currentPosition = currentPosition + thisProcessNumLines

                        with open(newFileName, "w") as newFile:
                            for lineOfText in textToWrite:
                                newFile.write(lineOfText)

                        createdFiles.append(newFileName)

                    newP = Process(target = otherFilesWC, \
                                   args = (newFileName, files[i], currentProcess))
                    processes.append(newP)
                    currentProcess = currentProcess + 1

            else:
                thisFileNumProcesses = numProcessesPerFile
                currentPosition = 0

                with open(files[i], "r") as originalFile:
                    originalFileText = originalFile.readlines()
                
                numLinesPerProcess = len(originalFileText) // thisFileNumProcesses
                lineEqualitarian = len(originalFileText) % thisFileNumProcesses

                for j in range(thisFileNumProcesses):
                    newFileName = "file" + str(i) + str(j) + ".txt"

                    if lineEqualitarian > 0:
                        thisProcessNumLines = numLinesPerProcess + 1
                        
                        textToWrite = originalFileText[currentPosition:\
                                                       currentPosition + thisProcessNumLines]
                        currentPosition = currentPosition + thisProcessNumLines
                        
                        with open(newFileName, "w") as newFile:
                            for lineOfText in textToWrite:
                                newFile.write(lineOfText)

                        createdFiles.append(newFileName)
                                
                        lineEqualitarian = lineEqualitarian - 1



                    else:
                        thisProcessNumLines = numLinesPerProcess

                        textToWrite = originalFileText[currentPosition:\
                                                       currentPosition + thisProcessNumLines]
                        currentPosition = currentPosition + thisProcessNumLines
                        
                        with open(newFileName, "w") as newFile:
                            for lineOfText in textToWrite:
                                newFile.write(lineOfText)

                        createdFiles.append(newFileName)
                                
                    newP = Process(target = otherFilesWC, \
                                   args = (newFileName, files[i], currentProcess))
                    processes.append(newP)
                    currentProcess = currentProcess + 1
                  
    else:
        numFilesPerProcess = len(files) // numProcesses
        equalitarian = len(files) % numProcesses
        currentFilesBatch = 0
        
        for i in range(numProcesses):
            if equalitarian > 0:
                #Determina que ficheiros é que o processo que vai ser criado vai contar
                thisProcessNumFiles = numFilesPerProcess + 1
                thisProcessFiles = files[currentFilesBatch:\
                                         currentFilesBatch + thisProcessNumFiles]
                currentFilesBatch = currentFilesBatch + thisProcessNumFiles
                equalitarian = equalitarian - 1
                #Cria o processo passando como argumento a lista de ficheiros que
                #se determinou no passo anterior
                newP = Process(target = filesWC, args = (thisProcessFiles, i))
                processes.append(newP)
                
            else:
                #Determina que ficheiros é que o processo que vai ser criado vai contar
                thisProcessNumFiles = numFilesPerProcess
                thisProcessFiles = files[currentFilesBatch:\
                                         currentFilesBatch + thisProcessNumFiles]
                currentFilesBatch = currentFilesBatch + thisProcessNumFiles
                #Cria o processo passando como argumento a lista de ficheiros que
                #se determinou no passo anterior
                newP = Process(target = filesWC, args = (thisProcessFiles, i))
                processes.append(newP)
            
    for i in range(len(processes)):
        processes[i].start()

    for i in range(len(processes)):
        processes[i].join()

else:
    filesWC(files, 0)
    
    
if interruptState.value == 1:
    print("O programa foi interrompido pelo utilizador, terminando corretamente.")

if "-c" in command:
    print("Número total de caracteres contados: " + str(totalSum.value) + ".")
    actualCommand = "-c"

elif "-w" in command:
    print("Número total de palavras contadas: " + str(totalSum.value) + ".")
    actualCommand = "-w"
    
else:
    print("Número total de linhas contadas: " + str(totalSum.value) + ".")
    actualCommand = "-l"


end = datetime.now()

endExecutionTime = str(end - start)


info = []
infoProcessesIDOrder = []
infoProcessesRunTime = []
infoFilesDimensions = []
infoFilesCounts = []
infoFileCountOrder = []

info.append(startExecutionDateTime)
info.append(endExecutionTime)

if numProcesses > len(files):
    for i in range(numProcesses):
        infoProcessesIDOrder.append(processesIDOrder[i])
        infoProcessesRunTime.append(processesRunTime[i])
        infoFilesDimensions.append(filesDimensions[i])
        infoFilesCounts.append(filesCounts[i])
        infoFileCountOrder.append(fileCountOrder[i])

else:
    for i in range(len(files)):
        infoProcessesIDOrder.append(processesIDOrder[i])
        infoProcessesRunTime.append(processesRunTime[i])
        infoFilesDimensions.append(filesDimensions[i])
        infoFilesCounts.append(filesCounts[i])
        infoFileCountOrder.append(fileCountOrder[i])

info.append(infoProcessesIDOrder)
info.append(files)
info.append(infoProcessesRunTime)
info.append(infoFilesDimensions)
info.append(infoFilesCounts)
info.append(infoFileCountOrder)
info.append(actualCommand)

if numProcesses > len(files):
    info.append(True)

else:
    info.append(False)

if "-f" in optional:
    with open(binaryFileName, "wb") as outFile:
       pickle.dump(info, outFile)

if numProcesses > len(files):
    for i in createdFiles:
        os.remove(i)

