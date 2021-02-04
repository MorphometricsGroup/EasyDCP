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

- Parameters of note:

  - `percentile` located in `base.py, def get_percentile_height():`
    - default `98`. This value may be adjusted depending on the quality of the point cloud.
      - `98` should give a near-maximum plant height in most cases. For a measurement closer to the maximum plant height (heighest plant point), increase to `99`, `99.5`, etc. Note: A lower-quality point cloud (e.g., produced from an image set with low overlap or resolution, or low settings used by EasyDCP_Creation) may contain some noise points above the true plant top and could cause overestimation bias. Values such as `99.9` are only recommended when point cloud quality is high.
  - Default `eps_points = 10`. Higher value may be used if segmentation fails, such as one plant being wrongly divided in two segments. Recommend trying 13. Higher `eps_points` value may dramatically increase CPU processing time. 

**Execute your.py file using python , using EasyDCP root folder as working directory:**

`(easydcp37) C:\Users\Alex\Documents\GitHub\3Dphenotyping>python example\example.py`

**TODO: change `example` to `scripts`?**

Output will be created in working directory. A folder will be created for each .ply file processed by EasyDCP. It contains several .ply files for classification and segmentation steps. Also, a .png file is output per each 'plant' output by segmentation step. The .png file contains individual phenotypic traits at a glance:

- Plant height, percentile-based (average of points above `percentile` parameter, default 98)
- Projected leaf area
- Ellipse long and short axis
- Convex hull volume
- etc.

Finally, a .csv file is created in **/data_out/ TODO - variable?** containing per-plant traits and metadata. This file can be read as is, or imported into R or other software for analysis.

## ~~Data visualization [not necessary?]~~

~~Materials:~~ 

~~R  **Include sample R file?**~~

~~RStudio~~

~~View .ply point clouds in CloudCompare~~

~~Rename output csv to Rinput.csv~~
~~Run foo.R in RStudio to generate graphs~~
~~Export graphs using RStudio~~