# -*- coding: utf-8 -*-
# cython: language_level=3

import win32api, win32con, ctypes
import struct

def reg_add(position, path: str, type, keyname: str, content):
    try:
        key = win32api.RegOpenKey(position, path, 0, win32con.KEY_ALL_ACCESS)
        win32api.RegSetValueEx(key, keyname, 0, type, content)
        win32api.RegCloseKey(key)
    except Exception as e:
        print(e)
        return False
    else: return True
    
def reg_del(position, path: str, keyname: str):
    try:
        key = win32api.RegOpenKey(position, path, 0, win32con.KEY_ALL_ACCESS)
        win32api.RegDeleteValue(key, keyname)
        win32api.RegCloseKey(key)
    except Exception as e:
        print(e)
        return False
    else: return True

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

class ExchangeProtocol:
    def __init__(self, sock) -> None:
        self.socket = sock
        self.available = True
        self.encoding = "utf-8"

    def send_msg(self, message: str):
        # 检查连接是否可用
        if not self.available: raise ValueError("连接不可用")

        message = message.encode(self.encoding)
        header = struct.pack('!I', len(message))  # 获取长度 Header

        try:
            self.socket.sendall(header + message)
        except: 
            self.available = False
            raise ValueError("发送失败")

    def recv_msg(self):
        # 检查连接是否可用
        if not self.available: raise ValueError("连接不可用")

        # 接收消息头
        header = self.socket.recv(4)

        if header == b'':
            self.available = False
            raise ValueError("连接已断开")
        
        elif len(header) != 4:
            self.available = False
            raise ValueError("Header 数据不完整. 无法解包.")

        message_len = struct.unpack('!I', header)[0]  # 解包消息长度

        # 接收消息内容
        data = self.socket.recv(message_len)

        return data.decode(self.encoding)
    
    def close(self):
        self.socket.close()
        self.available = False

