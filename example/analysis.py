import __init__
import pandas as pd
import easypcp as pcp
import os

planteye = False

# batch processing

group = ''
g_ht = 13.93164
num_plants = 3 #use 0 to force kmeans_split

os.mkdir(os.getcwd()+'\\data_out')

if not planteye: 
    #cla = pcp.Classifier(path_list=['example/training_data/01/fore_rm_y.png', 'example/training_data/01/back.png'], kind_list=[0, -1], core='dtc', unit='m') #PNG
    cla = pcp.Classifier(path_list=['example/training_data/02/fore_rm_r.png', 'example/training_data/02/back.png'], kind_list=[0, -1], core='dtc', unit='m') #PNG
    plot_path = 'C:/users/alex/documents/github/3dphenotyping/example/ply/'
    #plot_path = 'T:/ply/1227/v051-boundbox8/'
    #plot_path = 'D:/easypcp/1227/'
    file_list = [(plot_path + k) for k in os.listdir(plot_path) if ('.ply' in k) and (group in k)]
    plot_set = file_list
    print(plot_set)
    filename = 'easypcp-test'
else:
    cla = pcp.Classifier(path_list=['training_data/02/fore_sp3.ply', 'training_data/02/back2.ply'], kind_list=[0, -1], core='dtc', unit='mm') #PLY
    plot_set = ['T:/transformuse/transformed - merged/11_20191227T053249_M','T:/transformuse/transformed - merged/11_20191227T055715_M','T:/transformuse/transformed - merged/11_20191227T061216_M','T:/transformuse/transformed - merged/11_20191227T062221_M','T:/transformuse/transformed - merged/11_20191227T063340_M','T:/transformuse/transformed - merged/11_20191227T064758_M','T:/transformuse/transformed - merged/11_20191227T065433_M','T:/transformuse/transformed - merged/11_20191227T070513_M']
    #plot_set = ['T:/transformuse/transformed - merged/11_20191227T061216_M']
    filename = 'planteye-1227-'

# empty list for batch processing
result_container = []
plot_count = 0
plot_start, plot_end = 0,100

for plot in plot_set:
    plot_count = plot_count + 1
    if plot_count < plot_start or plot_count > plot_end: continue
    # show_steps=True to display output among calculation to check correct or not
    if not planteye: plot_class = pcp.Plot(plot, cla, write_ply=True, unit='m', down_sample=False)
    else: plot_class = pcp.Plot(plot, cla, write_ply=True, unit='mm', down_sample=True)
    # ---------- auto_segment() --------------
    if not planteye: plot_class.pcd_classified = plot_class.remove_noise()
    #-- different eps value for tricky cases
    if plot_count == 4: eps, min_points = plot_class.auto_dbscan_args(eps_grids=13, divide=100) #this is case-specific override for 4th set
    else: eps, min_points = plot_class.auto_dbscan_args(eps_grids=10, divide=100)
    seg = plot_class.dbscan_segment(eps=eps, min_points=min_points)
    #--
    if len(seg[0]) != num_plants:
        split = plot_class.kmeans_split() 
        print (len(seg[0]),'clusters')        
    if not planteye: reset_id = plot_class.sort_order(name_by='x', ascending=True)
    else: reset_id = plot_class.sort_order(name_by='y', ascending=True)
    plot_class.save_segment_result(img_folder='data_out')
    
    # ----------------------------------------
    if not planteye: traits = plot_class.get_traits(container_ht=0.12)#, ground_ht =g_ht)
    else: traits = plot_class.get_traits(container_ht=0.12, ground_ht =0)
    result_container.append(traits)

    

plot_all = pd.concat(result_container, axis=0).reset_index()
if not planteye: plot_all.to_csv('data_out/'+filename+group+str(plot_start)+'_to_'+str(plot_end)+'_agi.csv', index=False)  
else: plot_all.to_csv('data_out/'+filename+group+'_planteye.csv', index=False)  

