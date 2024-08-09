import sys, pickle
import datetime

args = sys.argv[1:]
file = args[0]


def formatTime(result):
    output = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(result),\
                               "%H:%M:%S:%f")
    return output


with open(file, "rb") as inFile:
    info = pickle.load(inFile)

startExecutionDateTime = info[0]
endExecutionTime = info[1]
processesOrder = info[2]
files = info[3]
filesRunTime = info[4]
filesDimensions = info[5]
filesCounts = info[6]
fileCountOrder = info[7]
command = info[8]

if command == "-c":
    commandPhrase = "caracteres"
    
elif command == "-w":
    commandPhrase = "palavras"

else:
    commandPhrase = "linhas"

print("Início da execução da pesquisa: " + startExecutionDateTime)
print("Duração da execução: " + endExecutionTime)

if info[9] == True:
    for i in range(len(processesOrder)):
        thisProcess = processesOrder[i]
        thisFileName = files[fileCountOrder[i]]
        thisFileRunTime = filesRunTime[i]
        thisFileDimensions = filesDimensions[i]
        thisFileCount = filesCounts[i]

        print("Processo: " + str(thisProcess))
        print("        ficheiro: " + str(thisFileName))
        print("                tempo de pesquisa: " + str(formatTime(thisFileRunTime)))
        print("                dimensão do ficheiro: " + str(thisFileDimensions))
        print("                número de " + commandPhrase + ": " + str(thisFileCount))

else:
    for i in range(len(files)):
        thisProcess = processesOrder[i]
        thisFileName = files[fileCountOrder[i]]
        thisFileRunTime = filesRunTime[i]
        thisFileDimensions = filesDimensions[i]
        thisFileCount = filesCounts[i]

        print("Processo: " + str(thisProcess))
        print("        ficheiro: " + str(thisFileName))
        print("                tempo de pesquisa: " + str(formatTime(thisFileRunTime)))
        print("                dimensão do ficheiro: " + str(thisFileDimensions))
        print("                número de " + commandPhrase + ": " + str(thisFileCount))
