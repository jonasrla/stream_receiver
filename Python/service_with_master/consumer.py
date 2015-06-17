import socket
import cv2
import numpy as np
from abstract_script import *


PORT_NO = 1081

UP = 65362
DOWN = 65364
ENTER = 13
ESC = 27

EXIT = ESC
CHANGE = ENTER

class ChangeChannel(Exception):
    def __init__(self,value = ''):
        self.value = value
    def __str__(self):
        return repr(self.value)

class KillBroadcast(Exception):
    def __init__(self, value = ''):
        self.value = value
    def __str__(self):
        return repr(self.value)

class consumer(periferical):
    def __init__(self, core_ip):
        super(consumer,self).__init__(core_ip)
        self.providers_cache = []
        self.get_channels()

        chosen_index = menu('Cameras',self.providers_cache)
        while chosen_index == None:
            chosen_index = menu('Cameras',self.providers_cache)
        
        self.provider_ip = self.providers_cache[chosen_index]

    def get_channels(self):
        try:
            core_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            core_socket.connect((self.core_ip,8080))
            core_socket.send('G')
            nProviders = ord(core_socket.recv(1))
            if nProviders:
                self.providers_cache = [decode_ip(core_socket.recv(4)) for i in range(nProviders)]
            else:
                raise Exception('No camera available')
        except IOError, e:
            pass
    
    def change_channel(self):
        self.socket.close() 
        self.get_channels()
        chosen_index = menu('Cameras',self.providers_cache)
        if chosen_index != None:
            self.provider_ip = self.providers_cache[chosen_index]
        else:
            raise KillBroadcast()

    def main_thread(self):
        while 1:
            try:
                self.consume()
            except ChangeChannel, e:
                self.change_channel()
            except IOError, e:
                self.notify_core()
                self.change_channel()
            except KillBroadcast, e:
                break


    def consume(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.provider_ip,1081))
        nOpt = ord(self.socket.recv(1))
        if nOpt > 1:
            index = menu('Choose Camera',map(lambda x: str(x),range(nOpt)))
            self.socket.send(bytearray([index]))
        else:
            self.socket.send(bytearray([0]))
        cv2.namedWindow(self.provider_ip)
        while 1:
            pack_size = decode_size(self.get_message(4))
            raw_frame = np.array(self.get_message(pack_size))
            frame = cv2.imdecode(raw_frame, cv2.CV_LOAD_IMAGE_COLOR)
            cv2.imshow(self.provider_ip, frame)
            key = cv2.waitKey(10)
            if key == CHANGE:
                raise ChangeChannel()
            elif key == EXIT:
                raise KillBroadcast()

    def get_message(self, size):
        buf = bytearray(0)
        while (len(buf) < size):
            buf += bytearray(self.socket.recv(size-len(buf)))
        return buf

def menu(name,options):
    options = [str(i)+" - "+opt for i,opt in enumerate(options)]
    text_height = 40
    height_margin = 10
    length = 370
    height = text_height*len(options)+height_margin*(len(options)-1) + 10
    img = np.empty([height,length,3])
    img.fill(255)
    font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
    for n, opt in enumerate(options):
        cv2.putText(img, opt, (10,35+(n)*(text_height+height_margin)), font, 1, (0,0,0), 2)
    cv2.namedWindow(name)
    j=0
    while 1:
        c_img = np.array(img)
        top = 5 + j*(text_height+height_margin)
        bottom = top + text_height
        cv2.rectangle(c_img,(7,top),(360,bottom),(0,0,0),2)
        cv2.imshow(name,c_img)
        key = cv2.waitKey(10)
        if key==UP and j > 0:
            j -= 1
        elif key==DOWN and j < len(options) - 1:
            j += 1
        elif key == ENTER:
            cv2.destroyWindow(name)
            return j
        elif key == ESC:
            cv2.destroyWindow(name)
            break

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Provides video streamming to multiple clients')
    parser.add_argument('core_ip', nargs=1, help="Defines core's IP address")
    args = parser.parse_args()

    c = consumer(args.core_ip[0])
    c.main_thread()