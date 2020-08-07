'''Standard or Professional?
 Tools - Preferences - GPU
 
 import images
 detect coded targets
 match photos
 align cameras (create tie points / sparse cloud)
    check alignment / sparse cloud
 build depth maps
 build dense cloud
    check dense cloud
 export dense cloud to .PLY
 build DEM
 export DEM to .TIF
 build orthomosaic
 export orthomosaic to .TIF   '''
 
import os, Metashape

savepath = 'f:/agi-out/demo-191022'

doc = Metashape.app.document
chunk = doc.chunk

chunk.detectMarkers(type=Metashape.CircularTarget12bit,tolerance=100)

chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, reference_preselection=False)#default: HighAccuracy
chunk.alignCameras()

doc.save(path = savepath+'-densecloud.psx')
chunk = doc.chunk

chunk.buildDepthMaps(quality=Metashape.MediumQuality, filter=Metashape.MildFiltering)#default: MediumQuality
chunk.buildDenseCloud() 

chunk.exportPoints(path = savepath+'.ply') 

chunk.buildDem()
#chunk.exportDem(path=savepath+'-DEM.tif',dx=0.001, dy=0.001)

chunk.buildOrthomosaic(fill_holes=False) 
#chunk.exportOrthomosaic(path=savepath+'-orthomosaic.tif',dx=0.001, dy=0.001)  

doc.save()

Metashape.app.messageBox("Finished!")