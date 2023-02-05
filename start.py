#-- coding:utf-8 --
import ctypes
from os import path
from sys import executable, exit, argv

import win32api,win32con

reg_root = win32con.HKEY_CURRENT_USER
reg_path = "Software\Microsoft\Windows\CurrentVersion\Run"

def reg_add(position, path: str, type, keyname: str, content):
    try:
        key = win32api.RegOpenKey(position, path, 0, win32con.KEY_ALL_ACCESS)
        win32api.RegSetValueEx(key, keyname, 0, type, content)
        win32api.RegCloseKey(key)
    except Exception as e:
        print(e)
    else:
        print('[ Info ] 注册表操作成功！')

print(argv)
if len(argv) > 1 and argv[1] == "--auto-start":
    print("ok")
else:
    reg_add(reg_root, reg_path, win32con.REG_SZ, "BKLike", "\"" + executable.replace("python.exe", "pythonw.exe") + "\" \"" + path.realpath(__file__) + "\" --auto-start")

ctypes.windll.shell32.ShellExecuteW(None, "runas", executable.replace("pythonw.exe", "python.exe"), "\"" + path.dirname(path.realpath(__file__)) + "\\main.py\"", None, 0)

exit()