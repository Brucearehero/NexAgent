#!/usr/bin/env python3
"""
最终修复测试
"""
import os
import subprocess
from pathlib import Path

def test_find_app(app_name):
    """测试查找应用程序"""
    print(f"测试: {app_name}")
    
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
    elif 'word' in app_name.lower() or ' Word' in app_name:
        app_variants.extend(['winword', 'winword.exe', 'Word', 'Word.exe'])
    elif 'excel' in app_name.lower() or 'Excel' in app_name:
        app_variants.extend(['excel', 'excel.exe', 'Excel', 'Excel.exe'])
    
    print(f"变体: {app_variants}")
    
    # 尝试 where 命令
    for variant in app_variants:
        if os.name == 'nt':
            # Windows 使用 cmd /c where
            result = subprocess.run(['cmd', '/c', 'where', variant], capture_output=True, text=True)
        else:
            # 其他系统直接使用 where
            result = subprocess.run(['where', variant], capture_output=True, text=True, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            found_path = result.stdout.strip().split('\n')[0]
            print(f"通过 where 找到: {found_path}")
            # 尝试启动
            if os.name == 'nt':
                subprocess.Popen([found_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([found_path], shell=True, detached=True)
            return True
    
    # 尝试直接运行常见命令
    common_commands = {
        '计算器': 'calc',
        '记事本': 'notepad',
        '画图': 'mspaint',
    }
    if app_name in common_commands:
        cmd = common_commands[app_name]
        try:
            if os.name == 'nt':
                subprocess.Popen([cmd], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                print(f"直接运行: {cmd}")
                return True
        except:
            pass
    
    print("未找到")
    return False

def main():
    print("=" * 60)
    print("NexAgent 最终修复测试")
    print("=" * 60)
    
    test_cases = ["计算器", "记事本", "画图", "QQ音乐"]
    
    for app in test_cases:
        print(f"\n测试: {app}")
        print("-" * 40)
        success = test_find_app(app)
        if success:
            print("[PASS] 成功找到并启动")
        else:
            print("[FAIL] 未找到")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
