# script for pipeline from multiple folders of photos
# modified from: scripts on Agisoft forums by Alexey Pasumansky
# by Alex Feldman - UTokyo Field Phenomics Lab

# updated 2020.01.20
# compatibility Metashape Pro 1.5.3
'''#! incompatible with nested folders
#! files in folders root will break the script
#! Non-agisoft nested folder in photos folder will break script'''
#! Agisoft errors will break the script. 
#>>TODO: Jump to next folder on error
#>>TODO: write info to log file (failed folders, etc)

import os, Metashape, math #for auto_ctrl

###Begin Agisoft auto_ctrl 3D reconstruction portion

##USER DEFINED VARIABLES
path_folders = 'T:/2020agisoft/191227pheno/' #enter full path to folders root (no nested folders!)
project_filename = '-v048-all-nocross-high'#' - 00000 - ALLSTEPS-v28-med'
#variables regarding nested folders
select_nested = False #set to True if you want to only use selected nested folders
nested_folders = ['1','2'] #put the first character of the folder names you want to use here
#agisoft variables
blur_threshold = 0.5 #set this to the minimum acceptable image quality rating provided by Agisoft 
detect_targets = True #set to True if you used Agisoft coded targets
target_tolerance = 100
detect_markers = False #set to True if you used non-coded (cross) markers
cross_tolerance = 50
ignore_gps = True #set to True if photos have bad GPS info, such as RGB handheld camera with GPS at short range
use_scalebars = True #set to True if you used coded-target scalebars and have provided scalebars.csv file 
align_ground = True #set to True if you want to use the scalebars to align the ground plane
export_cloud = True #set to True if you want to export the point cloud to .PLY file
build_dem = False #set to True if you want to build and export DEM as .TIF file
build_ortho = False #set to True if you want to build and export orthomosaic as .TIF file

##User does not need to change these variables
banner1 = '\n[3Dphenotyping][auto_ctrl]'

##FUNCTIONS
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

def append_by_type(filename, filepath):
    #print('~~~',filename)
    type = filename.rsplit(".",1)[-1].lower()
    if type in  ["jpg", "jpeg", "png"]:#, "tif", "tiff"]: #! change 1 to -1 and test with folder in photos folder
        photo_list.append("/".join([filepath, filename]))
        
def disable_below_threshold(threshold):
    print(banner1,'Analyze and Disable blurry photos...')
    chunk.analyzePhotos() 
    print('--- Disabling Cameras below',threshold)
    for image in chunk.cameras:
    #print (image.meta['Image/Quality'])
        if float(image.meta['Image/Quality']) < threshold:
            image.enabled = False
            print ('DISABLE %s' %(image))

def detect_noncoded_marker(tol):
    chunk.detectMarkers(target_type=Metashape.CrossTarget,tolerance=tol)

print('\n----',banner1,'----\n~~~~start auto_ctrl~~~~\n')    

#populate folder list
folder_list = os.listdir(path_folders) 
folder_count = len(folder_list)
print('# of folders:',folder_count)
print('\nfolder_list:')
for i in range(folder_count):
    print(i,folder_list[i])
photo_list = list()
filename_list = list()
nest_list = list()

#fill folder list
print(banner1,'filling folder list...')
for i in range(folder_count):
    if folder_list[i] != 'skip':
        path_photos = path_folders+folder_list[i]
        filename_list.append("/".join([path_photos,folder_list[i]])) 
        print("folder_list",i,folder_list[i])
    else: folder_count = folder_count - 1
    
doc = Metashape.app.document

for j in range(folder_count): #run the following code for each folder    
    
    #ensure photo list and agisoft document are empty
    photo_list.clear()
    nest_list.clear()
    doc.clear()  
    
    #set 'has nested folders' to false (none have been found yet)
    has_nested = False
    
    #populate file list
    print("\n-----------------------------------")
    print(banner1,"Looking for photos...")
    print("folder_list",j,folder_list[j])
    if folder_list[j] != 'skip': path_photos = path_folders+folder_list[j]
    '''
    '''
    file_list = os.listdir(path_photos)
    print(len(file_list),'files')
    print(str(j)+':','path_photos',path_photos)
    print('file list:',file_list)
    #look for nested folders
    for item in file_list: 
        if "." not in item: #check if folder
            print(item,"is a nested folder!")
            has_nested = True
            nestpath = "/".join([path_photos,item])
            print('nestpath:',nestpath)
            nest_list.append(nestpath)
        else: append_by_type(item, path_photos)
        '''
        '''

    photo_count = len(photo_list)
    print('\nphoto count:',photo_count) 
    #print('photo list:',photo_list)
    
    #populate file list from nested folders
    if has_nested:
        print(banner1,"Checking nested folders...\n")
        print('nest list: ',nest_list)
        for item in nest_list:
            print('item:',item)
            folder_name = item.rsplit("/",1)[-1].lower()
            char0 = folder_name[0]
            #print('folder name:',folder_name,'char0:',char0)#
            if select_nested:
                for m in range(len(nested_folders)):
                    if nested_folders[m] == char0:
                        print('selected nested folder found!')
                        '''
                        '''
                        file_list = os.listdir(item)
                        print(len(file_list),'files')
                        #print ('\nFL:',file_list)
                        for file in file_list:
                            if "." not in file:
                                print(file,"is a nested folder! Ignoring!!")
                            else: 
                                append_by_type(file, item)
                                '''
                                '''
            else: 
                '''
                '''
                file_list = os.listdir(item)
                print(len(file_list),'files')
                #print ('\nFL:',file_list)
                for file in file_list:
                    if "." not in file:
                        print(file,"is a nested folder! Ignoring!!")
                    else: 
                        append_by_type(file, item)
                        '''
                        '''
        photo_count = len(photo_list)
        print('\nphoto count:',photo_count) 
        #print('photo list:',photo_list)
    
    #import photos
    if photo_count > 0:
        print(banner1,"Adding photos...")
        chunk = doc.addChunk()
        chunk.addPhotos(photo_list)
    else:
        print('no photos found! moving to next folder...')
        continue #skip the rest of the loop because no photos were found.
    print(j,'save path:',filename_list[j])
    
    #save project - first save
    savepath = filename_list[j]+project_filename
    doc.save(path = savepath+'.psx')
    chunk = doc.chunk #this line is only necessary after the first save when defining path
    
    #DEBUG
    #continue
    
    #clear GPS data
    if ignore_gps:
        print(banner1,"Ignoring photo GPS metadata")
        chunk.crs = None
        #chunk.transform.matrix = None
        for camera_gps in chunk.cameras:
            camera_gps.reference.enabled = False
    
    #estimate image quality and disable below threshold
    disable_below_threshold(blur_threshold)
     
    #detect circular coded targets
    if detect_targets: chunk.detectMarkers(target_type=Metashape.CircularTarget12bit,tolerance=target_tolerance)


    #match, align
    print(banner1,'Matching and Aligning cameras...')
    chunk.matchPhotos(downscale=1, generic_preselection=True, reference_preselection=False)#defaults: 1,True,False
    chunk.alignCameras()

    #DEBUG
    '''doc.save()  
    continue'''
    

    #import scalebars from .csv
    if use_scalebars:
        print(banner1,'Importing scalebars data from .csv...')
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

    #save project
    doc.save()
    
    '''#optional continue to check result
    continue #only use if you want the script to stop here for each folder
    '''
    
    #align ground plane with markers
    if align_ground:
        print(banner1,'Aligning ground (XY) plane with coded targets...')
        '''
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
'''
        region = chunk.region
        '''vertical = ["target 9", "target 3"] 
        horizontal = ["target 9", "target 1"]'''
        
        horizontal = ["target 1", "target 3"]#["target 9", "target 16"]
        vertical = ["target 1", "target 4"]#["target 9", "target 3"] #fails on S08, S12
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
    if detect_markers: detect_noncoded_marker(cross_tolerance)

    chunk.optimizeCameras()
    
    #save project
    doc.save()
    '''#optional continue to check result
    continue #only use if you want the script to stop here for each folder
    '''
    
    #build depth map, dense cloud
    print(banner1,'Building depth maps and dense cloud...')
    chunk.buildDepthMaps(downscale=2, filter_mode=Metashape.MildFiltering)#defaults: 4,MildFiltering
    doc.save()
    chunk.buildDenseCloud() 
    #export dense cloud
    if export_cloud: chunk.exportPoints(path = savepath+'-MetashapeDenseCloud.ply')   
    
    #save project 
    
    '''#optional continue to check result
    continue #only use if you want the script to stop here for each folder
    '''
    
    #build DEM and export to TIF at standard resolution 0.001 m/px
    if build_dem:
        doc.save()
        print(banner1,'Building DEM...')
        chunk.buildDem()
        print('todo: update script for 1.6 API')
        #chunk.exportRaster(???) exportDem(path=savepath+'-DEM.tif',dx=0.001, dy=0.001)
    
    #save project
    
    '''#optional continue to check result
    continue #only use if you want the script to stop here for each folder
    '''
    
    #build Orthomosaic and export to TIF at standard resolution 0.001 m/px
    if build_ortho:
        print(banner1,'Building orthomosaic...')
        doc.save()
        chunk.buildOrthomosaic(fill_holes=False) 
        print('todo: update script for 1.6 API')
        #chunk.exportRaster(???) exportOrthomosaic(path=savepath+'-orthomosaic.tif',dx=0.001, dy=0.001)   
    
    #save project
    doc.save()
    '''#optional continue to check result
    continue #only use if you want the script to stop here for each folder
    '''

    '''
    '''
    #variables to pass to pcd_processing portion
    cloud = savepath+'-MetashapeDenseCloud.ply'
    dem = savepath+'-DEM.tif'
    ortho = savepath+'-orthomosaic.tif'
    #print variables
    print('path to cloud: ',cloud)
    if build_dem: print('path to DEM: ',dem)
    if build_ortho: print('path to orthomosaic: ',ortho)
    print (banner1,'auto_ctrl portion complete for ',savepath)
    '''
    '''
    #begin pcd_processing portion
    print('\n-----------------------\n~~~~start pcd_processing~~~~\n') 
   
print('Finished!')