# About EasyPCP
A python package for agricultural phenotype traits extraction from 3D point clouds.

## Core features

An auto python script for high throughput phenotype traits extraction of common container plants from 2D image sets via 3D reconstruction and measurement of 3D point clouds.
This script handles multiple sets of images taken in same environment, e.g. timescale photos of a plot or many plants photographed in the same place in several groups.

- Measure plant height, long and short axis, projected leaf area
- Batch processing multiple image sets

## Functions

**EasyPCP Point cloud creation**

* [ ] Auto match key points
* [ ] Auto point cloud generation
* [ ] Auto point cloud export to .ply
* [ ] Batch processing

**EasyPCP Point cloud analysis**

* [ ] Decision tree classifier for plant pixel classification
* [ ] Cluster algorithm for individual plant segmentation
* [ ] Plant width, length, and height calculation
* [ ] Plant projected leaf area calculation

## Resources

To be continued

# Getting Started

## Installing from PyPI [currently not supported]

In the **future** release, **will** add support of PyPI installation.

```bash
pip install easypcp
```

## Installing from source code

1. Download and unzip easypcp folders to any paths, e.g. `D:\Program\easypcp`

2. Open your environment or python IDE, install the `requirements.txt` in **Administrator permission** by:

   `(YourEnv) D:\Program\easypcp\> pip install -r requirements.txt`

3. Before the line containing `import easypcp` in your code, you need to write the following code in front: *(see `example/batch.py` for example)*

   ```python
   import sys
   sys.path.insert(0, r'D:/Program/')  # not Program/easypcp full path
   # then you can import easypcp for use
   import easypcp as pcp
   ```

## Installation Errors

### Shapely

Please note, if meet `shapely` errors on windows platform:

```bash
Collecting Shapely
  Using cached Shapely-1.5.17.tar.gz
    Complete output from command python setup.py egg_info:
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "C:\Users\AppData\Local\Temp\pip-build-mwuxcain\Shapely\setup.py", line 38, in <module>
        from shapely._buildcfg import geos_version_string, geos_version, \
      File "C:\Users\AppData\Local\Temp\pip-build-mwuxcain\Shapely\shapely\_buildcfg.py", line 200, in <module>
        lgeos = CDLL("geos.dll")
      File "C:\Users\Anaconda3\lib\ctypes\__init__.py", line 344, in __init__
        self._handle = _dlopen(self._name, mode)
    OSError: [WinError 126] The specified module could not be found
    ----------------------------------------
Command "python setup.py egg_info" failed with error code 1 in C:\Users\
```

please download shapely wheel from [http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely](http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely) and then using command line to install:

```bash
pip install "easypcp/wheels/Shapely-1.6.4.post2-cp36-cp36m-win_amd64.whl"
```

### Open3d import errors

```python
Traceback (most recent call last):
	File "", line 1, in
	File "C:\Python37\lib\site-packages\open3d_init_.py", line 28, in
	from .open3d import * # py2 py3 compatible
ImportError: DLL load failed: The specified module could not be found.
```

Please refer this link to solve this problem:https://github.com/intel-isl/Open3D/issues/979

The author solve this by installing `Microsoft Visual C++ Redistributable for Visual Studio 2015, 2017 and 2019`  followed by previous link. Quick download links: https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads

