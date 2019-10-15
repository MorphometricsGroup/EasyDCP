TODO
====
test with and without optimizeCameras
create part-2 pipeline where user may move steps they want to do after a manual check
play with YPR
add titles to steps in script

Pipeline for 3d reconstruction and orthomosaic to phenotypic data
=====
[A] automated step
[M] manual step
(o) optional manual step
{x} not implemented
[B] depend on user-defined boolean

[M] Place scale bars
[M] Capture images
[M] separate images into folders - This could possibly be automated but I did it manually.
[M] Follow installation steps in readme
[M] Run pipeline-all.bat to start pipeline-all.py withing agisoft (contains auto_ctrl and pcd_processing portions)
====
pipeline-all.py steps:
====
----agisoft(auto_ctrl)----
[A] create project
[A] import images
[A][B] clear coordinate system and dereference GPS data
[A] estimate image quality
[A] disable images below user-defined threshold
[A] detect coded targets
[A] match photos
[A] align cameras (create tie points / sparse cloud)
[A][B] import scale bars from .csv 
[A] save project
(o) break to check tie point cloud, scalebars and coded targets
[A][B] align model with ground plane using markers or scalebars on ground
[A] detect non-coded markers (cross)
[A] detect non-coded markers (circle)
[A] optimize cameras
[A] save project
(o) break to check tie point cloud alignment and marker detection
{x} cleanup sparse cloud (gradual selections)
	A. Reconstruction uncertainty
	B. Reprojection Error
	C. Projection Accuracy
[A] build depth maps
[A] build dense cloud
[A] save project
(o) break to check dense cloud
[A] export dense cloud to .PLY
{x} points classification
[A] build DEM
[A] save project
(o) break to check
[A] export DEM to .TIF
[A] build orthomosaic
[A] save project
(o) break to check
[A] export orthomosaic to .TIF 
----analysis(pcd_processing)---
import (orthomosaic/dem/) point cloud
Haozhou [many steps]
	A. Classification of dense cloud points from raw image
	B. Noise filtering
	C. Leftover noise filtering by point cloud size histogram
	D. Creation of DEM/DSM
	E. Segmentation of plants and Identification by x-axis order
	F. Measurement
		a. Ellipse long and short axis
		b. Volume 
		c. etc
output CSV containing phenotypic data
output model views (.JPG) of individual plants - to check segmentation	 accuracy

--
problems, manual steps. 
-clicking GCPs if too small or large to be detected automatically
-entering scalebar IF NON CODED
-markers may be occluded by plants and not put into tie point cloud, preventing ground alignment
export point cloud properly - scaling issue, phenotyping design concern