"""
客户端请求操作    2个界面
"""
import sys
from socket import socket


class ClientView:
    def __init__(self):
        self.ADDRESS = ("127.0.0.1", 8889)
        self.tcp_sk = self.create_sk()
        self.__controller = ClientController(self.tcp_sk)

    def create_sk(self):
        tcp = socket()
        tcp.connect(self.ADDRESS)
        return tcp

    def display01(self):
        print("""
        ***1级***
         1.注  册
         2.登  录
         3.退  出  
        *********      
        """)

    def display02(self):
        print("""
        ***2级***
         1.查询单词
         2.历史记录
         3.注   销    
        *********    
        """)

    def select01(self):
        option = input(">>")
        if option == "1":
            self.register()
        elif option == "2":
            self.login()
        elif option == "3":
            self.exit()
            sys.exit("谢谢使用!")

    def select02(self, name):
        option = input(">>")
        if option == "1":
            self.query(name)
        elif option == "2":
            self.history(name)
        elif option == "3":
            return True

    def main02(self, name):
        while True:
            self.display02()
            if self.select02(name):
                break

    def main01(self):
        while True:
            self.display01()
            self.select01()

    def register(self):
        while True:
            name = input("请输入注册用户名:")
            if not name:
                break
            password = input("请输入密码:")
            re_password = input("请确认密码:")
            if " " in name or " " in password:
                print("不能输入特殊字符")
                continue
            if password == re_password:
                msg = "R %s %s" % (name, password)
                if self.__controller.register(msg):
                    print(f"注册成功!请牢记用户名:{name};密码:{password},暂未开发找回业务!")
                else:
                    print("该用户名已被注册!")
            else:
                print("密码不一致!请重新输入!")

    def login(self):
        while True:
            name = input("请输入用户名:")
            if not name:
                break
            password = input("请输入密码:")
            msg = "L %s %s" % (name, password)
            if self.__controller.login(msg):
                print("登陆成功!")
                self.main02(name)
                self.main01()
            else:
                print("用户名或密码错误!")

    def exit(self):
        self.tcp_sk.send(b"E ")

    def query(self, name):
        while True:
            word = input("请输入需要查询的单词:")
            if not word:
                break
            msg = "Q %s %s" % (name, word)
            data = self.__controller.query(msg)
            if not data:
                print("没有收录该单词!")
            else:
                print(data)

    def history(self, name):
        msg = "H %s" % name
        for item in self.__controller.history(msg):
            print(item)


class ClientController:
    def __init__(self, tcp):
        self.tcp_sk = tcp

    def register(self, msg):
        self.tcp_sk.send(msg.encode())
        data = self.tcp_sk.recv(1024)
        if data == b"OK":
            return True
        else:
            return False

    def login(self, msg):
        self.tcp_sk.send(msg.encode())
        data = self.tcp_sk.recv(1024)
        if data == b"OK":
            return True
        else:
            return False

    def query(self, msg):
        self.tcp_sk.send(msg.encode())
        data = self.tcp_sk.recv(1024)
        if data == b"FAIL":
            return False
        else:
            return data.decode()

    def history(self, msg):
        self.tcp_sk.send(msg.encode())
        while True:
            data = self.tcp_sk.recv(1024)
            if data == b"FAIL":
                yield "暂无记录"
                break
            elif data == b"OK":
                break
            else:
                yield data.decode()


if __name__ == '__main__':
    obj = ClientView()
    obj.main01()
