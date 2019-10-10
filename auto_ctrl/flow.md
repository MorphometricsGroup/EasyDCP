TODO
====
test with and without optimizeCameras
create part-2 pipeline where user may move steps they want to do after a manual check
play with YPR


Pipeline for 3d reconstruction and orthomosaic to phenotypic data
=====
[A] means automated step
(O) optional manual step
{x} not implemented

Capture images
separate images into folders - This could possibly be automated but I did it manually.

----agisoft----
[A] create project
[A] import images
[A] clear GPS data
[A] estimate image quality
[A] disable images below user-defined threshold
[A] detect coded targets
[A] match photos
[A] align cameras (create tie points / sparse cloud)
[A] detect non-coded markers (cross)
[A] detect non-coded markers (circle?)
[A] optimize cameras
[A] align model with ground plane using markers on ground
[A] import scale bars
(O) check alignment / sparse cloud
{x} cleanup sparse cloud (gradual selections)
	A. Reconstruction uncertainty
	B. Reprojection Error
	C. Projection Accuracy
[A] build depth maps
[A] build dense cloud
(O) check dense cloud
{x} points classification
[A] build DEM (using Top XY?)
[A] build orthomosaic
(O) check DEM and orthomosaic
[A] export dense cloud to PLY, XYZ, etc
[A] export DEM to TIF
[A] export orthomosaic to TIF
----analysis---
import orthomosaic
run stuff [many steps]
output CSV containing phenotypic data
(in progress)

--
problems, manual steps. 
-clicking GCPs if too small or large
-entering scalebar IF NON CODED
export point cloud properly