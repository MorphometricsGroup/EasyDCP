import __init__
import pandas as pd
import easydcp as dcp
import os

def mkdir_if_needed(dir_path):
    if not os.path.isdir(dir_path):
        print('The directory is not present. Creating a new one..')
        os.mkdir(dir_path)
    else:
        print('The directory is present.')

#Create classifier
cla = dcp.Classifier(path_list=['example/training_data/02/fore_rm_r.png',
                            'example/training_data/02/back.png'],
                 kind_list=[0, -1], core='dtc', unit='m')

#Define input .ply files
plot_path =  'G:/My Drive/EasyDCP_Data/Performance test/1_EasyDCP_Creation/' # set to folder containing .ply files!
file_list = [(plot_path + k) for k in os.listdir(plot_path) if ('.ply' in k)]
plot_set = file_list

result_container = [] # empty list for batch processing
num_plants = 0 #change if using fixed number of plants
output_folder = 'data_out'

#create output folder if it does not exist
mkdir_if_needed(os.getcwd()+'\\'+output_folder) 

for plot in plot_set:

    plot_class = dcp.Plot(plot, cla, write_ply=True, unit='m', down_sample=False) # show_steps=True to display output among calculation to check correct or not
    # ---------- auto_segment() --------------
    plot_class.pcd_classified = plot_class.remove_noise()
    eps, min_points = plot_class.auto_dbscan_args(eps_grids=10, divide=100)
    seg = plot_class.dbscan_segment(eps=eps, min_points=min_points)
    if len(seg[0]) > num_plants:
        split = plot_class.kmeans_split()
    reset_id = plot_class.sort_order(name_by='x', ascending=True)
    plot_class.save_segment_result(img_folder=output_folder)
    # ----------------------------------------
    traits = plot_class.get_traits(container_ht=0.12) #set container height in meters
    result_container.append(traits)

plot_all = pd.concat(result_container, axis=0).reset_index()
plot_all.to_csv(output_folder+'/'+'traits.csv', index=False)