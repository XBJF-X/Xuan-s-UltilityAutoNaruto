# 获取当前的PATH变量
import os

from StaticFunctions import get_real_path

original_path = os.environ.get('PATH')
print(f"Original PATH: {original_path}")

os.environ['PATH'] = os.pathsep.join([get_real_path('bin/adb'), os.environ.get('PATH', '')])
# 验证修改后的PATH变量
modified_path = os.environ.get('PATH')
print(f"Modified PATH: {modified_path}")