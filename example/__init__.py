import sys
import os
cwd = os.getcwd()
print(f'[__init__]Append "{cwd}" to system.path')
sys.path.insert(0, cwd)
