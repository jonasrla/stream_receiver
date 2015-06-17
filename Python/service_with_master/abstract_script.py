import socket

def decode_ip(raw):
    return '.'.join([str(ord(i)) for i in raw])

def encode_ip(text):
    return bytearray([int(i) for i in text.split('.')])

def decode_size(bytearray):
    return int(bytearray[0]*(256**0)) + int(bytearray[1]*(256**1)) + int(bytearray[2]*(256**2)) + int(bytearray[3]*(256**3))

def encode_int(num):
    var1 = num/(256**3)
    var2 = (num - var1*(256**3))/(256**2)
    var3 = (num - var1*(256**3) - var2*(256**2))/(256**1)
    var4 = num % 256
    return bytearray([var4,var3,var2,var1])

class periferical(object):
    def __init__(self, core_ip):
        self.core_ip = core_ip

    def notify_core(self):
        core_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        core_socket.connect((self.core_ip,8080))
        core_socket.send('R')
        core_socket.send(encode_ip(self.provider_ip))