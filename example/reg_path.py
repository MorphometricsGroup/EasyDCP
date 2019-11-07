import sys
import os
cwd = os.getcwd()
package_path = os.path.abspath(os.path.join(cwd, '..'))
sys.path.append(package_path)