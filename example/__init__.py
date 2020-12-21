import sys
import os
cwd = os.getcwd()
'''
package_path = os.path.abspath(cwd.split('phenotypy')[0])
<<<<<<< Updated upstream
print(f'[__init__]Append "{package_path}" to system.path')
sys.path.insert(0, package_path)
=======
print(f'[Pnt][__init__]Append "{package_path}" to system.path')
sys.path.insert(0, package_path)
'''
print(f'[Pnt][__init__]Append "{cwd}" to system.path')
sys.path.insert(0, cwd)
>>>>>>> Stashed changes
