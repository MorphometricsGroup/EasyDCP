# TODO
* [ ] add numbered subfolders (to new chunk? may require revising other code doc.chunk)
* [ ] test with and without optimizeCameras
* [ ] create part-2 pipeline where user may move steps they want to do after a break/ manual check
* [ ] play with YPR
* [ ] add titles to steps in script
* [ ] scalebar markers as corners of boundbox
# Pipeline for 3d reconstruction and orthomosaic to phenotypic data

[A] automated step  
{x} not implemented  
[B] depend on user-defined boolean  
(O) optional manual step
(x) not implementsed
[M] Manual Operation

## 1. Initial setup and work
1. [M] Place scale bars
1. [M] Capture images
1. [M] separate images into folders - This could possibly be automated but I did it manually.
1. [M] **Manual make training dataset**
1. create .csv containing scalebar information
1. [M] Follow installation steps in readme
1. [M] Run pipeline-all.bat to start pipeline-all.py withing agisoft (contains auto_ctrl and pcd_processing portions)

## 2. Agisoft Reconstruction (auto_ctrl)
1. [A] create project
2. [A] import images
3. [A][B] clear GPS data
4. [A] estimate image quality
5. [A] disable images below user-defined threshold
6. [A] detect coded targets
7. [A] match photos
8. [A] align cameras (create tie points / sparse cloud)
9. [A][B] import scale bars from .csv
10. [A][B] align model with ground plane using markers or scalebars on ground
11. [A] detect non-coded markers (cross)
12. [A] detect non-coded markers (circle)
13. [A] optimize cameras
14. (O) check alignment / sparse cloud
15. {x} cleanup sparse cloud (gradual selections)  
    1. Reconstruction uncertainty
    2. Reprojection Error
    3. Projection Accuracy  
16. [A] build depth maps
17. [A] build dense cloud
18. (O) check dense cloud
19. [A] export dense cloud to .PLY
20. {x} points classification
21. [A][B] build DEM
22. [O] check DEM
23. [A][B] export DEM to .TIF
24. [A][B] build orthomosaic
25. [O] check orthomosaic
26. [A][B] export orthomosaic to .TIF   

## 3. Phenotyping analysis (phenotypy)
1. [A] File I/O
    1. read Plot ply file   
       `>>> pnt.read_ply('one_plot.ply')`  
       if need to merge multiply ply files as one plot (in the case of planteye left and right ply files)  
       `>>> pnt.read_plys(['plot_left.ply', 'plot_right.ply'])`
    1. read shp file (optional)
       `>>> pnt.read_shp('boundary.shp')`  
       `>>> pnt.read_shps(['boundary1.shp', 'boundary2.shp'])`  
1. [A] Classification of dense cloud (split fore- and back-ground)
    1. [M] Make training data
       * Image training data
          1. At least Need `fore.png` and `back.png`
          2. Ensure is PNG with alpha layer
          3. Using Photoshop or GIMP to crop the images
       * Point cloud data
          1. Need `fore.ply` and `back.ply`
          2. Using CloudCompare to crop the ply file
    1. [A] Build classifier
       1. Load training data and tell the kinds of them
       2. `cla=pnt.Classifier(path_list, kind_list)`
       3. [todo] choose 'SVM' or other classifier, or support one-class classification to avoid the heterogeneity of background, only foreground is required.
    2. [A] Apply classifier
    3. [A] Noise filtering by radius outlier removal (depends on training dataset quality)
1. [A] Segmentation
    1. Auto-segmentation(DBSCAN algorithm)
        1. [A] General DBSCAN algorithm cluster
           [todo] DBSCAN parameter need manual given, automatic it.
        2. [A] KMeans to split the large object (plant) with small object (noise) by [number of points, volumn of objects],  remove small noise groups
        3. [A] Sort by X or Y to number the order of each plants
    2. Shp-segmentation
        1. Crop the fore-ground plot cloud by the given shp boundary
1. [A] Phenotyping traits calculation
    1. Length & Width
        1. Drop Z values, keep X and Y values of all plants points
        1. Build the 2D convex hull of plants points
        1. Find the minimum area bounding rectangle
        1. Length = Rectangle.Length
        1. Width = Rectangle.Width
    1. Region Props
        1. Build the 2D binary DOM of plants
        1. Apply skimage.region_pros() algorithm to find the fitting ellipse
        2. get the center, long axis, and short axis of ellipse
    1. Projected leaf area
        1. Build the 2D binary DOM of plants
        1. Calculate the scale of pixels, count the pixel numbers
    1. Height
        1. Get ground height
           * Manual given ground height Z value 
           * Auto calculate ground height
               1. Use the 2D convex hull as the boundary, to cut ground points
               2. Use the median of ground points as the ground height
        1. Get container height, default is 0+ground_height
        1. Filter plant points over container_height
        1. Build the histogram of filtered plant points Z values
        1. Height = mean(10 percentile) - Z_min()
1. [A] Output CSV containing phenotypic data
1. (O) Output figure of traits to check the performance of this method

# Problems, manual steps.
- manually separating images into folders
- clicking GCPs if too small or large to be detected automatically
- entering scalebar IF NON CODED
- markers may be occluded by plants and not put into tie point cloud, preventing ground alignment
- export point cloud properly - scaling issue, phenotyping design concern