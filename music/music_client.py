import subprocess
import threading
import select
import socket
from time import sleep
from sys import stdin

musicPipe = ''


def musicPlayer(mutex: threading.Lock):
    global musicPipe
    soundp = subprocess.Popen("ffplay -i pipe:0 -f mp3 -nodisp", stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        mutex.acquire()
        data = musicPipe
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
        break

data = soc.recv(1024 * 1024)
mutex = threading.Lock()
musicPipe = data
sleep(0.5)

playerThread = threading.Thread(target=musicPlayer(mutex))
playerThread.setDaemon(True)
playerThread.start()
print("if you want to end the program type exit")
while True:
    receiveSel, useless1, useless2 = select.select([soc, stdin], [], [], 1)
    if receiveSel[0]:
        mutex.acquire()
        data = soc.recv(1024 * 1024)
        musicPipe = data
        mutex.release()
    elif receiveSel[1]:
        inp = stdin.read()
        if inp.lower() == 'exit':
            exit(0)
        else:
            print("error, if you want to end the program type exit")
    else:
        print("1 second time out, exiting")
        exit(1)
