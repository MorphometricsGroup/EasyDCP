# TODO

* [ ] test with and without optimizeCameras
* [ ] create part-2 pipeline where user may move steps they want to do after a manual check
* [ ] play with YPR
* [ ] add titles to steps in script

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
1. [A] import images
1. [A][B] clear GPS data
1. [A] estimate image quality
1. [A] disable images below user-defined threshold
1. [A] detect coded targets
1. [A] match photos
1. [A] align cameras (create tie points / sparse cloud)
1. [A][B] import scale bars from .csv
1. [A][B] align model with ground plane using markers or scalebars on ground
1. [A] detect non-coded markers (cross)
1. [A] detect non-coded markers (circle)
1. [A] optimize cameras
1. (O) check alignment / sparse cloud
1. {x} cleanup sparse cloud (gradual selections)  
    1. Reconstruction uncertainty
    1. Reprojection Error
    1. Projection Accuracy  
1. [A] build depth maps
1. [A] build dense cloud
1. (O) check dense cloud
1. [A][B] export dense cloud to .PLY
1. {x} points classification
1. [A][B] build DEM
1. [O] check DEM
1. [A][B] export DEM to .TIF
1. [A][B] build orthomosaic
1. [O] check orthomosaic
1. [A][B] export orthomosaic to .TIF   

## 3. Phenotyping analysis (pcd_processing)
1. [A] read point cloud
    1. Ensure is PNG with alpha layer
    1. Currently, using **2** class classification, so need `fore.png` and `back.png`
    1. [todo] Edit paths in config file.
1. [A] Classification of dense cloud from raw image
    1. [A] Build classifier
    1. [A] Apply classifier
    1. [A] Noise filtering by radius outlier removal (depends on training dataset quality)
1. [A] Segmentation
    1. [A] General DBSCAN algorithm cluster
    1. (O) Check if main plants wrongly segmented
    1. [A] Remove outlier very small noise groups haven't been removed in *Step 3.3*
    1. [A] Using x-y axis histogram to find the main body of plants, and remove ground noise
1. [A] Phenotyping traits calculation
    1. Length & Width (Long axis and short axis)
        1. Drop Z values, keep X and Y values of all plants points
        1. Build the 2D convex hull of plants points
        1. Find the minimum area bounding rectangle
        1. Long axis (Length) = Rectangle.Length
        1. Short axis (Width) = Rectangle.Width
    1. Cover Area
        1. = 2D Convex Hull.Area
    1. Height
        1. Using the 2D convex hull as the boundary, to cut ground points
        1. Merge cut ground points with plants points
        1. Height = Z_max(Merged Points) - Z_min(Merged Points)
    1. Convex Volume
        1. Build the 3D convex hull of merged points
        1. Calculate the volume of this 3D convex hull
    1. Concave Hull Volume
    1. Voxel Volume
        1. Build Voxel grid (split the shortest axis to 50 parts) to only plants voxles (**Not merged points**)
        1. Get the side length of voxel
        1. Calculate the each voxel volume (= side length ^ 3)
        1. Count the number of total voxels
        1. Volume = Voxel number \* voxel volume
1. [A] Output CSV containing phenotypic data
1. (O) Output model views of individual plants - to check segmentation accuracy

# problems, manual steps.
- manually separating images into folders
- clicking GCPs if too small or large to be detected automatically
- entering scalebar IF NON CODED
- markers may be occluded by plants and not put into tie point cloud, preventing ground alignment
- export point cloud properly - scaling issue, phenotyping design concern