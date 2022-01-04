import socket
import threading
import time

import select
from sys import exit, stdin
import dicfile

connections = []
songList = [""]
skipFlag = False
exitFlag = False


def user():
    global skipFlag
    global exitFlag
    while True:
        userin = input("if you wanna skip enter skip, if you wanna end the program enter exit otherwise just listen\n")
        if userin.lower() == 'skip':
            skipFlag = True
        elif userin.lower() == 'exit':
            exitFlag = True
        else:
            print("invalid input, if you wanna skip enter skip, if you wanna end the program enter exit otherwise just listen")


def listening_thread():
    global connections
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(("", 42069))
    soc.listen()
    while True:
        con, addr = soc.accept()
        print("accepted a connection from ", addr)
        connections.append(con)


def station():
    global connections
    global songList
    global skipFlag
    fileopen = False
    fileInd = 0
    while True:
        while not fileopen:
            if fileInd >= len(songList):
                print("no more songs to play, exiting")
                exit(0)
            try:
                f = open(songList[fileInd], 'rb')
            except:
                print("couldn't open the file ", songList[fileInd])
                del songList[fileInd]
            else:
                fileopen = True
        f.read(6)  # id3 header, useless stuff
        buffer = f.read(4)  # id3 header, size
        size = int(buffer[3]) + int(buffer[2]) * (2 ** 7) + int(buffer[1]) * (2 ** 14) + int(buffer[0]) * (2 ** 21)  # for some reason the size of the header is 4 bytes,
        # but in each byte the most significant bit is disabled, so we need this weird calculation
        f.read(size)  # ignoring the metadata
        checkeof = True
        ptime = 0
        while True:
            tim = time.time() + 1
            ptime = 0
            data = bytes()
            while ptime < 1 and checkeof:  # 1 seconds target
                buffer = f.read(4)  # reading a frame header
                data += buffer
                bitr, samplerate = dicfile.headtorate(buffer)  # getting the rates from the header
                sampleamount = dicfile.sample[(buffer[1] & 0b1110) >> 1]  # checking the amount of samples in the frame
                size = int((sampleamount / 8 * 1000 * bitr) / samplerate) + (
                        (buffer[3] & 0b10) >> 1) - 4  # calculating frame size: how many samples per bytes, bitrate in kbps times
                # 1000 (k = 1000) all divided by the sample rate plus a padding byte if there is any, -4 since we already read 4 bytes from the frame
                samplesize = size / sampleamount
                ptime += sampleamount / samplerate  # number of samples divided by how many samples per second
                data += f.read(size)  # reading the rest of the frame
                pos = f.tell()  # checking if we reached the end of file, for some reason python doesn't have a check for that, or peek function
                checkeof = f.read(1) != ''  # so i read a character, check if it's empty, if it's not we continue the loop, otherwise we end it
                f.seek(pos)  # and return to the space we were in the file before the check
            if data != '' and not skipFlag:
                for con in connections:
                    con.send(data)
            else:
                skipFlag = False
                break
            while time.time() <= tim:
                one = 1


############################################################################# main ###################################################################


check = True
while check:
    answer = input("welcome to yoyo's music server, please enter the path to a song \n(if it's in the same folder you only need the song name, only works with mp3)\n")
    try:
        f = open(answer, 'rb')
    except:
        print("a problem opening the file has occurred please try again")
    else:
        check = False
f.close()
songList[0] = answer
check = True
while check:
    answer = input("if you want to add another song enter the path to it now, otherwise press enter\n")
    if answer == '':
        break
    try:
        f = open(answer, 'rb')
    except:
        print("a problem opening the file has occurred please try again")
    else:
        songList.append(answer)
        f.close()
        print("song added successfully")
print("starting to listen")
navi = threading.Thread(target=listening_thread)
navi.setDaemon(True)
navi.start()
print("starting station")
stationThread = threading.Thread(target=station)
stationThread.setDaemon(True)
stationThread.start()

userThread = threading.Thread(target=user)
userThread.setDaemon(True)
userThread.start()

while stationThread.is_alive():
    if exitFlag:
        exit(0)
