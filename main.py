import winreg
import subprocess
import sys
import os
import ctypes

ICON_VALUE_NAME = "29"
ICON_VALUE_DATA = r"%windir%\System32\shell32.dll,-50"
REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer"
SUB_KEY = "Shell Icons"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def elevate():
    python_exe = sys.executable
    script = os.path.abspath(__file__)
    params = f'"{script}"'
    ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
    sys.exit(0)

def ensure_shell_icons_value():
    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
            try:
                try:
                    shell_key = winreg.OpenKey(hklm, REG_PATH + "\\" + SUB_KEY, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
                except FileNotFoundError:
                    explorer_key = winreg.OpenKey(hklm, REG_PATH, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
                    shell_key = winreg.CreateKey(explorer_key, SUB_KEY)

                winreg.SetValueEx(shell_key, ICON_VALUE_NAME, 0, winreg.REG_SZ, ICON_VALUE_DATA)
                try:
                    winreg.CloseKey(shell_key)
                except Exception:
                    pass
            except PermissionError:
                print("权限不足，无法写入注册表（HKLM）。")
                sys.exit(1)
    except PermissionError:
        print("权限不足，无法访问注册表（HKLM）。")
        sys.exit(1)

def restore_default_icons():
    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
            try:
                shell_key = winreg.OpenKey(hklm, REG_PATH + "\\" + SUB_KEY, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
                try:
                    winreg.DeleteValue(shell_key, ICON_VALUE_NAME)
                except FileNotFoundError:
                    pass
                try:
                    winreg.CloseKey(shell_key)
                except Exception:
                    pass
            except FileNotFoundError:
                pass
            except PermissionError:
                print("权限不足，无法修改注册表（HKLM）。")
                sys.exit(1)
    except PermissionError:
        print("权限不足，无法访问注册表（HKLM）。")
        sys.exit(1)

def restart_explorer():

    local_appdata = os.environ.get('LOCALAPPDATA', '')
    cmds = [
        'taskkill /IM explorer.exe /F',
        f'del /A /Q "{local_appdata}\\IconCache.db"',
        f'del /A /F /Q "{local_appdata}\\Microsoft\\Windows\\Explorer\\iconcache*"',
        'start explorer.exe'
    ]
    for cmd in cmds:
        subprocess.run(cmd, shell=True)

def main_menu():
    print("根据需求，填写1或2再按Enter回车键。（如有卡顿或异常需要稍等30秒，没用的话重启。使用后卸载本程序不会有任何残留垃圾）\n")
    print("1. 去除软件图标小箭头（包括黑块）")
    print("2. 恢复到默认软件图标\n")

    while True:
        choice = input("输入1或2并回车：").strip()
        if choice == "1":
            ensure_shell_icons_value()
            restart_explorer()
            print("操作完成：已设置 29 并重启 Explorer。")
            break
        elif choice == "2":
            restore_default_icons()
            restart_explorer()
            print("已恢复默认")
            break   
        else:
            print("无效输入，请输入正确指令")

if __name__ == "__main__":
    if not is_admin():
        try:
            print("检查到当前未以管理员权限运行，正在请求提升（UAC）……")
            elevate()
        except Exception:
            print("无法提升为管理员，请右键以管理员身份运行此程序。")
            sys.exit(1)
    main_menu()