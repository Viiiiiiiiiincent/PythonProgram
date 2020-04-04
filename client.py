from socket import *
import threading
import cv2
import struct
import pickle
import zlib
import sys
import time
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=10087)
parser.add_argument('--noself', type=bool, default=False)
parser.add_argument('--level', type=int, default=0)
parser.add_argument('-v', '--version', type=int, default=4)

args = parser.parse_args()

IP = args.host
PORT = args.port
VERSION = args.version
SHOWME = not args.noself
LEVEL = args.level



class Video_Client(threading.Thread):
    def __init__(self ,ip, port, showme, level, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = (ip, port)
        self.showme = showme
        if level == 0:
            self.interval = 0
        elif level == 1:
            self.interval = 1
        elif level == 2:
            self.interval = 2
        else:
            self.interval = 3
        self.fx = 1 / (self.interval + 1)
        if self.fx < 0.3:
            self.fx = 0.3
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.cap = cv2.VideoCapture(0)
        print("VEDIO client starts...")
    def __del__(self) :
        self.sock.close()
        self.cap.release()
        if self.showme:
            try:
                cv2.destroyAllWindows()
            except:
                pass
    def run(self):
        while True:
            try:
                self.sock.connect(self.ADDR)
                break
            except:
                time.sleep(3)
                continue
        if self.showme:
            cv2.namedWindow('You', cv2.WINDOW_NORMAL)
        print("VEDIO client connected...")
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if self.showme:
                cv2.imshow('You', frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    self.showme = False
                    cv2.destroyWindow('You')
            sframe = cv2.resize(frame, (0,0), fx=self.fx, fy=self.fx)
            data = pickle.dumps(sframe)
            zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            try:
                self.sock.sendall(struct.pack("L", len(zdata)) + zdata)
            except:
                break
            for i in range(self.interval):
                self.cap.read()


if __name__ == '__main__':
    vclient = Video_Client(IP, PORT, SHOWME, LEVEL, VERSION)

    vclient.start()

    while True:
        time.sleep(1)
        if not vclient.isAlive():
            print("Video connection lost...")
            sys.exit(0)
