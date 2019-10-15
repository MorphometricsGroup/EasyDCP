TODO
====
test with and without optimizeCameras
create part-2 pipeline where user may move steps they want to do after a manual check
play with YPR
add titles to steps in script

Pipeline for 3d reconstruction and orthomosaic to phenotypic data
=====
[A] means automated step
(O) optional manual step
{x} not implemented

Capture images
separate images into folders - This could possibly be automated but I did it manually.
create .csv containing scalebar information
----agisoft----
[A] create project
[A] import images
[A] clear GPS data (if True)
[A] estimate image quality
[A] disable images below user-defined threshold
[A] detect coded targets
[A] match photos
[A] align cameras (create tie points / sparse cloud)
[A] import scale bars from .csv
[A] align model with ground plane using markers or scalebars on ground
[A] detect non-coded markers (cross)
[A] detect non-coded markers (circle?)
[A] optimize cameras
(O) check alignment / sparse cloud
{x} cleanup sparse cloud (gradual selections)
	A. Reconstruction uncertainty
	B. Reprojection Error
	C. Projection Accuracy
[A] build depth maps
[A] build dense cloud
(O) check dense cloud
[A] export dense cloud to .PLY
{x} points classification
[A] build DEM
[O] check DEM
[A] export DEM to .TIF
[A] build orthomosaic
[O] check orthomosaic
[A] export orthomosaic to .TIF 
----analysis---
import orthomosaic / dem / dense cloud
Haozhou [many steps]
	A. Classification of dense cloud from raw image
	B. Noise filtering
	C. Leftover noise filtering by point cloud size histogram
	D. Creation of DEM/DSM
	E. Segmentation of plants and Identification by x-axis order
	F. Measurement
		a. Ellipse long and short axis
		b. Volume 
		c. etc
output CSV containing phenotypic data

--
problems, manual steps. 
-clicking GCPs if too small or large to be detected automatically
-entering scalebar IF NON CODED
-markers may be occluded by plants and not put into tie point cloud, preventing ground alignment
export point cloud properly - scaling issue, phenotyping design concern