import os
import ctypes
from sys import exit, executable
import shutil
from configparser import ConfigParser

if __name__ == "__main__":
    print("Python: " + executable)
    name = input("[ Input ] 此客户端名称: ")
    Extensions_Required = ["requests", "pywin32", "system_hotkey", "plyer"]

    for Extension in Extensions_Required:
        print("\n[ Info ] 开始安装模块 " + Extension)
        os.system("\"" + executable + "\" -m pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com --no-input " + Extension)

    source_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

    target_path = os.path.abspath(os.getenv("ProgramData") + "\\BKLTaskController\\Bin")

    if not os.path.exists(target_path):
        # 如果目标路径不存在原文件夹的话就创建
        print("补全目录")
        os.makedirs(target_path)

    if os.path.exists(source_path):
        # 如果目标路径存在原文件夹的话就先删除
        print("删除旧文件")
        shutil.rmtree(target_path)

    shutil.copytree(source_path, target_path)
    print('copy dir finished!')
    
    conf = ConfigParser()
    conf.read("config.ini")

    conf.set('data_center', 'name', name)
    f = open(target_path + "\\config.ini", "w", encoding="utf-8")
    conf.write(f)
    f.close()

    ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, "\"" + target_path + "\\start.py\"", None, 0)

    exit()
