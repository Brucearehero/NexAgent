#!/usr/bin/env python3
"""
NexAgent - 打开应用程序逻辑测试
"""
import sys
import os
import subprocess
from pathlib import Path

def test_find_application(app_name):
    """测试查找应用程序的逻辑"""
    print(f"测试查找: {app_name}")
    
    # 应用程序名称变体
    app_variants = [app_name]
    if not app_name.endswith('.exe'):
        app_variants.append(app_name + '.exe')
    if '音乐' in app_name:
        app_variants.extend(['QQ音乐', 'qq音乐', 'QQMusic', 'QQ音乐.exe', 'qq音乐.exe', 'QQMusic.exe'])
    elif 'chrome' in app_name.lower():
        app_variants.extend(['chrome', 'Chrome', 'chrome.exe', 'Chrome.exe', 'Google Chrome', 'Google Chrome.exe'])
    elif 'notepad' in app_name.lower() or '记事本' in app_name:
        app_variants.extend(['notepad', 'notepad.exe', '记事本', '记事本.exe'])
    elif 'calc' in app_name.lower() or '计算器' in app_name:
        app_variants.extend(['calc', 'calc.exe', '计算器', '计算器.exe'])
    elif 'mspaint' in app_name.lower() or '画图' in app_name:
        app_variants.extend(['mspaint', 'mspaint.exe', '画图', '画图.exe'])
    
    print(f"变体: {app_variants}")
    
    # 常见应用程序安装目录
    search_dirs = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expanduser(r"~\AppData\Local\Programs"),
        os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
        r"D:\Program Files",
        r"D:\Program Files (x86)",
        os.path.expanduser(r"~\Desktop"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Start Menu\Programs"),
    ]
    
    # 搜索应用程序
    import glob
    found = False
    for search_dir in search_dirs:
        for variant in app_variants:
            # 搜索带.exe的
            search_pattern = os.path.join(search_dir, "**", variant)
            matches = glob.glob(search_pattern, recursive=True)
            if matches:
                print(f"找到: {matches[0]}")
                found = True
                return matches[0]
            
            # 搜索快捷方式
            lnk_pattern = os.path.join(search_dir, "**", variant + '.lnk')
            lnk_matches = glob.glob(lnk_pattern, recursive=True)
            if lnk_matches:
                print(f"找到快捷方式: {lnk_matches[0]}")
                found = True
                return lnk_matches[0]
    
    # 尝试通过系统 where 命令查找
    try:
        result = subprocess.run(['where', app_name], capture_output=True, text=True, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            found_path = result.stdout.strip().split('\n')[0]
            print(f"通过 where 找到: {found_path}")
            found = True
            return found_path
    except:
        pass
    
    if not found:
        print("未找到")
    return None

def test_open_app():
    """测试打开应用程序"""
    print("=" * 60)
    print("NexAgent 打开应用程序逻辑测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        "notepad",      # 记事本
        "记事本",       # 记事本（中文）
        "calc",         # 计算器
        "计算器",        # 计算器（中文）
        "mspaint",      # 画图
        "画图",         # 画图（中文）
        "QQ音乐",       # QQ音乐
    ]
    
    for app in test_cases:
        print(f"\n测试: {app}")
        print("-" * 40)
        path = test_find_application(app)
        if path:
            print(f"[PASS] 找到应用程序: {path}")
            # 尝试启动
            try:
                if os.name == 'nt':
                    subprocess.Popen([path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    print("[PASS] 已尝试启动应用程序")
                else:
                    subprocess.Popen([path], shell=True, detached=True)
                    print("[PASS] 已尝试启动应用程序")
            except Exception as e:
                print(f"[ERROR] 启动失败: {str(e)}")
        else:
            print("[FAIL] 未找到应用程序")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_open_app()
