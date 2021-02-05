# script for phenotyping pipeline from multiple folders of photos
# using scripts on Agisoft forums by Alexey Pasumansky
# by Alex Feldman - UTokyo Field Phenomics Lab

# updated 2021.02.04
# compatibility Metashape Pro 1.6.5
## Incompatible Metashape Pro 1.5.x and below
# compatible with one level of nested folders
#! files in folders root will break the script
#! Non-agisoft nested folder in photos folder will break script
#! - Actually, it means any nested folder without '.' in the name will break the script
#! Metashape errors will break the script. 
#>>!TODO: Jump to next folder on error (catch exception)
#>>!TODO: write report to log file (failed folders, successful, etc)
#>>!todo: update export DEM/orthomosaic for 1.6 API [export disabled now]

# agisoft_LICENSE = 'C:\Program Files\Agisoft\Metashape Pro'
import Metashape 
import os, math, datetime 
import configparser, json 

banner1 = '\n[EasyDCP_Creation]'
start_time = datetime.datetime.now()
print(banner1,'Started at',start_time)

##USER DEFINED VARIABLES

config = configparser.ConfigParser()
params_path = os.getcwd() + '/alex_params-0618_v0825.ini'
print ('loading parameters from:',params_path)
config.read(params_path)

path_folders = config['DEFAULT']['path_folders']
project_filename = config['DEFAULT']['project_filename']
config_section = 'DEFAULT'
select_nested = False #config[config_section].getboolean('select_nested') - hardcoded for now
# nested_folders = config[config_section]['nested_folders']
# nested_folders = json.loads(config.get(config_section,'nested_folders'))
ignore_gps_exif             = config[config_section].getboolean('ignore_gps_exif')
disable_by_iq               = config[config_section].getboolean('disable_by_iq')
iq_threshold                = config[config_section].getfloat('iq_threshold')

align_times                 = config[config_section].getint('align_times')
align_quality               = config[config_section]['align_quality']
align_preselection_mode     = config[config_section]['align_preselection_mode']
dense_quality               = config[config_section]['dense_quality']
detect_coded_targets        = config[config_section].getboolean('detect_coded_targets')
target_tolerance            = config[config_section].getint('target_tolerance')
detect_noncoded_targets     = config[config_section].getboolean('detect_noncoded_targets')
noncoded_tolerance          = config[config_section].getint('noncoded_tolerance')
crop_by_targets             = config[config_section].getboolean('crop_by_targets')

use_scalebars               = config[config_section].getboolean('use_scalebars')
align_ground_with_targets   = config[config_section].getboolean('align_ground_with_targets')

export_cloud                = config[config_section].getboolean('export_cloud')
build_dem                   = config[config_section].getboolean('build_dem')
build_ortho                 = config[config_section].getboolean('build_ortho')

#del config

# print('p',path_folders,type(path_folders))
# print('n',nested_folders,type(nested_folders)) 
# print('a',align_times,type(align_times),'b',iq_threshold,type(iq_threshold),'d',detect_coded_targets,type(detect_coded_targets))

if align_quality == 'Highest':
    match_downscale = 0
elif align_quality == 'High':
    match_downscale = 1
elif align_quality == 'Medium':
    match_downscale = 2
elif align_quality == 'Low':
    match_downscale = 4
elif align_quality == 'Lowest':
    match_downscale = 8
else:
    print('align_quality variable in params.ini set incorrectly!\nchoices: Highest, High, Medium, Low, Lowest\nyou set:',align_quality)
    print('defaulting to Medium')
    match_downscale = 2
    
if dense_quality == 'Highest':
    depth_downscale = 1
elif dense_quality == 'High':
    depth_downscale = 2
elif dense_quality == 'Medium':
    depth_downscale = 4
elif dense_quality == 'Low':
    depth_downscale = 8
elif dense_quality == 'Lowest':
    depth_downscale = 16
else:
    print('depth_quality variable in params.ini set incorrectly!\nchoices: Highest, High, Medium, Low, Lowest\nyou set:',align_quality)
    print('defaulting to Medium')
    depth_downscale = 4
    

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
    if type in  ["jpg", "jpeg", "png"]:#, "tif", "tiff"]: 
        photo_list.append("/".join([filepath, filename]))
        
def disable_below_threshold(threshold=0.4):
    print(banner1,'Analyze and Disable blurry photos...')
    chunk.analyzePhotos() 
    print('--- Disabling Cameras below',threshold)
    for image in chunk.cameras:
    #print (image.meta['Image/Quality'])
        if float(image.meta['Image/Quality']) < threshold:
            image.enabled = False
            print ('DISABLE %s' %(image))

def detect_cross_target(tol):
    chunk.detectMarkers(target_type=Metashape.CrossTarget,tolerance=tol, progress=progress_print) #todo: update to support cross and circle noncoded

def scale_by_cameras(cam_1,cam_2,cam_dist):
    print("Create scalebars from cameras")
    scalebar = chunk.addScalebar(chunk.cameras[cam_1],chunk.cameras[cam_2])
    scalebar.reference.distance = cam_dist
    chunk.updateTransform()
    Metashape.app.update()
    print("Script finished")

def ignore_gps():
    print(banner1,"Ignoring photo GPS metadata")
    chunk.crs = None
    #chunk.transform.matrix = None
    for camera_gps in chunk.cameras:
        camera_gps.reference.enabled = False
    
def import_scalebars(path):
    print(banner1,'Importing scalebars data from .csv...')
    path = path + 'skip/scalebars.csv'
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
             print(banner1,"Missing one or other end of point!")
     else:
         print(banner1,"no markers!")

     print (len(line), line)
     #reading the next line in input file
     line = file.readline()
     print ("line length: ",len(line), line)
     if len(line) == 0:
         eof = True
         print ('End of file:', eof)
     # else:
         # print ('End of file:',eof)

    file.close()
    Metashape.app.update()
    print(banner1,"Scalebars script finished")
   
def align_cameras(reps=1, preselection_mode='generic'):
    for i in range(reps):
        print(banner1,'Matching and Aligning cameras... pass #',i+1,'of',reps)
        # Change metashape_quality variable to set downscale parameter
        if preselection_mode == 'generic':
            print('generic')
            chunk.matchPhotos(downscale=match_downscale, generic_preselection=True, reference_preselection=False, progress=progress_print)
        elif preselection_mode == 'reference':
            print('reference')
            chunk.matchPhotos(downscale=match_downscale, generic_preselection=False, reference_preselection=True, reference_preselection_mode=Metashape.ReferencePreselectionSequential, progress=progress_print)
        chunk.alignCameras(progress=progress_print)   
 
def align_ground(path, section='DEFAULT'):
    print(banner1,'Aligning ground (XY) plane with coded targets...')

    region = chunk.region
    
    path = path + 'skip/orientation.ini'
    print ('path: ',path)
    
    config = configparser.ConfigParser()
    config.read(path)
    # print(config.sections())
        
    horiz0 = config[section]['horiz0']
    horiz1 = config[section]['horiz1']
    vert0 = config[section]['vert0']
    vert1 = config[section]['vert1']
    
    del config
    
    print('x-axis:',horiz0,'to',horiz1)
    print('y-axis:',vert0,'to',vert1)
    
    H0_pos = get_marker(horiz0,chunk).position
    H1_pos = get_marker(horiz1,chunk).position
    V0_pos = get_marker(vert0,chunk).position
    V1_pos = get_marker(vert1,chunk).position
    
    print('H0: ',H0_pos)
    print('H1: ',H1_pos)
    
    #!disabled for strawberry 
    print('V0: ',V0_pos)
    print('V1: ',V1_pos)
           
    
    horizontal = H1_pos - H0_pos
    #!disabled for strawberry 
    vertical = V1_pos - V0_pos
    
    '''#!special for strawberry
    normal = get_marker(horiz[0], chunk).position
    normal[2] = normal[2] + 1'''

    ''' old version (!Delete?)
    normal = vect(horizontal, vertical)
    vertical = vertical.normalized()
    horizontal = vect(vertical, normal)'''
    #!disabled for strawberry 
    normal = vect(horizontal, vertical)
    vertical = - vect(horizontal, normal)
    horizontal = horizontal.normalized()
    '''#!disabled for strawberry 
    vertical = - vect(horizontal, normal)'''
    
    '''#!special for strawberry
    normal = - vect(horizontal, vertical)'''

    R = Metashape.Matrix ([horizontal, vertical, normal]) #horizontal = X, vertical = Y, normal = Z

    print(R.det()) #should be 1.0
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

    print("\nGround alignment finished\n")
    
def update_boundbox_by_markers(path,chunk,section='DEFAULT'):

    print(banner1,"Updating boundbox using markers...")

    #ground targets for finding horizontal center
    path = path + 'skip/orientation.ini'
    print ('path: ',path)
    config = configparser.ConfigParser()
    config.read(path)
    p0 = config[section]['p0']
    p1 = config[section]['p1']
    buffer = config[section].getint('buffer')
    print(p0,p1,buffer)
    
    del config
    
    """bypass .ini
    #normal for EasyDCP_Creation
    p0 = "target 1"  
    p1 = "target 8" 
    
    #below: special case for strawberry
    '''p0 = "target 1"  
    p1 = "target 19"  '''"""

    print('p0:',p0,'p1:',p1)
    
    fp0 = fp1 = 0 #initialize binary values for finding the markers to 0

    #setting for Y up, Z forward -> needed for mixamo/unity

    c = 0

    #find center points (my way)
    c1=0
    c2=0

    # print (p0,p1)
    for m in chunk.markers:
        if m.label == p0:
            c1=c
            fp0=1
        elif m.label == p1:
            c2=c
            fp1=1
        c=c+1

    #check markers found (my way)
    if fp0 and fp1:
      print ("Found all markers")
      print (c1,c2)
      chunk.updateTransform()
    else:
      print ("Error: not all markers found")
      print(fp0,fp1)

    newregion = chunk.region

    T = chunk.transform.matrix
    #v_t = T * Metashape.Vector( [0,0,0,1] )
    m = Metashape.Matrix().Diag([1,1,1,1])	

    m = m * T
    s = math.sqrt(m[0,0] ** 2 + m[0,1] ** 2 + m[0,2] ** 2) #scale factor
    R = Metashape.Matrix( [[m[0,0],m[0,1],m[0,2]], [m[1,0],m[1,1],m[1,2]], [m[2,0],m[2,1],m[2,2]]])
    R = R * (1. / s)
    newregion.rot = R.t()

    # Calculate center point of the bounding box, by taking the average of 2 left and 2 right markers 
    mx = (chunk.markers[c1].position + chunk.markers[c2].position) / 2 #my way 

    print('x',chunk.markers[c2].position[0],chunk.markers[c1].position[0])
    print('y',chunk.markers[c2].position[1],chunk.markers[c1].position[1])
    box_X_length = math.fabs(chunk.markers[c2].position[0] - chunk.markers[c1].position[0]) * (100+buffer) / 100 #x-axis. may return negative number, so absoluted
    box_Y_length = math.fabs(chunk.markers[c2].position[1] - chunk.markers[c1].position[1]) * (100+buffer) / 100 #y-axis. may return negative number, so absoluted
    
    print('lengths:',box_X_length,box_Y_length)
    
    #!disabled for strawberry
    if box_Y_length > box_X_length:
        swap_length = box_X_length
        box_X_length = box_Y_length
        box_Y_length = swap_length
        del swap_length 
    
    Z_ratio = 1 #my way. Change this to adjust box height (default=1)
    box_Z_length = box_Y_length * Z_ratio #same as Y length #chunk.markers[c2].position[2] - chunk.markers[c1].position[2] #z-axis 

    print('lengths:',box_X_length,box_Y_length,box_Z_length)

    mx = Metashape.Vector([mx[0], mx[1], mx[2]]) #adjusting the zratio thing shifts the whole boundbox on a diagonal. not so easy. set to 0 for now.
    newregion.center = mx
    print('cent1',newregion.center)
    newregion.size = Metashape.Vector([box_X_length, box_Y_length, box_Z_length]) #my way
    print('nrsize1',newregion.size)
    print('cent[2]',newregion.center[2],'size[2]',newregion.size[2])
    newregion.center = Metashape.Vector([newregion.center[0],newregion.center[1],newregion.center[2] + ( newregion.size[2] / 2 )])
    print('cent2',newregion.center)
    chunk.region = newregion
    chunk.updateTransform() #disabled for strawberry

    print ("Bounding box should be aligned now")

def build_dense_cloud(savepath,export_cloud=True):
    print(banner1,'Building depth maps and dense cloud...')
    # Change metashape_quality variable to set downscale parameter
    chunk.buildDepthMaps(downscale=depth_downscale, filter_mode=Metashape.MildFiltering, progress=progress_print)#default: MildFiltering
    chunk.buildDenseCloud(point_conﬁdence=True, progress=progress_print) 
    #export dense cloud
    if export_cloud: chunk.exportPoints(path = savepath+'.ply')  
    
def build_dem_and_orthomosaic(dem,ortho,export_dem=True,export_ortho=True):
    if dem or ortho:
        print(banner1,'Building DEM...')
        chunk.buildDem()
        print('todo: update script for 1.6 API [export disabled]')
        #if export_dem: chunk.exportRaster(???) exportDem(path=savepath+'-DEM.tif',dx=0.001, dy=0.001)
        if ortho:
            print(banner1,'Building orthomosaic...')
            chunk.buildOrthomosaic(fill_holes=False) 
            print('todo: update script for 1.6 API [export disabled]')
            #if export_ortho: chunk.exportRaster(???) exportOrthomosaic(path=savepath+'-orthomosaic.tif',dx=0.001, dy=0.001) #!todo update for 1.6 API
        
def progress_print(p):
        print('Current task progress: {:.2f}%'.format(p))
        
### --- Begin EasyDCP_Creation ---

doc = Metashape.app.document
print(type(align_quality),type(dense_quality))
project_filename = project_filename + '_' + align_preselection_mode[:3] + '_' + align_quality + '_' + dense_quality
print('\n----',banner1,'\nStart\n')    

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
    
# for j in range(2): #MAIN BODY. run the following code for each folder (image set)    
for j in range(folder_count): #MAIN BODY. run the following code for each folder (image set)    
    
    #ensure photo list and Metashape document are empty
    photo_list.clear()
    nest_list.clear()
    doc.clear()  
    
    #set 'has nested folders' to false (none have been found yet)
    has_nested = False
    
    #populate file list
    print("\n-----------------------------------")
    print(banner1,"Looking for photos...")
    this_folder = folder_list[j]
    print("current folder:",j+1,'of',folder_count,this_folder)

    path_photos = path_folders + this_folder
    file_list = os.listdir(path_photos)
    print(len(file_list),'files')
    print(str(j)+':',path_photos)
    # print('file list:',file_list)
    
    ## nested folder operations
    #look for nested folders
    for item in file_list: 
        if "." not in item: #check if folder
            print(item,"is a nested folder!")
            has_nested = True
            nestpath = "/".join([path_photos,item])
            # print('nestpath:',nestpath)
            nest_list.append(nestpath)
        else: append_by_type(item, path_photos)

    photo_count = len(photo_list)
    print('\nphoto count:',photo_count) 
    #print('photo list:',photo_list)
    
    if has_nested:    #populate file list from nested folders

        print(banner1,"Checking nested folders...\n")
        print('nested folder list: ',nest_list)
        for item in nest_list:
            print('item:',item)
            if select_nested:
                print('checking if this nested folder is selected by user')
                folder_name = item.rsplit("/",1)[-1].lower()
                char0 = folder_name[0]
                #print('folder name:',folder_name,'char0:',char0)#
                for m in range(len(nested_folders)):
                    if nested_folders[m] == char0:
                        print('selected nested folder found!')
                        file_list = os.listdir(item)
                        print(len(file_list),'files')
                        # print ('\nFile list:',file_list)
                        for file in file_list:
                            if "." not in file:
                                print(file,"is a nested folder! Ignoring!!")
                            else: 
                                append_by_type(file, item)
            else: 
                print("using all nested folders")
                file_list = os.listdir(item)
                print(len(file_list),'files')
                #print ('\nFile list:',file_list)
                for file in file_list:
                    if "." not in file:
                        print(file,"is a nested folder! Ignoring!!")
                    else: 
                        append_by_type(file, item)
        photo_count = len(photo_list)
        print('\nphoto count:',photo_count) 
        #print('photo list:',photo_list)
    
    #!debug only
    # break 
    # continue 
    
    #import photos
    if photo_count > 0:
        print(banner1,"Adding photos...")
        chunk = doc.addChunk()
        chunk.addPhotos(photo_list)
    else:
        print('no photos found! moving to next folder...')
        continue #skip the rest of the for loop contents (for the current folder) because no photos were found.
    print(j,'save path:',filename_list[j])
    
    #save project - first save
    savepath = filename_list[j]+project_filename
    doc.save(path = savepath+'.psx')
    chunk = doc.chunk #this line is only necessary after the first save when defining path
       
    #clear GPS data
    if ignore_gps_exif: ignore_gps()
    
    #estimate image quality and disable below threshold
    if disable_by_iq: disable_below_threshold(iq_threshold)
     
    #detect circular coded targets
    if detect_coded_targets: chunk.detectMarkers(target_type=Metashape.CircularTarget12bit,tolerance=target_tolerance, progress=progress_print)

    doc.save()  

    #continue #only use if you want the script to stop here for each folder
    
    #match, align cameras (images)
    align_cameras(reps=align_times,preselection_mode=align_preselection_mode)
        
    #import scalebars from .csv
    if use_scalebars: import_scalebars(path=path_folders)
    doc.save()
    
    #align ground plane with markers
    if align_ground_with_targets: align_ground(path=path_folders, section='0618-0')

    chunk.resetRegion()
    
    doc.save()    #save project
    
    #continue #only use if you want the script to stop here for each folder 
    
    #detect non-coded targets
    if detect_noncoded_targets: detect_cross_target(noncoded_tolerance)

    #optimize cameras
    chunk.optimizeCameras()
    
    #update bounding box 
    if crop_by_targets: update_boundbox_by_markers(path=path_folders,chunk=chunk, section='0618-0')
    
    #save project
    doc.save()
    
    # break #only use if you want the script to stop after running the first folder
    #continue #only use if you want the script to stop here for each folder
    
    #build depth map, dense cloud
    build_dense_cloud(export_cloud = export_cloud, savepath = savepath)
    
    doc.save()    #save project

    # continue #only use if you want the script to stop here for each folder
    
    #scale_by_cameras(40,140,1.1) #only use this if you want to scale the model based on known camera distance !delete
    
    #build DEM and orthomosaic and export to TIF at standard resolution 0.001 m/px
    if build_dem or build_ortho: build_dem_and_orthomosaic(dem=build_dem,ortho=build_ortho)
   
    #save project
    doc.save()
    
    #generate report to .pdf
    chunk.exportReport(path = savepath+'-report.pdf')
    
    # continue #only use if you want the script to stop here for each folder    

    #variables to pass to EasyDCP_Analysis
    cloud_path = savepath+'-MetashapeDenseCloud.ply'
    #print dense point cloud file path 
    print('path to point cloud: ',cloud_path)

    #begin EasyDCP_Analysis
    print('\n-----')
    print(banner1,'complete for',this_folder)
    print('[Ready to start EasyDCP_Analysis!]') 
    
    # break #only use if you want the script to stop after running the first folder
   
finish_time = datetime.datetime.now()

print(banner1,'Started at',start_time)
print (banner1,'Finished at',finish_time)