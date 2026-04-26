#!/usr/bin/env python3
"""
测试计算器查找逻辑
"""
import os
import subprocess

app_name = "计算器"

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

print(f"测试: {app_name}")
print(f"变体: {app_variants}")

# 尝试 where 命令
print("\n尝试 where 命令:")
for variant in app_variants:
    try:
        result = subprocess.run(['where', variant], capture_output=True, text=True, shell=True)
        print(f"  where {variant} -> 退出码: {result.returncode}")
        if result.stdout.strip():
            print(f"  输出: {result.stdout.strip()}")
        if result.stderr.strip():
            print(f"  错误: {result.stderr.strip()}")
    except Exception as e:
        print(f"  错误: {e}")

# 尝试直接运行
print("\n尝试直接运行:")
try:
    # 尝试直接运行 calc
    subprocess.Popen(['calc'], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("  已尝试启动 calc")
except Exception as e:
    print(f"  错误: {e}")

# 尝试 start 命令
print("\n尝试 start 命令:")
try:
    result = subprocess.run(f"start {app_name}", shell=True, capture_output=True, text=True)
    print(f"  start {app_name} -> 退出码: {result.returncode}")
except Exception as e:
    print(f"  错误: {e}")
