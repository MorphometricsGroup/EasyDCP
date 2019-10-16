# script for pipeline from multiple folders of photos
# modified from: scripts on Agisoft forums by Alexey Pasumansky
# by Alex Feldman - UTokyo Field Phenomics Lab

# updated 2019.10.16
# compatibility Metashape Pro 1.5.3
#! incompatible with nested folders
#! files in folders root will break the script
#! Non-agisoft nested folder in photos folder will break script
#! Agisoft errors will break the script. 
#>>TODO: Jump to next folder on error
#>>TODO: write info to log file (failed folders, etc)

import os, Metashape, math #for auto_ctrl

###Begin Agisoft auto_ctrl 3D reconstruction portion

print('\n-----------------------\n~~~~start auto_ctrl~~~~\n')

##USER DEFINED VARIABLES
path_folders = 'F:/ALEX_SSD/20190618_fukano_weed/' #enter full path to folders root (no nested folders!)
project_filename = ' - 00000 - ALLSTEPS-v28-med'
blur_threshold = 0.4
ignore_gps = True
use_scalebars = True
align_ground = True
export_cloud = True
build_dem = True
build_ortho = True

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
print('\n[3Dphenotyping] filling path list...')
for i in range(folder_count):
    if folder_list[i] != 'skip':
        path_photos = path_folders+folder_list[i]
        filename_list.append("/".join([path_photos,folder_list[i]])) 
        print(i)
    else:
        folder_count = folder_count - 1
    
doc = Metashape.app.document

for j in range(folder_count): #run the following code for each folder    

    chunk = doc.addChunk()
    
    #ensure photo list is empty
    photo_list.clear()
    
    #import photos
    if folder_list[j] != 'skip':
        path_photos = path_folders+folder_list[j]
    image_list = os.listdir(path_photos)
    print(str(j)+':','path_photos',path_photos)
    #print('file list:',image_list)
    for photo in image_list: #create photo list
        if photo.rsplit(".",1)[1].lower() in  ["jpg", "jpeg"]:#, "tif", "tiff"]: #! change 1 to -1 and test with folder in photos folder
            photo_list.append("/".join([path_photos, photo]))
    chunk.addPhotos(photo_list)
    print(j)    
    print('path:',filename_list[j])
    
    #clear GPS data
    if ignore_gps:
        chunk.crs = None
        #chunk.transform.matrix = None
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
   
    #match, align
    chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, reference_preselection=False)#default: HighAccuracy
    chunk.alignCameras()

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

        file.close()
        Metashape.app.update()
        print("Scalebars script finished")

    #save project (required before building DEM)
    savepath = filename_list[j]+project_filename
    doc.save(path = savepath+'.psx')
    chunk = doc.chunk #this line is only necessary after the first save when defining path
    
    '''#optional break to check result
    break #only break if you want the script to stop here for each folder
    '''
    
    #align ground plane with markers
    if align_ground:
        
        def vect(a, b):
            """
            Normalized vector product for two vectors
            """

            result = Metashape.Vector([a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y *b.x])
            return result.normalized()

        def get_marker(label, chunk):
            """
            Returns marker instance from chunk based on the label correspondence
            """
            
            for marker in chunk.markers:
                if label == marker.label:
                    return marker
            print("Marker not found! " + label)
            return False

        region = chunk.region
        '''vertical = ["target 9", "target 3"] 
        horizontal = ["target 9", "target 1"]'''
        
        horizontal = ["target 9", "target 16"]
        vertical = ["target 9", "target 3"] #fails on S08, S12
        #vertical = ["target 2", "target 15"] #run for all?
        
        print('H0: ',get_marker(horizontal[0], chunk).position)
        print('H1: ',get_marker(horizontal[1], chunk).position)
        print('V0: ',get_marker(vertical[0], chunk).position)
        print('V1: ',get_marker(vertical[1], chunk).position)
               
        horizontal = get_marker(horizontal[0], chunk).position - get_marker(horizontal[1], chunk).position
        vertical = get_marker(vertical[0], chunk).position - get_marker(vertical[1], chunk).position

        '''normal = vect(horizontal, vertical)
        vertical = - vertical.normalized()
        horizontal = vect(vertical, normal)'''
        normal = vect(horizontal, vertical)
        horizontal = - horizontal.normalized()
        vertical = - vect(horizontal, normal)

        R = Metashape.Matrix ([horizontal, vertical, normal]) #horizontal = X, vertical = Y, normal = Z

        print(R.det())
        region.rot = R.t()
        chunk.region = region
        R = chunk.region.rot        #Bounding box rotation matrix
        C = chunk.region.center        #Bounding box center vector

        if chunk.transform.matrix:
            T = chunk.transform.matrix
            s = math.sqrt(T[0,0] ** 2 + T[0,1] ** 2 + T[0,2] ** 2)         #scaling # T.scale()
            S = Metashape.Matrix().Diag([s, s, s, 1]) #scale matrix
        else:
            S = Metashape.Matrix().Diag([1, 1, 1, 1])
        T = Metashape.Matrix( [[R[0,0], R[0,1], R[0,2], C[0]], [R[1,0], R[1,1], R[1,2], C[1]], [R[2,0], R[2,1], R[2,2], C[2]], [0, 0, 0, 1]])
        chunk.transform.matrix = S * T.inv()        #resulting chunk transformation matrix        

        chunk.resetRegion()

        print(filename_list[j]," Ground alignment finished")
    
    #detect non-coded targets and optimize cameras
    chunk.detectMarkers(type=Metashape.CrossTarget,tolerance=50)
    chunk.detectMarkers(type=Metashape.CircularTarget,tolerance=50)
    chunk.optimizeCameras()
    
    #save project
    doc.save()
    '''#optional break to check result
    break #only break if you want the script to stop here for each folder
    '''
    
    #build depth map, dense cloud
    chunk.buildDepthMaps(quality=Metashape.MediumQuality, filter=Metashape.MildFiltering)#default: MediumQuality
    chunk.buildDenseCloud() 
    
    #export dense cloud
    if export_cloud:
        chunk.exportPoints(path = savepath+'-MetashapeDenseCloud.ply')   
    
    #save project 
    doc.save()
    '''#optional break to check result
    break #only break if you want the script to stop here for each folder
    '''
    
    #build DEM and export to TIF at standard resolution 0.001 m/px
    if build_dem:
        chunk.buildDem()
        chunk.exportDem(path=savepath+'-DEM.tif',dx=0.001, dy=0.001)
    
    #save project
    doc.save()
    '''#optional break to check result
    break #only break if you want the script to stop here for each folder
    '''
    
    #build Orthomosaic and export to TIF at standard resolution 0.001 m/px
    if build_ortho:
        chunk.buildOrthomosaic(fill_holes=False) 
        chunk.exportOrthomosaic(path=savepath+'-orthomosaic.tif',dx=0.001, dy=0.001)   
    
    #save project
    doc.save()
    '''#optional break to check result
    break #only break if you want the script to stop here for each folder
    '''
    
    print ('\n3Dphenotyping auto_ctrl portion complete for ',savepath

    
    #variables to pass to pcd_processing portion
    cloud = savepath+'-MetashapeDenseCloud.ply'
    dem = savepath+'-DEM.tif'
    ortho = path=savepath+'-orthomosaic.tif'
    #print variables
    print('path to cloud: ',cloud)
    print('path to DEM: ',dem)
    print('path to orthomosaic: ',ortho)
    
    #begin pcd_processing portion
    print('\n-----------------------\n~~~~start pcd_processing~~~~\n')
    
    #cleanup before next folder
    doc.clear()    
   
print('Finished!')