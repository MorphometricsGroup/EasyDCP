import __init__
import phenotypy as pnt
cla = pnt.Classifier(path_list=['training_data/01/fore_rm_y.png',
                                'training_data/01/back.png'],
                     kind_list=[0, -1], core='dtc')

plot1 = pnt.Plot(r'S03.ply', cla)
# ----------- auto_segmentation() ----------
plot1.pcd_classified = plot1.remove_noise()
# split the shortest axis into 100 parts
eps, min_points = plot1.auto_dbscan_args(eps_grids=10, divide=100)
# the dbscan eps is the length of 10 grids, (10/100=10% of shortest axis in this case)
# the min_points is the mean points of each grids (voxels)
seg = plot1.dbscan_segment(eps=eps, min_points=min_points)
split = plot1.kmeans_split()  # the algorithm to remove big noise that can not be removed in previous steps (limited by min_points)
reset_id = plot1.sort_order(name_by='x', ascending=True)
plot1.save_segment_result(img_folder='plot_out')
# -------------------------------------------
traits = plot1.get_traits(container_ht=0.057)    # size in meter
traits.to_csv('S03/plot1.csv')