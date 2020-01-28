# 3Dphenotyping

An auto python scripts for batch image processing, and common phenotype traits extraction from 3D point clouds.
This script handles multiple sets of images taken in same environment, e.g. timescale photos of a plot or many plants photographed in the same place.

## Installation

In the future release, will add support of PyPI installation.

```bash
pip install phenotypy
```

Currently, it can be used as packages in the following way:

1. Download and unzip phenotypy folders to any paths, e.g. `D:\Program\phenotypy`

2. Open your environment or python IDE, install the `requirements.txt` in **Administrator permission** by:

   `(YourEnv) D:\Program\phenotypy\> pip install -r requirements.txt`

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

3. Before `import phenotypy` in your code, you need to write the following code in front:

   ```python
   import sys
   sys.path.insert(0, r'D:/Program/')  # not Program/Phenotypy full path
   # then you can import to use
   import phenotypy as pnt
   ```

   

## Create training data

Use GIMP to create fore.png and back.png
1. Use Free Select Tool to select plant parts only - Maybe 3 different plants is enough to represent them all eg. one light green, one dark green, one yellowing
	* Deselect Antialiasing in Free Select settings pane
	* Select '1. Pixel (3 x 3) in Brushes tab
2. Copy the selection and create a new file, PNG *with transparency*
	* Under Advanced Options in 'Create a New Image' dialog, select Fill with: Transparency
3. Save as fore.png
4. Repeat steps 1-3 with background samples and save as back.png
* Maybe we can have example fore.png and back.png in github

## Functions

**Agisoft auto control**

* [ ] Auto match key points
* [ ] Auto points cloud generation
* [ ] Auto points cloud output
* [ ] Batch processing

**Phenotype Processing**

* [ ] Decision tree classifier for plant pixel classification
* [ ] Cluster algorithm for individual plant segmentation
* [ ] Plant width, length, and height calculation

## Using Agisoft auto control

open pipeline-all.py
-change 'path_folders' to the path containing the folders of images
-change 'blur_threshold' to desired value. Pipeline will disable all images with Agisoft image quality below the blur_threshold.
-set ignore_gps, align_ground, and use_scalebars depending on need

Ensure folder structure matches intended format
- only folders in root folder (path_folders), no files in root
- 'skip' folder contains scalebars.csv if needed