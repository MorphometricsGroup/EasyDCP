**See heading.md for installation instructions.**

Overview of EasyPCP workflow:

# <img src="flow.png" style="zoom:33%;" />

# Point cloud creation

## (a) Image acquisition/capturing (manual init.)

Materials : 

Floor area minimum 1 m x 2 m

Container plants. Avoid using green-colored container.

floor covering (black or other non-plant color) (optional)

RGB camera

Printed attached .pdf file `easypcp\materials\targets.pdf`, first 2 pages. [easypcp requires 4 targets per page. i used 6mm radius .] Attach to clipboard or other rigid backing.

1. The height of plant container is needed by EasyPCP, so be sure to measure and record the height of the container.
2. If using floor covering, place on desired area to be used for image acquisition. If not using floor covering, ensure floor area is free of any materials that may be similar to plant color (e.g. weeds)
3. Define measurement area by placing the two printed target sheets at opposite corners. [see figure]
4. Arrange a group of container plants within the measurement area, by placing them in a single row, or 2 rows using triangular spacing [see image]. Ensure adequate gap between all plants. *Note: The number of plants per group is only limited by the size of the measurement area and the size of the plants.*
5. Photograph in one or more rows parallel to plant row. Recommend 5cm spacing . e.g., 20 images per each meter of plant row.
6. Repeat steps 3 and 4 for all remaining plants.
7. Organize photos into folders by group. One folder per one group of plants. (See example/images)

## (b) Point cloud creation

Materials: 

Photos from image acquisition step, organized into folders by group as described above.

Agisoft Metashape Professional 1.6.5

CloudCompare (optional)

1. Edit params.ini user-defined variables:
   - Open `easypcp\creation\params.ini` in text editor 
   - set all parameters as desired, defaults are set, and each parameter is explained in the comments, e.g.:
     - set `align_quality` and `dense_quality`, default medium
     - change`path_folders`to the path containing the folders of images
     - change `blur_threshold` to desired value. Pipeline will disable all images with Agisoft image quality below the `blur_threshold`.
     - set booleans e.g., `ignore_gps`, `align_ground`, and `use_scalebars ` as needed
2. Ensure folder structure matches intended format
   - only folders in root folder (path_folders), no files in root
     - e.g. (`path_folders\images_1\img_001.jpg...`)
   - 'skip' folder contains scalebars.csv if needed 
     - located in `path_folders\skip`s
     - **Default scalebars.csv provided in 3dphenotyping\materials to match targets.pdf. Copy to [path_folders]\skip directory.**
3. Open `easypcp\creation\creation.bat` in text editor, and confirm the path to your `easypcp\creation` folder.
4. Run `creation.bat` ~~**[dev] update program to use agisoft package. update installation for .whl.**~~
   - Find output .psx and .ply files in each corresponding folder. **[dev] change output to single folder?** Verify successful 3D reconstruction with Agisoft and CloudCompare, respectively.

# (c) Point cloud analysis

Materials: 

Point cloud files (.ply) from point cloud creation step

GIMP, Photoshop or equivalent software

Known height of container (mm) 

## Setup for PCD analysis (manual init.)

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

## PCD analysis

Materials:

- Folder containing .ply point cloud files output by previous step, (b) EasyPCP point cloud creation
- training data created in previous step "Setup for PCD analysis"

Control EasyPCP via API using python script in your python 3.7 environment as described in Installation documentation (heading.md). Several .py files are provided in /example/ as examples of simple scripts to control EasyPCP. See documentation (api.md) for details on controlling EasyPCP via python.

Configure EasyPCP before launching:

- Ensure your .py script points to correct training data and point cloud folder. *Ensure `container_ht` is correctly set.* 

- Default `eps_points = 10`. Higher value may be used if segmentation fails, such as one plant being wrongly divided in two segments. Recommend trying 13. Higher `eps_points` value may dramatically increase CPU processing time. 

**Execute your.py file using python , using 3Dphenotyping root folder as working directory:**

`(easypcp37) C:\Users\Alex\Documents\GitHub\3Dphenotyping>python example\example.py`

Output will be created in working directory. A folder will be created for each .ply file processed by EasyPCP. It contains several .ply files for classification and segmentation steps. Also, a .png file is output per each 'plant' output by segmentation step. The .png file contains phenotypic traits:

- Ellipse long and short axis
- Plant height, absolute or percentile (average of points above 90th percentile)
- Projected leaf area
- etc.

Finally, a .csv file is created in /data_out/ containing per-plant traits and metadata. This file can be read as is, or imported into R for analysis. **Include sample R file?**

## Data visualization [not necessary?]

~~Materials:~~ 

~~R~~

~~RStudio~~

~~View .ply point clouds in CloudCompare~~

~~Rename output csv to Rinput.csv~~
~~Run foo.R in RStudio to generate graphs~~
~~Export graphs using RStudio~~