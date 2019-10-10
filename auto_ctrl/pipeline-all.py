# script for pipeline from multiple folders of photos
# modified from: some script from Agisoft forums, probably... i forgot 
# by Alex Feldman - UTokyo Field Phenomics Lab

# updated 2019.6.7
# compatibility Metashape Pro 1.5.2
# incompatible with nested folders
#! files in folders root will break the script

import os, Metashape

#for scalebars
from PySide2 import QtCore, QtGui

print('\n-----------------------\n~~~~start~~~~\n')

##USER DEFINED VARIABLES
path_folders = 'F:/ALEX_SSD/20190618_fukano_weed/' #enter full path to folders root (no nested folders!)
#print('path_folders',path_folders)
blur_threshold = 0.4
trust_gps = False
use_scalebars = True

#populate folder list
folder_list = os.listdir(path_folders) 
folder_count = len(folder_list)

print('# of folders:',folder_count)
print('\nfolder_list:')
for i in range(folder_count):
    print(i,folder_list[i])

photo_list = list()
filename_list = list()

#fill path list
print('\nfilling path list...')
for i in range(folder_count):
    if folder_list[i] != 'skip':
        path_photos = path_folders+folder_list[i]
        filename_list.append("/".join([path_photos,folder_list[i]])) 
        print(i)
    else:
        folder_count = folder_count - 1
    
#print(filename_list)
    
doc = Metashape.Document()

for j in range(folder_count): #run the following code for each folder    

    chunk = doc.addChunk()

    #ensure photo list is empty
    photo_list.clear()
    
    #import photos
    if folder_list[j] != 'skip':
        path_photos = path_folders+folder_list[j]
    image_list = os.listdir(path_photos)
    print(str(j)+':','path_photos',path_photos)
    print('file list:',image_list)
    for photo in image_list: #create photo list
        if photo.rsplit(".",1)[1].lower() in  ["jpg", "jpeg"]:#, "tif", "tiff"]:
            photo_list.append("/".join([path_photos, photo]))
    chunk.addPhotos(photo_list)
    print(j)    
    print('path:',filename_list[j])
    
    #clear GPS data
    if trust_gps == False:
        chunk.crs = None
        chunk.transform.matrix = None
        for camera_gps in chunk.cameras:
            camera_gps.reference.enabled = False
    
    #estimate image quality and disable below threshold
    chunk.estimateImageQuality() 
    print('--- Disabling Cameras below',blur_threshold)
    for image in chunk.cameras:
    #print (image.meta['Image/Quality'])
        if float(image.meta['Image/Quality']) < blur_threshold:
            image.enabled = False
            print ('DISABLE %s' %(image))

    #detect circular coded targets
    chunk.detectMarkers(type=Metashape.CircularTarget12bit,tolerance=100)    
    
    '''######'''
    #import scalebars from .csv
    if use_scalebars:
        path = path_folders+'skip/scalebars.csv'
        print ('path: ',path)
        file = open(path, "rt")

        eof = False
        line = file.readline()

        while not eof:
         #split the line and load into variables
         point1, point2, dist, acc = line.split(",")

         #iterate through chunk markers and see if there is a match for point 1
         if (len(chunk.markers) > 0):
             for marker in chunk.markers:
                 if (marker.label == point1):
                     scale1 = marker
                     #iterate through chunk markers and see if there is a match for point 2
                     for marker in chunk.markers:
                         if (marker.label == point2):
                             scale2 = marker

                             #create a new scale bar between points if they exist and set distance
                             scalebar = chunk.addScalebar(scale1,scale2)
                             scalebar.reference.distance = float(dist)
                             nopair = 0
                         else:
                             nopair = 1
                 else:
                     nopair = 0
                 
             if nopair:
                 print("Missing one or other end of point")

         else:
             print("no markers")

         print (len(line), line)
         #reading the next line in input file
         line = file.readline()
         print (">",len(line), line)
         if len(line) == 0:
             eof = True
             print (eof)
         else:
             print ("x",eof)
         #break

        file.close()
        Metashape.app.update()
        print("Script finished")
    '''#######'''
    
    #match, align
    chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, reference_preselection=False)
    chunk.alignCameras()
    
    #detect cross non-coded targets
    chunk.detectMarkers(type=Metashape.CrossTarget,tolerance=50)
    chunk.optimizeCameras()
    
    #depth map, dense cloud
    chunk.buildDepthMaps(quality=Metashape.MediumQuality, filter=Metashape.MildFiltering)
    chunk.buildDenseCloud() 

    #save project (required before building DEM)
    project_filename = ' - 00000 - ALLSTEPS-v15'
    savepath = filename_list[j]+project_filename
    doc.save(path = savepath+'.psx')
    chunk = doc.chunk
    
    #build DEM and export to TIF at standard resolution 0.001 m/px
    chunk.buildDem()
    chunk.exportDem(path=savepath+'-DEM.tif',dx=0.001, dy=0.001)
    
    #build Orthomosaic and export to TIF at standard resolution 0.001 m/px
    chunk.buildOrthomosaic(fill_holes=False) 
    chunk.exportOrthomosaic(path=savepath+'-orthomosaic.tif',dx=0.001, dy=0.001)   
    
    #export dense cloud
    chunk.exportPoints(path = savepath+' - MetashapeDenseCloud.ply') 
    
    doc.save()
    
    #cleanup before next folder
    doc.clear()    
   
print('Finished!')