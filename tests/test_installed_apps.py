#!/usr/bin/env python3
"""
测试 get_installed_applications 函数，显示当前电脑上已安装的应用程序列表
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入函数
def get_installed_applications():
    """
    获取系统中已安装的应用程序列表
    """
    installed_apps = []
    
    # 1. 从 Windows 注册表读取
    if os.name == 'nt':
        try:
            import winreg
            # 32位和64位注册表路径
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
            ]
            
            for reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    try:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                subkey = winreg.OpenKey(key, subkey_name)
                                try:
                                    # 读取默认值（通常是可执行文件路径）
                                    default_value, _ = winreg.QueryValueEx(subkey, "")
                                    if default_value and Path(default_value).exists():
                                        installed_apps.append((subkey_name, default_value))
                                except:
                                    pass
                                finally:
                                    winreg.CloseKey(subkey)
                            except WindowsError:
                                break
                            i += 1
                    finally:
                        winreg.CloseKey(key)
                except:
                    pass
        except:
            pass
    
    # 2. 从开始菜单读取快捷方式
    start_menu_paths = [
        os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Start Menu\Programs"),
    ]
    
    for start_menu_path in start_menu_paths:
        if Path(start_menu_path).exists():
            for root, dirs, files in os.walk(start_menu_path):
                for file in files:
                    if file.endswith('.lnk'):
                        lnk_path = os.path.join(root, file)
                        # 尝试解析快捷方式
                        try:
                            import win32com.client
                            shell = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell.CreateShortcut(lnk_path)
                            target_path = shortcut.TargetPath
                            if target_path and Path(target_path).exists():
                                # 提取应用名称（去除.lnk后缀）
                                app_name = file[:-4] if file.endswith('.lnk') else file
                                installed_apps.append((app_name, target_path))
                        except:
                            pass
    
    # 3. 从 Windows 应用商店读取
    windows_apps_path = r"C:\Program Files\WindowsApps"
    if Path(windows_apps_path).exists():
        try:
            for root, dirs, files in os.walk(windows_apps_path):
                # 限制搜索深度，避免过深搜索
                if root.count(os.sep) - windows_apps_path.count(os.sep) > 3:
                    continue
                for file in files:
                    if file.endswith('.exe') and not file.startswith('App'):
                        exe_path = os.path.join(root, file)
                        if Path(exe_path).exists():
                            # 提取应用名称
                            app_name = file[:-4] if file.endswith('.exe') else file
                            installed_apps.append((app_name, exe_path))
        except:
            pass
    
    # 4. 从环境变量 PATH 读取
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for path_dir in path_dirs:
        if Path(path_dir).exists():
            try:
                for file in os.listdir(path_dir):
                    if file.endswith('.exe'):
                        exe_path = os.path.join(path_dir, file)
                        if Path(exe_path).exists():
                            app_name = file[:-4] if file.endswith('.exe') else file
                            installed_apps.append((app_name, exe_path))
            except:
                pass
    
    # 去重
    unique_apps = {}
    for app_name, app_path in installed_apps:
        # 以应用路径为键去重
        if app_path not in unique_apps:
            unique_apps[app_path] = app_name
    
    # 转换回列表格式
    return [(name, path) for path, name in unique_apps.items()]

# 测试函数
if __name__ == "__main__":
    print("正在获取已安装的应用程序列表...")
    print("=" * 60)
    
    installed_apps = get_installed_applications()
    
    print(f"共找到 {len(installed_apps)} 个应用程序")
    print("=" * 60)
    
    # 显示前50个应用程序（如果超过50个）
    display_count = min(50, len(installed_apps))
    for i, (app_name, app_path) in enumerate(installed_apps[:display_count]):
        print(f"{i+1}. {app_name}")
        print(f"   路径: {app_path}")
        print()
    
    if len(installed_apps) > 50:
        print(f"... 还有 {len(installed_apps) - 50} 个应用程序未显示")
    
    print("=" * 60)
    print("测试完成！")
