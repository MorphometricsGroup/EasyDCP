# script for pipeline from multiple folders of photos
# modified from: some script from Agisoft forums, probably... i forgot 
# by Alex Feldman - UTokyo Field Phenomics Lab

# updated 2019.6.7
# compatibility Metashape Pro 1.5.2
# incompatible with nested folders
#! files in folders root will break the script

import os, Metashape
print('\n-----------------------\n~~~~start~~~~\n')

path_folders = 'F:/ALEX_SSD/20190618_fukano_weed/' #enter full path to folders root (no nested folders!)
print('path_folders',path_folders)
blur_threshold = 0.4

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
    print('image list:',image_list)
    for photo in image_list: #create photo list
        if photo.rsplit(".",1)[1].lower() in  ["jpg", "jpeg"]:#, "tif", "tiff"]:
            photo_list.append("/".join([path_photos, photo]))
        '''print('photo list:',photo_list)'''
    chunk.addPhotos(photo_list)
    print(j)    
    print('path:',filename_list[j])
    
    ##~~save placeholder~~    
    
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
    chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, reference_preselection=False)
    chunk.alignCameras()
    
    #detect cross non-coded targets
    chunk.detectMarkers(type=Metashape.CrossTarget,tolerance=50)
    '''
    ##~~save placeholder~~
    
    #build depth maps
    chunk.buildDepthMaps(quality=Metashape.MediumQuality, filter=Metashape.MildFiltering)
    
    ##~~save placeholder~~
    
    chunk.buildDenseCloud() #build dense cloud
    
    chunk.exportPoints(path = filename_list[j]+' - MetashapeDenseCloud.ply') #export dense cloud
    '''
    project_filename = ' - 00001 - checkIQ+disable+detectMks'#+ str(blur_threshold)
    doc.save(path = filename_list[j]+project_filename+'-v2.psx')
    
    #cleanup before next folder
    doc.clear()    

    
Metashape.app.messageBox('Finished')
#Metashape.app.quit()