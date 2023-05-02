import os
from sys import exit, executable, argv
import winreg
import py_compile
from configparser import ConfigParser
import base64

if __name__ == "__main__":
    name = argv[1]
    Extensions_Required = ["requests", "pywin32"]

    for Extension in Extensions_Required:
        print("\n[ Info ] 开始安装模块 " + Extension)
        os.system("\"" + executable + "\" -m pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com --no-input " + Extension)

    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    
    config_path = os.path.realpath(".\\..\\Profile\\config.ini")
    
    conf = ConfigParser()
    conf.read(config_path)

    conf.set('BKLTC', 'name', base64.b64encode(name.encode("utf-8")).decode("utf-8"))

    f = open(config_path, "w", encoding="utf-8")
    conf.write(f)
    f.close()

    lst = os.listdir('.')
    for filename in lst:
        stem, suffix = os.path.splitext(filename)
        if suffix == ".py" and stem != "installer":
            py_compile.compile(filename, cfile=filename + "c")
            os.remove(filename)
    print("pyc build done.")

    srv = os.path.realpath(".\\Services\\srvany.exe")

    os.system(".\\Services\\instsrv.exe BKLTaskController " + srv)

    file = os.path.dirname(os.path.realpath(__file__)) + "\\main.pyc"

    # 打开注册表
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    # 打开MyService项
    service_key = winreg.OpenKey(reg, r"SYSTEM\CurrentControlSet\Services\BKLTaskController", 0, winreg.KEY_ALL_ACCESS)

    # 创建 Parameters 子项
    parameters_key = winreg.CreateKeyEx(service_key, "Parameters", 0, winreg.KEY_ALL_ACCESS)

    # 在 Parameters 子项中创建值
    winreg.SetValueEx(parameters_key, "Application", 0, winreg.REG_SZ, executable)
    winreg.SetValueEx(parameters_key, "AppDirectory", 0, winreg.REG_SZ, os.path.dirname(os.path.realpath(executable)))
    winreg.SetValueEx(parameters_key, "AppParameters", 0, winreg.REG_SZ, file + " --auto-start")

    # 关闭注册表
    winreg.CloseKey(parameters_key)
    winreg.CloseKey(service_key)
    winreg.CloseKey(reg)

    # 打开 HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\BKLTaskController 键
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\BKLTaskController", 0, winreg.KEY_ALL_ACCESS)

    # 创建名为 Type 的值，数据为 1
    winreg.SetValueEx(key, "Type", 0, winreg.REG_DWORD, 272)

    # 关闭键
    winreg.CloseKey(key)

    os.system("sc start BKLTaskController")
    os.remove("installer.py")
    print("Installed SUCCESS.")
    exit()