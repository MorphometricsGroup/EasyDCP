# EasyDCP_Analysis

Materials: 

Point cloud files (.ply) from EasyDCP_Creation step

GIMP, Photoshop or equivalent software

Known height of container (mm) or ground offset height.

## (a) Setup

Materials: GIMP or equivalent software.

**Use GIMP to create training data**

1. Use Free Select Tool to select plant parts only - Use a representative sample. Maybe 3 different plants is enough to represent them all e.g. one light green, one dark green, different light conditions, etc.
	* Deselect Antialiasing in Free Select settings pane
	* Select '1. Pixel (3 x 3) in Brushes tab
2. Copy the selection and create a new file, PNG *with transparency*
	* Under Advanced Options in 'Create a New Image' dialog, select Fill with: Transparency
3. Save as fore.png
4. Repeat steps 1-3 with background samples and save as back.png

* See example fore.png and back.png in `/example`

## (b) Running EasyDCP_Analysis

Materials:

- Folder containing .ply point cloud files output by previous step, EasyDCP_Creation
- training data created in previous step "(a) Setup"

Control EasyDCP via API using python script in your python 3.7 environment as described in Installation documentation (heading.md). Several .py files are provided in /example/ as examples of simple scripts to control EasyDCP. See documentation (api.md) for details on controlling EasyDCP via python.

Configure EasyDCP before launching:

- Ensure your .py script points to correct training data and point cloud folder. *Ensure `container_ht` is correctly set.* 

- Before the line containing `import easydcp` in your code, you need to write the following code in front: *(see `example/analysis.py` for example)* **or batch.py?!**

  ```python
  import __init__
  import easydcp as dcp
  ```

- Default `eps_points = 10`. Higher value may be used if segmentation fails, such as one plant being wrongly divided in two segments. Recommend trying 13. Higher `eps_points` value may dramatically increase CPU processing time. 

**Execute your.py file using python , using 3Dphenotyping root folder as working directory:**

`(easydcp37) C:\Users\Alex\Documents\GitHub\3Dphenotyping>python example\example.py`

Output will be created in working directory. A folder will be created for each .ply file processed by EasyDCP. It contains several .ply files for classification and segmentation steps. Also, a .png file is output per each 'plant' output by segmentation step. The .png file contains phenotypic traits:

- Ellipse long and short axis
- Plant height, absolute or percentile (average of points above 90th percentile)
- Projected leaf area
- etc.

Finally, a .csv file is created in /data_out/ containing per-plant traits and metadata. This file can be read as is, or imported into R for analysis. **Include sample R file?**

## ~~Data visualization [not necessary?]~~

~~Materials:~~ 

~~R~~

~~RStudio~~

~~View .ply point clouds in CloudCompare~~

~~Rename output csv to Rinput.csv~~
~~Run foo.R in RStudio to generate graphs~~
~~Export graphs using RStudio~~