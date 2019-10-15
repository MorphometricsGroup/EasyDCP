# TODO

* [ ] test with and without optimizeCameras
* [ ] create part-2 pipeline where user may move steps they want to do after a manual check
  play with YPR
* [ ] add titles to steps in script

# Pipeline for 3d reconstruction and orthomosaic to phenotypic data

[A] means automated step  
{x} not implemented  
[B] depend on user-defined boolean  

[M] Manual Operation

## 1. Capture images
separate images into folders - This could possibly be automated but I did it manually.

**create .csv containing scalebar information**

* [M] Place scale bars
* [M] Capture images
* [M] separate images into folders - This could possibly be automated but I did it manually.
* [M] Follow installation steps in readme
* [M] Run pipeline-all.bat to start pipeline-all.py withing agisoft (contains auto_ctrl and pcd_processing portions)

## 2. Agisoft Reconstruction (auto_ctrl)
1. [A] create project
2. [A] import images
3. [A] clear GPS data (if True)
4. [A] estimate image quality
5. [A] disable images below user-defined threshold
6. [A] detect coded targets
7. [A] match photos
8. [A] align cameras (create tie points / sparse cloud)
9. [A] import scale bars from .csv
10. [A] align model with ground plane using markers or scalebars on ground
11. [A] detect non-coded markers (cross)
12. [A] detect non-coded markers (circle?)
13. [A] optimize cameras
14. (O) check alignment / sparse cloud
15. {x} cleanup sparse cloud (gradual selections)  
    1. Reconstruction uncertainty
    1. Reprojection Error
    1. Projection Accuracy  
1. [A] build depth maps
2. [A] build dense cloud
3. (O) check dense cloud
4. [A] export dense cloud to .PLY
5. {x} points classification
6. [A] build DEM
7. [O] check DEM
8. [A] export DEM to .TIF
9. [A] build orthomosaic
10. [O] check orthomosaic
11. [A] export orthomosaic to .TIF   

## 3. Phenotyping analysis (pcd_processing)
1. [A] read point cloud
1. (O) **Manual make training dataset**
  1. Ensure is PNG with alpha layer
  1. Currently, using **2** class classification, so need `fore.png` and `back.png`
  1. [todo] Edit paths in config file.
 	3. [A] Classification of dense cloud from raw image
      	1. [A] Build classifier
      	2. [A] Apply classifier
      	3. [A] Noise filtering by radius outlier removal (depends on training dataset quality)
 	4. [A] Segmentation
       	1. [A] General DBSCAN algorithm cluster
      	2. (O) Check if main plants wrongly segmented
      	3. [A] Remove outlier very small noise groups haven't been removed in *Step 3.3*
      	4. [A] Using x-y axis histogram to find the main body of plants, and remove ground noise
 	5. [A] Phenotyping traits calculation
      	1. Length & Width
           	1. $Length = max{pcd.x} - min{pcd.x}$
           	2. $Width = max{pcd.y} - min{pcd.y}$
      	2. Height
           	1. $P(x_p, y_p, z_p) = max{pcd.z}$
           	2. [A] Ground points cloud denoise by statistical outlier removal
           	3. Creation of digital elevation model (DEM)
           	4. $z_{ground} = DEM(x_p, y_p)$
           	5. $Height = z_p - z_{ground}$
      	3. Volume
           	1. Generate DSM from plants clouds (given voxel\pixel size by resolution)
           	2. CHM = {DSM - DEM}
           	3. CHM = CHM >= 0
           	4. $Vol = SUM(CHM) \cdot pixel size ^2 \cdot resolution ^ 3$
 	6. [A] Output CSV containing phenotypic data
 	7. (O) Output model views of individual plants - to check segmentation accuracy

# problems, manual steps.
- clicking GCPs if too small or large to be detected automatically
- entering scalebar IF NON CODED
- markers may be occluded by plants and not put into tie point cloud, preventing ground alignment
- export point cloud properly - scaling issue, phenotyping design concern