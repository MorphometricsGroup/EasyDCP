#Wont work as is!

import os, Metashape

doc = Metashape.app.document

chunk = doc.chunk

chunk.optimizeCameras()

chunk.exportPoints(path = savepath+'-MetashapeDenseCloud.ply')