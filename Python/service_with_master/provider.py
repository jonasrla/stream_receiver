import socket
import threading
import cv2
import argparse
from time import time
from abstract_script import *

my_epoch = 1433813157

class provider(periferical):
    def __init__ (self, core_ip, nCam):
        super(provider,self).__init__(core_ip)
        self.cap = [cv2.VideoCapture(i) for i in range(nCam)]

        # Setup server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = ('0.0.0.0', 1081)
        self.socket.bind(address)
        self.socket.listen(5)
        # Register on core server
        core_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        core_socket.connect((core_ip,8080))
        core_socket.send('A')
        self.provider_ip = decode_ip(core_socket.recv(4))
        core_socket.close()
    
    def main_thread(self):
        try:
            while 1:
                (client_socket, address) = self.socket.accept()
                print address[0], 'is in'
                ct = threading.Thread(target=self.client_thread, args=(client_socket, address[0]))
                ct.start()
        except KeyboardInterrupt, e:
            self.socket.close()
            map(lambda i: i.release(), self.cap)
            self.notify_core()
    
    def client_thread(self, client_socket, address):
        lock = threading.RLock()
        client_socket.send(bytearray([len(self.cap)]))
        cam_index = ord(client_socket.recv(1))
        try:
            while 1:
                with lock:
                    ret, frame = self.cap[cam_index].read()
                b, buf = cv2.imencode('.jpg',frame)
                buf = bytearray(buf)
                client_socket.send(encode_int(len(buf)))
                client_socket.send(buf)
        except IOError, e:
            print address, 'is out'

if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Provides video streamming to multiple clients')
    parser.add_argument('core_ip', nargs=1, help="Defines core's IP address")
    parser.add_argument('-n', nargs=1, type=int,help='Defines quantity of cameras')
    args = parser.parse_args()
    
    p = provider(args.core_ip[0],args.n[0])
    p.main_thread()