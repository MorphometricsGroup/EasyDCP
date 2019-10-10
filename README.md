# 3Dphenotyping

An auto python scripts for batch image processing, and common phenotype traits extraction from 3D point clouds.
This script handles multiple sets of images taken in same environment, e.g. timescale photos of a plot or many plants photographed in the same place.

## Installation

unzip all files to the `plugins` folder in Agisoft installation paths, e.g. `C:\Program Files\Agisoft\Metashape Pro\plugins\3Dphenotyping`

Right click the `install_packages.bat`，and edit the start paths to your Agisoft path:

`X:\Your_path_to\Agisoft\Metashape Pro\python\python.exe" -m pip install -r requirements.txt`

And then run `install_packages.bat` in Administrator permission, the batch file will automatically install all the packages required for this project.

Add Metashape program folder to Windows PATH
See https://helpdeskgeek.com/windows-10/add-windows-path-environment-variable/

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