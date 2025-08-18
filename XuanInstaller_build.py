import os
import shutil
import subprocess
import sys
from pathlib import Path
import time
from StaticFunctions import get_real_path


def change_version(new_version, file_path=get_real_path("bin/XuanInstaller.nsi")):
    """
        更新文本文件中 PRODUCT_VERSION 定义
        :param file_path: 文本文件路径
        :param new_version: 新版本号字符串 (如 "1.2.3")
        """
    # 构建要替换的新行
    new_line = f'!define PRODUCT_VERSION "{new_version}"'
    updated = False

    try:
        # 读取文件所有行
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 查找并替换目标行
        for i, line in enumerate(lines):
            if line.strip().startswith('!define PRODUCT_VERSION'):
                lines[i] = new_line + '\n'  # 确保有换行符
                updated = True
                print(f"找到并替换第 {i + 1} 行: {line.strip()} → {new_line}")
                break  # 找到第一个匹配项后停止

        # 如果没有找到匹配行
        if not updated:
            print(f"警告: 文件中未找到 !define PRODUCT_VERSION 行")
            # 可选: 在文件末尾添加新行
            # lines.append(new_line + '\n')
            # updated = True

        # 如果有更改，写回文件
        if updated:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            print(f"文件更新成功: {file_path}")
        else:
            print("文件未更改")

    except Exception as e:
        print(f"处理文件时出错: {e}")


def main(version):
    # 配置路径
    py_project = Path(get_real_path(""))
    nsis_project = Path(get_real_path("bin"))
    upx_dir = Path(get_real_path("bin/upx-5.0.1-win64"))
    venv_dir = py_project / ".venv"

    # 虚拟环境中的 Python 解释器
    venv_python = venv_dir / "Scripts" / "python.exe"

    # 确保目录存在
    if not py_project.exists():
        print(f"错误: Python项目目录不存在 - {py_project}")
        sys.exit(1)

    if not nsis_project.exists():
        print(f"错误: NSIS项目目录不存在 - {nsis_project}")
        sys.exit(1)

    try:
        # 2. 使用NSIS构建安装包
        print("\n" + "=" * 50)
        print("步骤 2: 构建NSIS安装程序")
        change_version(version)

        # 直接使用makensis命令（假设已在PATH中）
        nsis_cmd = [get_real_path("bin/NSIS/Bin/makensis.exe"), str(nsis_project / "XuanInstaller.nsi")]
        print(f"执行命令: {' '.join(nsis_cmd)}")

        # 在NSIS项目目录执行命令
        subprocess.run(nsis_cmd, cwd=nsis_project, check=True)
        print("NSIS 构建成功")

        # 3. 移动生成的安装程序
        print("\n" + "=" * 50)
        print("步骤 3: 移动安装程序到发布目录")

        installer_src = nsis_project / "XuanInstaller.exe"
        if not installer_src.exists():
            raise FileNotFoundError(f"安装程序未生成: {installer_src}")

        # 创建release目录（如果不存在）
        release_dir = py_project / "release"
        release_dir.mkdir(parents=True, exist_ok=True)

        installer_dest = release_dir / f"XuanInstaller_V{version}.exe"

        # 移动文件
        shutil.move(str(installer_src), str(installer_dest))
        print(f"安装程序已移动到: {installer_dest}")

        # 4. 清理临时文件
        print("\n" + "=" * 50)
        print("步骤 4: 清理构建临时文件")

        # 删除dist目录
        for dir_name in ["dist"]:
            dir_path = py_project / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"已删除目录: {dir_path}")

        # 完成消息
        print("\n" + "=" * 50)
        print("[所有操作已完成]")
        print(f"安装程序位置: {installer_dest}")

    except subprocess.CalledProcessError as e:
        print(f"\n错误: 命令执行失败 (返回码 {e.returncode})")
        print(f"命令: {e.cmd}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n错误: 文件或目录未找到 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n未知错误: {e}")
        sys.exit(1)


def run_cz_bump(use_shell=False):
    py_project = Path(get_real_path(""))
    venv_dir = py_project / ".venv"

    # 虚拟环境中的 Python 解释器
    cz_path = venv_dir / "Scripts" / "cz.exe"

    # 确保目录存在
    if not py_project.exists():
        print(f"错误: Python项目目录不存在 - {py_project}")
        sys.exit(1)

    # 验证虚拟环境中的Python解释器
    if not cz_path.exists():
        raise FileNotFoundError(f"cz.exe未找到: {cz_path}")

    cmd = f"{cz_path} bump"
    # 执行 cz bump 命令
    # 调试信息
    print(f"[调试] 执行命令: {cmd}")
    print(f"[调试] 使用shell: {use_shell}")

    try:
        # 执行命令，显式指定编码为utf-8
        result = subprocess.run(
            cmd,
            cwd=".",
            capture_output=True,
            text=True,
            encoding="utf-8",  # 显式指定UTF-8编码
            errors="replace",  # 替换无法解码的字符
            shell=use_shell
        )

        # 安全获取输出，处理可能的None值
        stdout = result.stdout or ""
        stderr = result.stderr or ""

        # 合并标准输出和错误输出
        full_output = (stdout + stderr)

        # 检查关键字
        keyword_found = "increment detected:" in full_output

        return {
            "returncode": result.returncode,
            "full_output": full_output,
            "keyword_found": keyword_found
        }

    except UnicodeDecodeError as e:
        print(f"编码错误: 无法解码子进程输出 - {e}")
        # 返回部分信息，避免程序崩溃
        return {
            "returncode": result.returncode if 'result' in locals() else -1,
            "full_output": "解码输出时出错，可能包含非UTF-8字符",
            "keyword_found": False
        }
    except Exception as e:
        print(f"执行命令时发生未知错误: {e}")
        return {
            "returncode": -1,
            "full_output": f"执行命令时出错: {str(e)}",
            "keyword_found": False
        }


if __name__ == "__main__":
    result = run_cz_bump(True)
    print(f"命令返回代码: {result['returncode']}")
    # 只打印输出的前500个字符（避免大量输出）
    print(result['full_output'][:500] + ('...' if len(result['full_output']) > 500 else ''))

    # 设置控制台编码为 UTF-8 (等效于 chcp 65001)
    os.system("chcp 65001 > nul")
    from _version import __version__
    print(f"版本更新为：v{__version__}")
    main(__version__)
