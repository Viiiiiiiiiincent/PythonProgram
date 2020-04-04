import argparse
from socket import *
import threading
import cv2
import sys
import struct
import pickle
import time
import zlib

parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, default='192.168.1.102')
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


class Video_Server(threading.Thread):
    def __init__(self, port, version) :
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = ('', port)
        if version == 4:
            self.sock = socket(AF_INET ,SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6 ,SOCK_STREAM)

    def __del__(self):
        self.sock.close()
        try:
            cv2.destroyAllWindows()
        except:
            pass

    def run(self):
        print("VEDIO server starts...")
        self.sock.bind(self.ADDR)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("remote VEDIO client success connected...")
        data = "".encode("utf-8")
        payload_size = struct.calcsize("L")
        cv2.namedWindow('Remote', cv2.WINDOW_NORMAL)
        face_cascade = cv2.CascadeClassifier("D:\pycharm\haarcascade_frontalface_default.xml")
        while True:
            while len(data) < payload_size:
                data += conn.recv(81920)
            packed_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            while len(data) < msg_size:
                data += conn.recv(81920)
            zframe_data = data[:msg_size]
            data = data[msg_size:]
            frame_data = zlib.decompress(zframe_data)
            frame = pickle.loads(frame_data)
            #print(type(frame))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) > 0:
                l = len(faces)
                for faceRect in faces:
                    x, y, w, h = faceRect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "face count", (20, 20), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 255), 2, 1)
                    cv2.putText(frame, str(l), (230, 20), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 255), 2, 1)

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            outVideo = cv2.VideoWriter('save.avi', fourcc, 30, (640, 480))
            cv2.imshow('Remote', frame)
            #if len(faces) > 0:
            outVideo.write(frame)


            cv2.imshow('Remote', frame)

            if cv2.waitKey(1) & 0xFF == 27:
                outVideo.release()

                break


if __name__ == '__main__':
    vserver = Video_Server(PORT, VERSION)

    vserver.start()

    while True:
        time.sleep(1)
        if not vserver.isAlive() :
            print("Video connection lost...")
            sys.exit(0)

