import __init__
import phenotypy as pnt

cla = pnt.Classifier(path_list=['data/weed_fore.png', 'data/weed_back.png'], kind_list=[0, -1], core='dtc')
plot = pnt.Plot('data/weed.ply', cla, output_path='output')
# start auto_segmentation()
plot.pcd_classified = plot.remove_noise()
eps, min_points = plot.auto_dbscan_args(times=10)
seg = plot.dbscan_segment(eps=eps, min_points=min_points)
split = plot.kmeans_split()
reset_id = plot.sort_order(name_by='x', ascending=True)
plot.save_segment_result()
# end auto_segmentation()
df = plot.get_traits()