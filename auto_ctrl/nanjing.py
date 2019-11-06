import Metashape
doc = Metashape.app.document
chunk = doc.chunk
chunk.detectMarkers(type=Metashape.CircularTarget12bit,tolerance=50)

#align cameras
chunk.matchPhotos(accuracy=Metashape.LowestAccuracy, generic_preselection=True,reference_preselection=True)
chunk.alignCameras(adaptive_fitting=True)

#densecloud
chunk.buildDepthMaps(quality=Metashape.LowestQuality, filter=Metashape.ModerateFiltering)
chunk.buildDenseCloud()

doc.save()

chunk.buildDem()
chunk.buildOrthomosaic(fill_holes=False)

doc.save()

Metashape.app.messageBox("Finished ^_^")