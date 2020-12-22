"""
tcp 多进程 并发
"""
from multiprocessing import Process
from socket import socket
from time import sleep

from Online_dictionary.dict_server.dict_database import Database


class Handle01:
    def __init__(self, tcp, db):
        self.tcp_sk = tcp
        self.db = db

    def request(self, data):
        msg = data.decode().split(" ", 2)
        if msg[0] == "R":
            self.register(msg[1], msg[2])
        elif msg[0] == "L":
            self.login(msg[1], msg[2])
        elif msg[0] == "Q":
            self.query(msg[1], msg[2])
        elif msg[0] == "H":
            self.history(msg[1])

    def register(self, name, psw):
        if self.db.register(name, psw):
            self.tcp_sk.send(b"OK")
        else:
            self.tcp_sk.send(b"FAIL")

    def login(self, name, psd):
        if self.db.login(name, psd):
            self.tcp_sk.send(b"OK")
        else:
            self.tcp_sk.send(b"FAIL")

    def query(self, name, word):
        data = self.db.query(name, word)
        if not data:
            self.tcp_sk.send(b"FAIL")
        else:
            self.tcp_sk.send(data.encode())

    def history(self, name):
        data = self.db.history(name)
        if not data:
            self.tcp_sk.send(b"FAIL")
        else:
            for item in data:
                msg = "%s   %s   %s" % item
                self.tcp_sk.send(msg.encode())
                sleep(0.1)
            self.tcp_sk.send(b"OK")


# 定义进程类
class ClientProcess(Process):
    def __init__(self, conn_df, db):
        super(ClientProcess, self).__init__(daemon=True)
        self.tcp_sk = conn_df
        self.db = db
        self.__handle = Handle01(self.tcp_sk, self.db)

    def run(self) -> None:
        self.db.cursor()
        while True:
            data = self.tcp_sk.recv(1024)
            print("run:", data.decode())
            if not data or data == "E ":
                break
            self.__handle.request(data)
        self.db.cur.close()
        self.tcp_sk.close()


# 创建多进程
class ConcurrentProcess:
    def __init__(self, host="", port=0):
        self.host = host
        self.port = port
        self.db = Database()
        self.ADDRESS = (self.host, self.port)
        self.tcp_sk = self.create_sk()

    def create_sk(self):
        tcp = socket()
        tcp.bind(self.ADDRESS)
        return tcp

    def start(self):
        self.tcp_sk.listen(5)
        print("Listen the port %d" % self.port)
        while True:
            try:
                conn_df, address = self.tcp_sk.accept()
                print("Connect from", address)
            except KeyboardInterrupt as e:
                print(e)
                self.db.close()
                self.tcp_sk.close()
                return
            p = ClientProcess(conn_df, self.db)
            p.start()


if __name__ == '__main__':
    ConcurrentProcess("0.0.0.0", 8889).start()
