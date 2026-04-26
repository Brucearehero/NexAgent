#!/usr/bin/env python3
"""
测试 open_application 工具的功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入核心函数
def test_open_application(app_path):
    """
    测试应用程序打开功能
    """
    import os
    from pathlib import Path
    import subprocess
    import glob
    
    # 处理输入
    app_path = app_path.strip()
    if not app_path:
        return "请提供应用程序名称"
    
    # 智能处理中文应用名称
    suffixes = ['浏览器', '播放器', '编辑器', '软件', '应用', '程序', '工具', '助手', '客户端', '桌面']
    base_name = app_path
    for suffix in suffixes:
        if app_path.endswith(suffix):
            base_name = app_path[:-len(suffix)]
            break
    
    # 智能处理英文应用名称
    english_suffixes = ['app', 'application', 'software', 'tool', 'client', 'desktop']
    base_name_lower = base_name.lower()
    for suffix in english_suffixes:
        if base_name_lower.endswith(suffix):
            base_name = base_name[:-len(suffix)]
            break
    
    # 生成应用程序名称的变体
    app_variants = set()
    
    # 添加原始名称
    app_variants.add(app_path)
    app_variants.add(base_name)
    
    # 添加带 .exe 的变体
    if not app_path.endswith('.exe'):
        app_variants.add(app_path + '.exe')
        app_variants.add(base_name + '.exe')
    
    # 处理空格和连字符
    app_variants.add(app_path.replace(' ', ''))
    app_variants.add(app_path.replace(' ', '-'))
    app_variants.add(app_path.replace(' ', '_'))
    app_variants.add(base_name.replace(' ', ''))
    app_variants.add(base_name.replace(' ', '-'))
    app_variants.add(base_name.replace(' ', '_'))
    
    # 处理大小写变体
    app_variants.add(app_path.lower())
    app_variants.add(app_path.upper())
    app_variants.add(base_name.lower())
    app_variants.add(base_name.upper())
    
    # 转换为列表
    app_variants = list(app_variants)
    
    # 常见应用程序安装目录
    search_dirs = [
        # 系统默认安装目录
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"D:\Program Files",
        r"D:\Program Files (x86)",
        
        # 用户应用目录
        os.path.expanduser(r"~\AppData\Local\Programs"),
        os.path.expanduser(r"~\AppData\Local"),
        os.path.expanduser(r"~\AppData\Roaming"),
        
        # 开始菜单目录
        os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Start Menu\Programs"),
        
        # 桌面
        os.path.expanduser(r"~\Desktop"),
        
        # 常见自定义安装目录
        r"C:\Apps",
        r"D:\Apps",
        r"C:\Software",
        r"D:\Software",
        r"C:\Programs",
        r"D:\Programs",
        r"C:\Applications",
        r"D:\Applications",
        r"C:\Tools",
        r"D:\Tools",
        r"C:\Program Files\Common Files",
        r"C:\Program Files (x86)\Common Files",
        
        # 游戏和娱乐软件目录
        r"C:\Program Files\Steam\steamapps\common",
        r"D:\Program Files\Steam\steamapps\common",
        r"C:\Gaming",
        r"D:\Gaming",
        
        # 开发工具目录
        r"C:\Development",
        r"D:\Development",
        r"C:\Dev",
        r"D:\Dev",
    ]
    
    # 存储所有找到的候选路径
    candidate_paths = []
    
    # 优先搜索可执行文件和快捷方式
    for search_dir in search_dirs:
        if not Path(search_dir).exists():
            continue
            
        for variant in app_variants:
            # 搜索带.exe的可执行文件
            exe_pattern = os.path.join(search_dir, "**", variant)
            try:
                exe_matches = glob.glob(exe_pattern, recursive=True)
                # 过滤掉目录，只保留文件
                exe_files = [m for m in exe_matches if Path(m).is_file()]
                for exe_file in exe_files:
                    # 计算匹配度：路径中包含应用名称的权重更高
                    match_score = 0
                    if base_name.lower() in exe_file.lower():
                        match_score += 10
                    if variant.lower() in exe_file.lower():
                        match_score += 5
                    # 路径越短，权重越高（更可能是直接安装目录）
                    match_score += 100 - len(exe_file) // 10
                    candidate_paths.append((-match_score, exe_file))  # 负号用于排序
            except:
                pass
                
            # 搜索快捷方式
            lnk_pattern = os.path.join(search_dir, "**", variant + '.lnk')
            try:
                lnk_matches = glob.glob(lnk_pattern, recursive=True)
                for lnk_file in lnk_matches:
                    match_score = 0
                    if base_name.lower() in lnk_file.lower():
                        match_score += 8
                    if variant.lower() in lnk_file.lower():
                        match_score += 4
                    candidate_paths.append((-match_score, lnk_file))
            except:
                pass
    
    # 搜索应用程序目录
    for search_dir in search_dirs:
        if not Path(search_dir).exists():
            continue
            
        for variant in app_variants:
            # 搜索应用程序目录
            dir_pattern = os.path.join(search_dir, "**", variant)
            try:
                dir_matches = glob.glob(dir_pattern, recursive=True)
                # 过滤出目录
                app_dirs = [m for m in dir_matches if Path(m).is_dir()]
                for app_dir in app_dirs:
                    # 在目录中查找.exe文件
                    exe_files = list(Path(app_dir).glob("**/*.exe"))
                    for exe_file in exe_files:
                        # 过滤掉明显不是主程序的文件
                        exe_path = str(exe_file)
                        if any(keyword in exe_path.lower() for keyword in ['autopoweroff', 'uninstall', 'setup', 'update', 'helper', 'crash', 'error', 'debug']):
                            continue
                        
                        # 计算匹配度
                        match_score = 0
                        dir_name = Path(app_dir).name
                        exe_name = exe_file.name
                        if dir_name.lower() in exe_name.lower():
                            match_score += 15
                        if base_name.lower() in exe_path.lower():
                            match_score += 10
                        if variant.lower() in exe_path.lower():
                            match_score += 5
                        candidate_paths.append((-match_score, exe_path))
            except:
                pass
    
    # 按匹配度排序，选择最佳候选
    candidate_paths.sort()
    
    # 尝试启动前几个候选
    for _, candidate_path in candidate_paths[:10]:  # 最多尝试前10个
        try:
            if os.name == 'nt':
                process = subprocess.Popen([candidate_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                process = subprocess.Popen([candidate_path], shell=True, detached=True)
            
            # 给进程一点时间启动
            import time
            time.sleep(0.5)
            
            if process.poll() is None:
                return f"正在打开: {candidate_path}"
        except:
            continue
    
    # 尝试通过系统 where 命令查找
    try:
        # 尝试所有变体
        for variant in app_variants:
            if os.name == 'nt':
                # Windows 使用 cmd /c where
                result = subprocess.run(['cmd', '/c', 'where', variant], capture_output=True, text=True, timeout=5)
            else:
                # 其他系统直接使用 where
                result = subprocess.run(['where', variant], capture_output=True, text=True, shell=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                found_paths = result.stdout.strip().split('\n')
                # 过滤出存在的文件
                existing_paths = [p for p in found_paths if Path(p).exists()]
                if existing_paths:
                    found_path = existing_paths[0]
                    if os.name == 'nt':
                        process = subprocess.Popen([found_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    else:
                        process = subprocess.Popen([found_path], shell=True, detached=True)
                    
                    # 给进程一点时间启动
                    import time
                    time.sleep(0.5)
                    
                    if process.poll() is None:
                        return f"正在打开: {found_path}"
    except:
        pass
    
    # 尝试通过 PowerShell 查找（更智能的搜索）
    try:
        # 构建更精确的 PowerShell 命令
        for variant in app_variants:
            # 优先搜索可执行文件
            ps_command = f"""
            $searchPaths = @('C:\', 'D:\')
            $searchPatterns = @('*{0}*.exe', '*{0}*.lnk')
            $results = @()
            
            foreach ($path in $searchPaths) {{
                foreach ($pattern in $searchPatterns) {{
                    try {{
                        $items = Get-ChildItem -Path $path -Include ($pattern -f '{0}') -Recurse -ErrorAction SilentlyContinue | 
                                 Where-Object {{ $_.Name -notlike '*uninstall*' -and $_.Name -notlike '*setup*' -and $_.Name -notlike '*update*' }}
                        $results += $items
                    }} catch {{}}
                }}
            }}
            
            # 按路径长度排序，优先选择更具体的路径
            $results | Sort-Object {{ $_.FullName.Length }} | Select-Object -First 3 | Format-List FullName
            """
            
            result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, shell=True, timeout=15)
            if result.stdout.strip():
                # 解析 PowerShell 输出
                lines = result.stdout.strip().split('\n')
                found_paths = []
                for line in lines:
                    if line.strip().startswith('FullName'):
                        found_path = line.split(':', 1)[1].strip()
                        if Path(found_path).exists():
                            found_paths.append(found_path)
                
                if found_paths:
                    for found_path in found_paths:
                        if os.name == 'nt':
                            process = subprocess.Popen([found_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                        else:
                            process = subprocess.Popen([found_path], shell=True, detached=True)
                        
                        # 给进程一点时间启动
                        import time
                        time.sleep(0.5)
                        
                        if process.poll() is None:
                            return f"正在打开: {found_path}"
    except Exception as e:
        print(f"PowerShell 查找失败: {str(e)}")
        pass
    
    # 尝试通过 start 命令打开（适用于已注册的应用程序）
    try:
        if os.name == 'nt':
            # 使用 start 命令打开，正确处理带空格的应用名称
            process = subprocess.Popen(f"start \"{app_path}\"", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # 给进程一点时间启动
            import time
            time.sleep(1)
            
            if process.poll() is None:
                return f"正在打开: {app_path}"
        else:
            # 其他系统使用 open 命令
            process = subprocess.Popen(f"open \"{app_path}\"", shell=True, detached=True)
            
            # 给进程一点时间启动
            import time
            time.sleep(1)
            
            if process.poll() is None:
                return f"正在打开: {app_path}"
    except Exception as e:
        print(f"Start 命令失败: {str(e)}")
        pass
    
    # 尝试通过 explorer 命令打开
    try:
        if os.name == 'nt':
            # 使用 explorer 命令打开，正确处理带空格的应用名称
            process = subprocess.Popen(f"explorer \"{app_path}\"", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # 给进程一点时间启动
            import time
            time.sleep(0.5)
            
            if process.poll() is None:
                return f"正在打开: {app_path}"
        else:
            # 其他系统使用 xdg-open 命令
            process = subprocess.Popen(f"xdg-open \"{app_path}\"", shell=True, detached=True)
            
            # 给进程一点时间启动
            import time
            time.sleep(0.5)
            
            if process.poll() is None:
                return f"正在打开: {app_path}"
    except Exception as e:
        print(f"Explorer 命令失败: {str(e)}")
        pass
    
    # 尝试通过 Windows 注册表查找（仅 Windows）
    if os.name == 'nt':
        try:
            import winreg
            # 常见注册表路径
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
                                for variant in app_variants:
                                    if variant.lower() in subkey_name.lower():
                                        subkey = winreg.OpenKey(key, subkey_name)
                                        try:
                                            # 读取默认值（通常是可执行文件路径）
                                            default_value, _ = winreg.QueryValueEx(subkey, "")
                                            if default_value and Path(default_value).exists():
                                                if os.name == 'nt':
                                                    process = subprocess.Popen([default_value], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                                                else:
                                                    process = subprocess.Popen([default_value], shell=True, detached=True)
                                                
                                                # 给进程一点时间启动
                                                import time
                                                time.sleep(0.5)
                                                
                                                if process.poll() is None:
                                                    return f"正在打开: {default_value}"
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
    
    # 智能错误处理和用户反馈
    # 检查是否是常见的应用程序
    common_app_names = ['qq音乐', '微信', '记事本', '计算器', '画图', 'word', 'excel', 'powerpoint', 'edge', 'chrome', 'vscode', 'pycharm', 'xmind', 'mindmaster', 'photoshop', 'illustrator', 'audition', 'premiere', 'aftereffects', 'qq', 'tim', 'thunder', 'kugou', 'kuwo', 'netease', '夸克']
    
    # 检查输入是否是常见应用
    input_lower = app_path.lower()
    is_common_app = any(app in input_lower for app in common_app_names)
    
    if is_common_app:
        return f"未找到应用程序: {app_path}\n\n可能的原因：\n1. 应用程序未安装\n2. 安装路径不在常见位置\n3. 应用程序名称拼写错误\n\n请尝试提供完整的应用程序路径，或确认应用程序已正确安装。"
    else:
        return f"未找到应用程序: {app_path}\n\n建议：\n1. 检查应用程序名称是否拼写正确\n2. 尝试提供完整的应用程序路径（.exe 文件）\n3. 确认应用程序已正确安装到系统中"

# 测试应用程序列表
test_apps = [
    "notepad",  # 记事本（英文）
    "记事本",    # 记事本（中文）
    "calc",     # 计算器（英文）
    "计算器",    # 计算器（中文）
    "mspaint",  # 画图（英文）
    "画图",     # 画图（中文）
    "edge",     # Edge 浏览器（英文）
    "浏览器",    # 浏览器（中文）
    "chrome",   # Chrome 浏览器（英文）
    "微信",     # 微信（中文）
    "qq",       # QQ（英文）
    "vscode",   # VS Code（英文）
    "代码",     # 代码编辑器（中文）
    "xmind",    # XMind（英文）
    "思维导图",  # 思维导图（中文）
    "photoshop",# Photoshop（英文）
    "ps",       # Photoshop 简写（英文）
    "夸克",     # 夸克浏览器（中文）
    "kuaike",   # 夸克浏览器（拼音）
]

print("测试 open_application 工具...")
print("=" * 60)

for app in test_apps:
    print(f"\n测试应用: {app}")
    print("-" * 40)
    try:
        result = test_open_application(app)
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {str(e)}")

print("\n" + "=" * 60)
print("测试完成！")
