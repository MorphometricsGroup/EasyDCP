# script for pipeline from multiple folders of photos
# modified from: some script from Agisoft forums, probably... i forgot 
# by Alex Feldman - UTokyo Field Phenomics Lab

# updated 2019.6.11
# compatibility Metashape Pro 1.5.2
# incompatible with nested folders
#! files in folders root will break the script

import os, Metashape
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
        if (file.rsplit(".",1)[-1].lower() in  ["psx", "psz"]) and ("47" in file) and ('high' in file): #do stuff if project file
            #open project
            print('\nopen project: '+path_photos+'/'+file)    
            doc.open(path_photos+'/'+file)
            chunk = doc.chunk
            #do stuff here
            chunk.optimizeCameras()
            chunk.buildDepthMaps(downscale=2, filter_mode=Metashape.MildFiltering)#defaults: 4,MildFiltering
            chunk.buildDenseCloud() 
            chunk.exportPoints(path = filename_list[j]+'-MetashapeDenseCloud-optimized.ply')
            #save project (as new name - will eat tons of space, change after dev)
            project_filename = '-optimized'
            doc.save(path = filename_list[j]+project_filename+'.psx') #save metashape project
            continue #break out of for loop after first .psx file found
        
    
#Metashape.app.messageBox('Finished (Discard?)')
'''Metashape.app.quit()'''