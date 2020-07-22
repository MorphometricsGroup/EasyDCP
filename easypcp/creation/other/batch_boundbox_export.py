# script for pipeline from multiple folders of photos
# modified from: some script from Agisoft forums, probably... i forgot 
# by Alex Feldman - UTokyo Field Phenomics Lab

# updated 2019.6.11
# compatibility Metashape Pro 1.5.2
# incompatible with nested folders
#! files in folders root will break the script

import os, Metashape
import math

def update_boundbox():

    '''doc = Metashape.app.document
    chunk = doc.chunk'''     # This points to the first chunk!

    #ground targets for finding horizontal center
    p0 = "target 1"  
    p1 = "target 8"  #mine
    #px = "target 4"
    #py = "target 1"

    #not used?
    distancepx = 0.7
    distancepy = 0.4

    '''
    box_X_length = 1.5
    box_Z_length = 0.75
    box_Y_length = 1 # in meters?
    '''

    #side targets (above ground plane, for finding vertical center)
    '''
    c1target = "target 21"
    c2target = "target 22"
    c3target = "target 6"
    c4target = "target 7"
    '''

    ##########################################
    ##                                      ##
    ##   End of variables                   ##
    ##                                      ##
    ##########################################


    mp0 = 0
    mpy = 0
    mpx = 0

    fp0 = 0
    fpy = 0
    fpx = 0

    #mine
    fp1 = 0

    #setting for Y up, Z forward -> needed for mixamo/unity
    '''
    vector0 = Metashape.Vector((0,0,0))
    vectorY = Metashape.Vector((0,0,distancepy))   # Specify Y Distance
    vectorX = Metashape.Vector((distancepx,0,0))   # Specify X Distance

    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    '''
    c = 0

    #find center points from side markers (his way)
    '''
    for m in chunk.markers:
      if m.label == c1target:
        print ("Center 1 point found")
        c1 = c
      if m.label == c2target:
        print ("Center 2 point found")
        c2 = c
      if m.label == c3target:
        print ("Center 3 point found")
        c3 = c
      if m.label == c4target:
        print ("Center 4 point found")
        c4 = c
      if m.label == p0: 
        mp0 = c
        fp0 = 1
        m.reference.location = vector0
        m.reference.enabled = 1
        print ("Found center point")
      if m.label == py: 
        mpy = c
        fpy = 1
        m.reference.location = vectorY
        m.reference.enabled = 1
        print ("found Y point")
        
      if m.label == px: 
        mpx = c
        fpx = 1
        m.reference.location = vectorX
        m.reference.enabled = 1
        print ("found X point")
      c = c + 1
    '''

    #find center points (my way)
    c1=0
    c2=0

    print (p0,p1)
    for m in chunk.markers:
        if m.label == p0:
            c1=c
            fp0=1
        elif m.label == p1:
            c2=c
            fp1=1
        c=c+1

    #check markers found (his way)
    '''
    if fp0 and fpx and fpy:
      print ("Found all markers")
      chunk.updateTransform()
    else:
      print ("Error: not all markers found")
    '''

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
    v_t = T * Metashape.Vector( [0,0,0,1] )
    m = Metashape.Matrix().Diag([1,1,1,1])	

    m = m * T
    s = math.sqrt(m[0,0] ** 2 + m[0,1] ** 2 + m[0,2] ** 2) #scale factor
    R = Metashape.Matrix( [[m[0,0],m[0,1],m[0,2]], [m[1,0],m[1,1],m[1,2]], [m[2,0],m[2,1],m[2,2]]])
    R = R * (1. / s)
    newregion.rot = R.t()

    # Calculate center point of the bounding box, by taking the average of 2 left and 2 right markers 
    #mx = (chunk.markers[c1].position + chunk.markers[c2].position + chunk.markers[c3].position + chunk.markers[c4].position) / 4 #his way
    mx = (chunk.markers[c1].position + chunk.markers[c2].position) / 2 #my way 

    print('x',chunk.markers[c2].position[0],chunk.markers[c1].position[0])
    print('y',chunk.markers[c2].position[1],chunk.markers[c1].position[1])
    box_X_length = -(chunk.markers[c2].position[0] - chunk.markers[c1].position[0]) #x-axis. returns negative number, so inverted
    box_Y_length = -(chunk.markers[c2].position[1] - chunk.markers[c1].position[1]) #y-axis. returns negative number, so inverted
    box_Z_length = box_Y_length#chunk.markers[c2].position[2] - chunk.markers[c1].position[2] #z-axis. same as Y length

    print('lengths:',box_X_length,box_Y_length,box_Z_length)

    Z_ratio = 2 #my way. Change this to adjust box height (default=1)

    mx = Metashape.Vector([mx[0], mx[1], mx[2] + (0*Z_ratio*box_Z_length/2)]) #adjusting the zratio thing shifts the whole boundbox on a diagonal. not so easy. set to 0 for now.
    newregion.center = mx
    '''
    dist = chunk.markers[mp0].position - chunk.markers[mpy].position
    dist = dist.norm()
    '''
    #ratio = dist / distancepy #his way


    #newregion.size = Metashape.Vector([box_X_length* ratio, box_Y_length* ratio, box_Z_length * ratio]) #his way

    newregion.size = Metashape.Vector([box_X_length, box_Y_length, box_Z_length * Z_ratio]) #my way

    chunk.region = newregion
    chunk.updateTransform()

    print ("Bounding box should be aligned now")

print('\n-----------------------\n~~~~start~~~~\n')

path_folders = 'T:/2020agisoft/191227pheno/' #enter full path to folders root (no nested folders!)
print('path_folders',path_folders)

#populate folder list
folder_list = os.listdir(path_folders) 
folder_count = len(folder_list)

print('# of folders:',folder_count)
print('\nfolder_list:')
for i in range(folder_count):
    print(i,folder_list[i])

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
    
print('\nfilename_list: ',filename_list)
    
doc = Metashape.Document()


#find .psx file in list, and open it
for j in range(folder_count): #run the following code for each folder    
    if folder_list[j] != 'skip':
        path_photos = path_folders+folder_list[j]
    print('\npath_photos: ',path_photos)
    file_list = os.listdir(path_photos)
    print('\nfile_list: ',file_list)
    print(str(j)+':','path_photos',path_photos)
    for file in file_list: #search file list for .psx
        if (file.rsplit(".",1)[-1].lower() in  ["psx", "psz"]) and ('optimized' in file) and ('canon-sp1' not in file) and ('canon-sp2' not in file): #do stuff if project file
            #open project
            print('\nopen project: '+path_photos+'/'+file)    
            doc.open(path_photos+'/'+file)
            chunk = doc.chunk
            #do stuff here
            update_boundbox()
            chunk.exportPoints(path = filename_list[j]+'-MetashapeDenseCloud-boundbox.ply')
            #save project (as new name - will eat tons of space, change after dev)
            project_filename = '-boundbox'
            doc.save(path = filename_list[j]+project_filename+'.psx') #save metashape project
            continue #break out of for loop after first .psx file found
        
    
#Metashape.app.messageBox('Finished (Discard?)')
'''Metashape.app.quit()'''