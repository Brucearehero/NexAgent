"""
NexAgent - Shell 工具
打开应用程序、执行系统命令等
"""
import subprocess
import os
from pathlib import Path
from langchain_core.tools import tool
from agent.core import check_tool_stop, AgentStoppedException


@tool
def open_vscode(directory: str = ".") -> str:
    """
    打开 VS Code

    Args:
        directory: 要打开的目录路径（默认当前目录）

    Returns:
        操作结果
    """
    try:
        path = Path(directory).resolve()
        if not path.exists():
            return f"目录不存在: {directory}"

        # 尝试使用 code 命令
        subprocess.Popen(["code", str(path)], shell=True, detached=True)
        return f"正在打开 VS Code: {path}"
    except Exception as e:
        return f"打开 VS Code 失败: {str(e)}"


@tool
def open_pycharm(directory: str = ".") -> str:
    """
    打开 PyCharm

    Args:
        directory: 要打开的目录路径（默认当前目录）

    Returns:
        操作结果
    """
    try:
        path = Path(directory).resolve()
        if not path.exists():
            return f"目录不存在: {directory}"

        # 常见 PyCharm 安装路径
        pycharm_paths = [
            r"C:\\Program Files\\JetBrains\\PyCharm\\bin\\pycharm64.exe",
            r"C:\\Program Files (x86)\\JetBrains\\PyCharm\\bin\\pycharm64.exe",
            os.path.expanduser(r"~\\AppData\\Local\\JetBrains\\Toolbox\\apps\\PyCharm\\*\\bin\\pycharm64.exe"),
        ]

        for pycharm_path in pycharm_paths:
            if "*" in pycharm_path:
                import glob
                matches = glob.glob(pycharm_path)
                if matches:
                    pycharm_path = matches[-1]
                    subprocess.Popen([pycharm_path, str(path)], shell=True, detached=True)
                    return f"正在打开 PyCharm: {path}"
            elif Path(pycharm_path).exists():
                subprocess.Popen([pycharm_path, str(path)], shell=True, detached=True)
                return f"正在打开 PyCharm: {path}"

        return "未找到 PyCharm，请确认已安装 PyCharm"
    except Exception as e:
        return f"打开 PyCharm 失败: {str(e)}"


@tool
def open_application(app_path: str) -> str:
    """
    打开任意应用程序

    Args:
        app_path: 应用程序的路径（.exe 文件路径）或应用程序名称（如 "QQ音乐"）

    Returns:
        操作结果
    """
    try:
        check_tool_stop()
        # 尝试直接使用路径
        path = Path(app_path).resolve()
        if path.exists():
            # Windows 兼容的启动方式
            if os.name == 'nt':
                # Windows 使用 creationflags
                process = subprocess.Popen([str(path)], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # 其他系统使用 detached
                process = subprocess.Popen([str(path)], shell=True, detached=True)
            # 验证进程是否成功启动
            if process.poll() is None:
                return f"正在打开: {app_path}"
            else:
                return f"打开应用程序失败: 进程启动失败"

        # 智能生成应用程序名称变体
        app_variants = set()
        
        # 基本变体
        base_name = app_path
        if base_name.endswith('.exe'):
            base_name = base_name[:-4]
        
        # 添加各种大小写变体
        variants = [
            base_name,
            base_name.lower(),
            base_name.upper(),
            base_name.capitalize(),
        ]
        
        # 添加带.exe的变体
        for variant in variants:
            app_variants.add(variant)
            app_variants.add(variant + '.exe')
        
        # 智能处理中文应用名称
        # 移除常见的后缀词
        suffixes = ['浏览器', '播放器', '编辑器', '软件', '应用', '程序', '工具', '助手', '客户端', '桌面']
        for suffix in suffixes:
            if base_name.endswith(suffix):
                base_name_no_suffix = base_name[:-len(suffix)]
                app_variants.add(base_name_no_suffix)
                app_variants.add(base_name_no_suffix + '.exe')
                # 添加大小写变体
                app_variants.add(base_name_no_suffix.lower())
                app_variants.add(base_name_no_suffix.lower() + '.exe')
                app_variants.add(base_name_no_suffix.upper())
                app_variants.add(base_name_no_suffix.upper() + '.exe')
                app_variants.add(base_name_no_suffix.capitalize())
                app_variants.add(base_name_no_suffix.capitalize() + '.exe')
                break
        
        # 智能处理英文应用名称
        # 移除常见的后缀词
        english_suffixes = ['app', 'application', 'software', 'tool', 'client', 'desktop', 'player', 'browser', 'editor']
        base_name_lower = base_name.lower()
        for suffix in english_suffixes:
            if base_name_lower.endswith(suffix):
                base_name_no_suffix = base_name[:-len(suffix)]
                # 移除可能的空格
                base_name_no_suffix = base_name_no_suffix.strip()
                if base_name_no_suffix:
                    app_variants.add(base_name_no_suffix)
                    app_variants.add(base_name_no_suffix + '.exe')
                    # 添加大小写变体
                    app_variants.add(base_name_no_suffix.lower())
                    app_variants.add(base_name_no_suffix.lower() + '.exe')
                    app_variants.add(base_name_no_suffix.upper())
                    app_variants.add(base_name_no_suffix.upper() + '.exe')
                    app_variants.add(base_name_no_suffix.capitalize())
                    app_variants.add(base_name_no_suffix.capitalize() + '.exe')
                break
        
        # 添加更多变体
        # 去除空格的变体
        base_name_no_spaces = base_name.replace(' ', '')
        if base_name_no_spaces != base_name:
            app_variants.add(base_name_no_spaces)
            app_variants.add(base_name_no_spaces + '.exe')
            # 添加大小写变体
            app_variants.add(base_name_no_spaces.lower())
            app_variants.add(base_name_no_spaces.lower() + '.exe')
        
        # 添加连字符和下划线变体
        base_name_hyphenated = base_name.replace(' ', '-')
        if base_name_hyphenated != base_name:
            app_variants.add(base_name_hyphenated)
            app_variants.add(base_name_hyphenated + '.exe')
        
        base_name_underscored = base_name.replace(' ', '_')
        if base_name_underscored != base_name:
            app_variants.add(base_name_underscored)
            app_variants.add(base_name_underscored + '.exe')
        
        # 常见应用程序名称映射（作为补充）
        common_apps = {
            'qq音乐': ['QQ音乐', 'QQMusic', 'qqmusic'],
            '微信': ['WeChat', 'wechat'],
            '记事本': ['notepad'],
            '计算器': ['calc'],
            '画图': ['mspaint'],
            'word': ['winword'],
            'excel': ['excel'],
            'powerpoint': ['powerpnt', 'PPT'],
            'edge': ['msedge'],
            'chrome': ['Google Chrome'],
            'vscode': ['code', 'VS Code'],
            'pycharm': ['PyCharm'],
            'xmind': ['XMind', 'XMind.exe'],
            'mindmaster': ['MindMaster', 'MindMaster.exe'],
            'photoshop': ['Photoshop', 'Photoshop.exe', 'PS', 'PS.exe'],
            'illustrator': ['Illustrator', 'Illustrator.exe', 'AI', 'AI.exe'],
            'audition': ['Audition', 'Audition.exe', 'AU', 'AU.exe'],
            'premiere': ['Premiere', 'Premiere.exe', 'PR', 'PR.exe'],
            'aftereffects': ['After Effects', 'AfterEffects', 'AE', 'AE.exe'],
            'qq': ['QQ', 'QQ.exe'],
            'tim': ['TIM', 'TIM.exe'],
            'thunder': ['Thunder', 'Thunder.exe', '迅雷', '迅雷.exe'],
            'kugou': ['Kugou', 'Kugou.exe', '酷狗', '酷狗.exe'],
            'kuwo': ['Kuwo', 'Kuwo.exe', '酷我', '酷我.exe'],
            'netease': ['Netease', 'Netease.exe', '网易云音乐', '网易云音乐.exe'],
            '夸克': ['Quark', 'quark', '夸克浏览器', 'Quark.exe', 'quark.exe'],
        }
        
        # 添加常见应用的变体（作为补充）
        for key, values in common_apps.items():
            if key in base_name.lower():
                for value in values:
                    app_variants.add(value)
                    if not value.endswith('.exe'):
                        app_variants.add(value + '.exe')
        
        # 转换为列表
        app_variants = list(app_variants)

        check_tool_stop()

        # 读取电脑本地的应用总目录
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
                                    check_tool_stop()
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
                check_tool_stop()
                if Path(start_menu_path).exists():
                    for root, dirs, files in os.walk(start_menu_path):
                        check_tool_stop()
                        for file in files:
                            if file.endswith('.lnk'):
                                lnk_path = os.path.join(root, file)
                                # 尝试解析快捷方式
                                try:
                                    import win32com.client  # type: ignore
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
                        check_tool_stop()
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
                check_tool_stop()
                if Path(path_dir).exists():
                    try:
                        for file in os.listdir(path_dir):
                            check_tool_stop()
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
        
        # 获取已安装的应用程序列表
        installed_applications = get_installed_applications()
        
        check_tool_stop()
        
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

        # 搜索应用程序
        import glob
        
        # 存储所有找到的候选路径
        candidate_paths = []
        
        # 1. 首先从已安装的应用程序列表中查找
        if installed_applications:
            for app_name, app_path in installed_applications:
                check_tool_stop()
                # 计算匹配度
                match_score = 0
                app_name_lower = app_name.lower()
                app_path_lower = app_path.lower()
                
                # 检查应用名称是否匹配
                for variant in app_variants:
                    variant_lower = variant.lower()
                    if variant_lower in app_name_lower:
                        match_score += 20  # 名称匹配权重最高
                    if variant_lower in app_path_lower:
                        match_score += 10  # 路径匹配权重次之
                
                # 检查基础名称是否匹配
                base_name_lower = base_name.lower()
                if base_name_lower in app_name_lower:
                    match_score += 15
                if base_name_lower in app_path_lower:
                    match_score += 8
                
                # 如果匹配度足够高，添加到候选列表
                if match_score > 5:
                    candidate_paths.append((-match_score, app_path))
        
        # 2. 然后进行传统的文件系统搜索
        # 优先搜索可执行文件和快捷方式
        for search_dir in search_dirs:
            check_tool_stop()
            if not Path(search_dir).exists():
                continue
                
            for variant in app_variants:
                check_tool_stop()
                # 搜索带.exe的可执行文件
                exe_pattern = os.path.join(search_dir, "**", variant)
                try:
                    exe_matches = glob.glob(exe_pattern, recursive=True)
                    # 过滤掉目录，只保留文件
                    exe_files = [m for m in exe_matches if Path(m).is_file()]
                    for exe_file in exe_files:
                        check_tool_stop()
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
                        check_tool_stop()
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
            check_tool_stop()
            if not Path(search_dir).exists():
                continue
                
            for variant in app_variants:
                check_tool_stop()
                # 搜索应用程序目录
                dir_pattern = os.path.join(search_dir, "**", variant)
                try:
                    dir_matches = glob.glob(dir_pattern, recursive=True)
                    # 过滤出目录
                    app_dirs = [m for m in dir_matches if Path(m).is_dir()]
                    for app_dir in app_dirs:
                        check_tool_stop()
                        # 在目录中查找.exe文件
                        exe_files = list(Path(app_dir).glob("**/*.exe"))
                        for exe_file in exe_files:
                            check_tool_stop()
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
            check_tool_stop()
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
                check_tool_stop()
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
                check_tool_stop()
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
                            check_tool_stop()
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
            check_tool_stop()
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
            check_tool_stop()
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
                    check_tool_stop()
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                        try:
                            i = 0
                            while True:
                                check_tool_stop()
                                try:
                                    subkey_name = winreg.EnumKey(key, i)
                                    for variant in app_variants:
                                        if variant.lower() in subkey_name.lower():
                                            subkey = winreg.OpenKey(key, subkey_name)
                                            try:
                                                path = winreg.QueryValue(subkey, None)
                                                if Path(path).exists():
                                                    process = subprocess.Popen([path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                                                    if process.poll() is None:
                                                        return f"正在打开: {path}"
                                            except:
                                                pass
                                            finally:
                                                winreg.CloseKey(subkey)
                                    i += 1
                                except OSError:
                                    break
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
    except AgentStoppedException:
        return "[已停止] 用户请求中断了执行。"
    except Exception as e:
        error_msg = str(e)
        # 智能错误信息处理
        if 'permission' in error_msg.lower():
            return f"打开应用程序失败: 权限不足\n\n请以管理员身份运行应用程序，或检查文件权限设置。"
        elif 'not found' in error_msg.lower() or '不存在' in error_msg:
            return f"打开应用程序失败: 文件不存在\n\n请检查应用程序路径是否正确，或确认应用程序已正确安装。"
        elif 'access denied' in error_msg.lower():
            return f"打开应用程序失败: 访问被拒绝\n\n请检查文件权限设置，或以管理员身份运行应用程序。"
        else:
            return f"打开应用程序失败: {error_msg}\n\n请检查应用程序是否已正确安装，或尝试提供完整的应用程序路径。"


@tool
def open_in_explorer(path: str = ".") -> str:
    """
    在文件资源管理器中打开目录

    Args:
        path: 目录路径（默认当前目录）

    Returns:
        操作结果
    """
    try:
        full_path = Path(path).resolve()
        if not full_path.exists():
            return f"路径不存在: {path}"

        subprocess.Popen(f"explorer {full_path}", shell=True)
        return f"已在文件资源管理器中打开: {full_path}"
    except Exception as e:
        return f"打开资源管理器失败: {str(e)}"


@tool
def get_system_info() -> str:
    """
    获取系统基本信息

    Returns:
        系统信息
    """
    import platform
    import os

    info = [
        f"系统: {platform.system()}",
        f"版本: {platform.version()}",
        f"架构: {platform.machine()}",
        f"处理器: {platform.processor()}",
        f"Python 版本: {platform.python_version()}",
        f"当前目录: {os.getcwd()}",
        f"用户目录: {os.path.expanduser('~')}",
    ]

    return "\n".join(info)


def get_shell_tools() -> list:
    """获取所有 Shell 工具"""
    return [
        open_vscode,
        open_pycharm,
        open_application,
        open_in_explorer,
        get_system_info,
    ]
