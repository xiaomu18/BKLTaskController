# -*- coding: UTF-8 -*-
import socketserver
from threading import Thread
from ast import literal_eval
from time import sleep, strftime, localtime, time
import sys


def timer():
    return '[ ' + strftime("%m-%d %H:%M:%S", localtime()) + ' ]'

def make_sure_connect(name):
    global online
    online[name] = {"name": name, "state": True, "time": time(), "str_time": strftime("%Y-%m-%d %H:%M:%S", localtime())}
    
def connect_recorder(name, connect):
    global names, online, connects
    
    if not name in names:
        names.append(name)
    
    connects[name] = connect
    make_sure_connect(name)
    

def disconnect_recorder(name):
    global online, connects
    
    if online[name]["state"] != False:
        try:
            connects[name].close()
        except:
            pass
    
        online[name] = {"name": name, "state": False, "time": time(), "str_time": strftime("%Y-%m-%d %H:%M:%S", localtime())}

        try:
            del connects[name]
        except:
            pass


class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        global connects, names, online
        print("A new connect: ", self.client_address)
        try:
            data = self.request.recv(buffer_size)
            json = literal_eval(data.decode("utf-8"))

            if json['state'] != "SUCCESS":
                print(timer(), "[ Fail ] " + data)
                self.disconnect()
                return
            elif json['signature'] != signature:
                print(timer(), "[ Fail ] 签名验证失败.")
                self.disconnect()
                return
            else:
                sd = str({"state": "SUCCESS"})
                self.request.sendall(sd.encode("utf-8"))
                print(timer(), "[ SUCCESS ] 客户端配对成功.", json['name'])
        except Exception as e:
            print(timer(), "[ Fail ]", e)
            return
        else:
            self.name = json['name']
            self.connect()

        while 1:
            try:
                data = self.request.recv(buffer_size)
            except Exception as e:
                print(timer(), self.name, "离线", e)
                self.disconnect()
                break
            if not data:
                continue
            try:
                str_data = data.decode("utf-8")
            except:
                print(timer(), self.name, "信息解码错误", e)
                del data
                continue
            
            if str_data[0] == "{" and str_data[-1] == "}":
                try:
                    json = literal_eval(str_data)
                except Exception as e:
                    print(timer(), self.name, str_data)
                    continue
                if not "state" in json or not "content" in json:
                    print(timer(), self.name, "信息格式错误", json)
                    continue
                if json['state'] == 1:
                    if json['content'] == "online":
                        make_sure_connect(self.name)
                        continue
                    
                    print(f"{timer()} {self.name} 成功: {json['content']}")
                elif json['state'] == 0:
                    print(f"{timer()} {self.name} 错误: {json['content']}")
                else:
                    print(f"{timer()} {self.name} {json['state']}: {json['content']}")
            else:
                print(f"{self.name} | {str_data}")
            
            del data, str_data, json
    
    def connect(self):
        connect_recorder(self.name, self.request)
    
    def disconnect(self):
        disconnect_recorder(self.name)
        self.request.close()


def onliner():
    global names, online, connects
    while 1:
        for name in names:
            if online[name]['state'] == True:
                online[name] = {"name": name, "state": "unknow", "time": time(), "str_time": strftime("%Y-%m-%d %H:%M:%S", localtime())}
                try:
                    connects[name].sendall('{"type": "IsOnline"}'.encode("utf-8"))
                except Exception as e:
                    print(timer(), name, "离线", e)
                    disconnect_recorder(name)
        sleep(30)


def inputs():
    global names, online, connects
    while 1:
        try:
            i = input("> ").split("|")
            if i[0] == "":
                continue
            elif i[0] == "online":
                if len(online) < 1:
                    print("[ Info ] 没有在线实例.")
                else:
                    for name in online:
                        print(name, online[name]['state'], online[name]['str_time'])
            else:
                if i[1] == "kick":
                    print("[ Info ] 踢出客户端 " + i[0])
                    try:
                        connects[i[0]].close()
                        disconnect_recorder(i[0])
                    except Exception as e:
                        print("[ Error ] 强制断开连接时出现错误", e)
                    continue
                if len(i) != 3:
                    print("无效输入")
                    continue

                if i[1] == "pyfile":
                    f = open(i[2], "r")
                    i[1] = "codex"
                    i[2] = f.read()
                    f.close()
                
                data = str({'type': i[1], 'content': i[2]})

                if i[0] == "all":
                    for name in names:
                        if online[name]['state']:
                            try:
                                connects[name].sendall(data.encode("utf-8"))
                            except:
                                print(name, "离线")
                                disconnect_recorder(name)
                        else:
                            print(name, "离线")
                else:
                    if i[0] in connects:
                        connects[i[0]].sendall(data.encode("utf-8"))
                    else:
                        print("此客户端未连接")
        except Exception as e:
            print(timer(), "主线程", e)
        finally:
            i = ['']

if __name__ == "__main__":
    names = []
    connects = {}
    online = {}

    signature = "OvljVQ4e#ZWSlG3Bxh1O"
    buffer_size = 65536

    t = Thread(target=inputs)
    t.daemon = True
    t.start()
    t1 = Thread(target=onliner)
    t1.daemon = True
    t1.start()

    socketserver.ThreadingMixIn.daemon_threads = True

    s = socketserver.ThreadingTCPServer(("0.0.0.0", 32579), MyServer)
    s.serve_forever()