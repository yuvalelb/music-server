import subprocess
import socket
import sys
import threading
import select
from sys import exit, stdin
import dicfile

stationConnectionList = []
stationConnection = []
stationArgument = ""
skippingstation = []
activeStation = []
exitFlags = []


#  **************************************************************************************************************************************************
#  *************************************************station code*************************************************************************************
#  **************************************************************************************************************************************************

def station(station_id, music_list):
    track_num = 0
    estart = -1  # where did the file opening error start
    fileread = False
    ptime = 0  # playing time

    # fileread asks if a file is currently open and is not finished, at first run it's false
    while not fileread:
        try:
            f = open(music_list[track_num], 'rb')  # try to open a file
        except:  # fail to open a file
            if estart == track_num:
                print("we had a problem opening all the music files, exiting station " + str(station_id))
                exit(1)
            if estart == -1:  # if it's the first time in a row that it failed save this position, if we reach this position again it means the entire list is unreadable
                estart = track_num
            print("station ", station_id, " couldn't open file ' ", music_list[track_num], " ' trying to skip")
            track_num += 1
            if track_num >= len(music_list):  # if we reached the end of the list
                track_num = 0
        else:  # managed to open a file
            fileread = True
            estart = -1

    # left the loop, a file is open

    f.read(6)  # id3 header, useless stuff
    buffer = f.read(4)  # id3 header, size
    size = int(buffer[3]) + int(buffer[2]) * (2 ** 7) + int(buffer[1]) * (2 ** 14) + int(buffer[0]) * (2 ** 21)  # for some reason the size of the header is 4 bytes,
    # but in each byte the most significant bit is disabled, so we need this weird calculation
    f.read(size)  # ignoring the metadata

    buffer = f.read(4)  # reading a frame header
    while buffer != "":
        data = buffer
        while ptime < 1:  # 5 seconds target
            bitr, samplerate = dicfile.headtorate(buffer)  # getting the rates from the header
            sampleamount = dicfile.sample[(buffer[1] & 0b1110) >> 1]  # checking the amount of samples in the frame
            size = int((sampleamount / 8 * 1000 * bitr) / samplerate) + (
                        (buffer[3] & 0b10) >> 1) - 4  # calculating frame size: how many samples per bytes, bitrate in kbps times
            # 1000 (k = 1000) all divided by the sample rate plus a padding byte if there is any, -4 since we already read 4 bytes from the frame
            samplesize = size / sampleamount
            ptime += sampleamount / samplerate  # number of samples divided by how many samples per second
            data += f.read(size)  # reading the rest of the frame


def listening_thread():
    global stationConnection
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(("", 69420))
    soc.listen()
    con, addr = soc.accept()
    stationConnection.append(con)
    print("accepted a connection from ", addr)

#  **************************************************************************************************************************************************
#  ******************************************************main****************************************************************************************
#  **************************************************************************************************************************************************


global stationArgument
songspath = input("welcome to the music server, please enter the path to the songs separated by a coma (,)\n")
stationthreads = threading.Thread(target=station,args=(1, songspath))
stationthreads.setDaemon(True)
stationthreads.start()
navi = threading.Thread(target=listening_thread, args=())

print("welcome to the server menu! please choose an option (or don't and let the music play)\n1. get the number of stations running\n2. add another song to a "
          "station's list\n3. get the amount of connections a station has\n4. skip a song on a station\n5.stop a station\n6. stop all stations and finish")
while stationthreads.is_alive():
    rlist, wlist, xlist = select.select([stdin], [], [], 1)
    if len(rlist):
        option = sys.stdin.read()
        print(type(option))
        if option == "1":
            print("currently it only works with one (1) station, stay tuned for updates though!")
        elif option == "2":
            stationArgument = input("please enter the path to the song you'd like to add!\n")
        elif option == "3":
            print(len(stationConnection[0]))
        elif option == "4":
            print("skipping")
            skippingstation[0] = 1
        elif option == "5":
            while True:
                option = input("which station would you like to stop? (currently only 0 works)\n")
                if int(option) > len(activeStation):
                    print("%d station doesn't exist, please try again" % option)
                else:
                    break
            exitFlags[option] = True
            option = "5"
        elif option == "6":
            print("stopping all stations and shutting down, may take a few seconds..\n")
            exit(0)
