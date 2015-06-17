import socket
import sys
import cv2
from numpy import array

def error(message):
    raise Exception(message)

def create_server(portno):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', portno)
    sock.bind(server_address)
    sock.listen(1)
    print >>sys.stderr, 'Waiting connection...'
    connection, address = sock.accept()
    print >>sys.stderr, '%s connected' % address[0]
    return (connection, sock)

def get_message(socket, size):
    buf = bytearray(0)
    while (len(buf) < size):
        buf += bytearray(socket.recv(size-len(buf)))
    return buf

def decode_size(bytearray):
    return int(bytearray[0]*(256**0)) + int(bytearray[1]*(256**1)) + int(bytearray[2]*(256**2)) + int(bytearray[3]*(256**3))

def request_frame(socket):
    socket.send(bytearray(1))

def get_frame(socket):
    pack_size = decode_size(get_message(socket, 4))
    return array(get_message(socket,pack_size))

if __name__=="__main__":
    foreign_socket, local_socket = create_server(8080)
    cv2.namedWindow("results")
    while 1:
        request_frame(foreign_socket)
        raw_frame = get_frame(foreign_socket)
        frame = cv2.imdecode(raw_frame, cv2.CV_LOAD_IMAGE_COLOR)
        cv2.imshow("results", frame)
        if cv2.waitKey(10)>=0:
            break
    foreign_socket.close()
    local_socket.close()