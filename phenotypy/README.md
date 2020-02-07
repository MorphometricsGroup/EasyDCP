<h1>Phenotypy</h1>
A  python package for agricultural phenotype traits extraction from 3D point clouds.

# Getting Started
## Installing from PyPI
In the **future** release, **will** add support of PyPI installation.

```bash
pip install phenotypy
```
## Using source codes
1. Download and unzip Phenotypy folders to any paths, e.g. `D:\Program\phenotypy`

2. Open your environment or python IDE, install the `requirements.txt` in **Administrator permission** by:

   `(YourEnv) D:\Program\phenotypy\> pip install -r requirements.txt`

3. Before `import phenotypy` in your code, you need to write the following code in front:

   ```python
   import sys
   sys.path.insert(0, r'D:/Program/')  # not Program/Phenotypy full path
   # then you can import to use
   import phenotypy as pnt
   ```

### Installation Errors
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
pip install "phenotypy/wheels/Shapely-1.6.4.post2-cp36-cp36m-win_amd64.whl"
```

# Tutorial

## Basic

To be continued

## Advanced

To be continued



# APIs

A wrapper for quick use

**Classes**

|name|Description|
|---|---|
|`Classifier`|...|
|`Plot`|...|
|`Plant`|...|

**Functions**

| name         | Description |
| ------------ | ----------- |
| [`read_ply`](#read_ply)   |             |
| `read_plys`  |             |
| `read_shp`   |             |
| `read_shps`  |             |
| `read_xyz`   |             |
| `merge_pcd`  |             |
| `pcd2dxm`    |             |
| `pcd2binary` |             |



## pnt.pcd_tools

**Functions**

| name                   | description |
| ---------------------- | ----------- |
| `build_cut_boundary`   |             |
| `calculate_xyz_volume` |             |
| `clip_pcd`             |             |
| `convex_hull2d`        |             |
| `merge_pcd`            |             |
| `pcd2binary`           |             |
| `pcd2dxm`              |             |
| `pcd2voxel`            |             |
| `round2val`            |             |


## pnt.io

**functions**

| name            | description |
| --------------- | ----------- |
| `pcd.read_ply`  |             |
| `pcd.read_plys` |             |
| `pcd.write_ply` |             |
| `shp.read_shp`  |             |
| `shp.read_shps` |             |
| `shp.read_xyz`  |             |

<h4 id="read_ply">pnt.io.pcd.read_ply(args)</h4>
Function to read point cloud ply file

> Parameters

&nbsp; &nbsp; &nbsp; &nbsp; **filename** (str) - Path to file

> Returns

&nbsp; &nbsp; &nbsp; &nbsp; open3d.geometry.PointCloud



## pnt.plotting



## pnt.geometry

