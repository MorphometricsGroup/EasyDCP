**See heading.md for installation instructions.**

Image below: Draft version. Update later.

# <img src="flow.png" style="zoom:33%;" />

# Point cloud creation

## Image acquisition/capturing (manual init.)

Materials : 

Container plants

floor covering (black or other non-plant color)

RGB camera

Printed attached .pdf file `easypcp\materials\targets.pdf`, first 2 pages. [easypcp requires 4 targets per page. i used 6mm radius .] Attach to clipboard or other rigid backing.

0. The height of plant container is needed by EasyPCP, so be sure to measure and record the height of the container.

1. If using floor covering, place in desired area to be used for image acquisition. If not using floor covering, ensure area is free of any materials that may be similar to plant color (e.g. weeds)
2. Define measurement area by placing the two printed target sheets at opposite corners. [see figure]
3. Arrange a group of container plants within the measurement area, by placing them in a single row, or 2 rows using triangular spacing [see image]. Ensure adequate gap between all plants. *Note: The number of plants per group is only limited by the size of the measurement area and the size of the plants.*
4. Photograph in one or more rows parallel to plant row. Recommend 5cm spacing . e.g., 20 images per each meter of plant row.
5. Repeat steps 3 and 4 for all remaining plants.
6. Organize photos into folders by group. One folder per one group of plants.

*To be continued?*

## Point cloud creation

Materials: 

Photos from image acquisition step, organized into folders by group as described above.

Agisoft Metashape Professional 1.6.x (0 or higher?)

CloudCompare

1. Edit pipeline-all.py user-defined variables:

Navigate to `easypcp/creation`

open pipeline-all.py

-set `agisoft_quality` to 5 (lowest) for initial run. change later

-change`path_folders`to the path containing the folders of images
-change `blur_threshold` to desired value. Pipeline will disable all images with Agisoft image quality below the `blur_threshold`.
-set `ignore_gps`, `align_ground`, and `use_scalebars ` as needed

Ensure folder structure matches intended format
- only folders in root folder (path_folders), no files in root
- 'skip' folder contains scalebars.csv if needed **Default scalebars.csv provided to match targets.pdf**

2. Run pipeline-all.bat **update program to use agisoft package?? update installation?**

3. Find output .psx and .ply files in each corresponding folder. **change output to single folder?** Verify successful 3D reconstruction with Agisoft and CloudCompare, respectively.

# Point cloud analysis

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

See docs/api.md 

Arrange point clouds into folder

Ensure batch.py points to correct training data and point cloud folder. Also ensure `container_ht` is correctly set. If unknown, set to 0.

Run batch.py

*To be continued?*

## Data visualization [maybe not necessary]

~~Materials:~~ 

~~R~~

~~RStudio~~

~~View .ply point clouds in CloudCompare~~

~~Rename output csv to Rinput.csv~~
~~Run foo.R in RStudio to generate graphs~~
~~Export graphs using RStudio~~