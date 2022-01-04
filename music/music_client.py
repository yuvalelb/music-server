import subprocess
import threading
import select
import socket
from time import sleep
from sys import stdin

musicPipe = ''
exitFlag = False

new = False


def user():
    global exitFlag
    while True:
        userin = input("if you wanna end the program enter exit otherwise just listen\n")
        if userin.lower() == 'exit':
            exitFlag = True
        else:
            print("invalid input")


def musicPlayer(mutex: threading.Lock):
    global musicPipe
    global new
    soundp = subprocess.Popen("ffplay -i pipe:0 -f mp3 -nodisp -loglevel quiet", stdin=subprocess.PIPE)
    print("starting to play")
    while True:
        while not new:
            zero = 0
        mutex.acquire()
        data = musicPipe
        new = False
        mutex.release()
        soundp.stdin.write(data)


# #############################   main    ###############################

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    inp = input("please enter the ip of the server and the port number\n").split()
    if len(inp) != 2:
        print("incorrect number of arguments")
        continue
    ip, port = inp[0], int(inp[1])
    try:
        soc.connect((ip, port))
    except socket.error:
        print("couldn't connect to ", ip, " on port number ", port, " please try again")
    else:
        print("connected!")
        break

mutex = threading.Lock()
playerThread = threading.Thread(target=musicPlayer, args=(mutex,))
playerThread.setDaemon(True)
playerThread.start()

data = soc.recv(1024 * 1024)
print("got first packet with the size of", len(data))
musicPipe = data
# sleep(0.5)

userThread = threading.Thread(target=user)
userThread.setDaemon(True)
userThread.start()
while True:
    receiveSel, useless1, useless2 = select.select([soc], [], [], 1.5)
    if exitFlag:
        exit(0)
    if receiveSel:
        while new:
            zero = 0
        mutex.acquire()
        data = soc.recv(1024 * 1024)
        musicPipe = data
        new = True
        mutex.release()
    else:
        print("1 second time out, exiting")
        exit(1)
