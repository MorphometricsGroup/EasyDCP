import __init__
import pandas as pd
import easypcp as pcp

cla = pcp.Classifier(path_list=['training_data/02/fore_rm_r.png',
                            'training_data/02/back.png'],
                 kind_list=[0, -1], core='dtc', unit='m')

# batch processing
plot_set = ['SP1G2.ply','SP4G1.ply'] #ply files must be in working directory
# empty list for batch processing
result_container = []

for plot in plot_set:
    plot_class = pcp.Plot(plot, cla, write_ply=True, unit='m', down_sample=True) # show_steps=True to display output among calculation to check correct or not
    # ---------- auto_segment() --------------
    plot_class.pcd_classified = plot_class.remove_noise()
    eps, min_points = plot_class.auto_dbscan_args(eps_grids=13, divide=100)
    seg = plot_class.dbscan_segment(eps=eps, min_points=min_points)
    if len(seg[0]) > 3:
        split = plot_class.rm_noise_by_kmeans()
    reset_id = plot_class.sort_order(name_by='x', ascending=True)
    plot_class.save_segment_result(img_folder='plot_out')
    # ----------------------------------------
    traits = plot_class.get_traits()
    result_container.append(traits)

plot_all = pd.concat(result_container, axis=0).reset_index()
plot_all.to_csv('traits.csv', index=False)