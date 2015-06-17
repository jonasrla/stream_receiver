import socket
import threading
import sqlite3
from time import time
from abstract_script import decode_ip, encode_ip

my_epoch = 1433813157

class core:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('0.0.0.0',8080)
        self.socket.bind(server_address)
        self.socket.listen(5)
        # self.providers = set()

    def main_thread(self):
        try:
            while 1:
                (client_socket, address) = self.socket.accept()
                ct = threading.Thread(target=self.client_thread, args=(client_socket, address[0]))
                ct.start()
        except KeyboardInterrupt, e:
            self.socket.close()

    def client_thread(self, client_socket, address):
        lock = threading.RLock()
        service = client_socket.recv(1)
        conn = sqlite3.connect('core.db')

        if service == "A":
            with lock:
                # self.providers.add(address)
                conn.execute("insert or replace into provider values (?,?)", [address,int(time())-my_epoch])
                conn.commit()
                client_socket.send(encode_ip(address))
            print address,"requests A"
            # self.current_state()
        
        elif service == "R":
            with lock:
                ip_remove = decode_ip(client_socket.recv(4))

                try:
                    # self.providers.remove(ip_remove)
                    conn.execute("delete from provider where ip = ?",[ip_remove])
                    conn.commit()
                except KeyError, e:
                    pass
            print address + " requests R to " + ip_remove
            # self.current_state()
        
        elif service == "G":
            with lock:
                cursor = conn.execute('select ip from provider')
                addresses = cursor.fetchall()
                b = bytearray([len(addresses)])
                for ip in addresses:
                    b.extend(encode_ip(ip[0]))
                client_socket.send(b)

            print address,"requests G"
            # self.current_state()
        
        else:
            client_socket.send(self.error_message())
            print address, "failed\nRequest:", service
        client_socket.close()

        conn.close()

    # def current_state(self):
    #     print 'Current providers'
    #     for p in self.providers:
    #         print p

    def get_providers(self):
        cursor = conn.execute('select ip from provider')
        addresses = cursor.fetchall()
        b = bytearray([len(addresses)])
        for ip in addresses:
            b.extend(encode_ip(ip))
        return b

    def error_message():
        return 'No service identified\n'

if __name__ == "__main__":
    c = core()
    c.main_thread()
