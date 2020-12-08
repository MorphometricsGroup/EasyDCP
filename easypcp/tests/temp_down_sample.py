import __init__
import easypcp as pcp

cla = pcp.Classifier(path_list=['data/down_sample_train_fore.ply', 'data/down_sample_train_back.ply'],
                     kind_list=[0, -1], core='dtc', unit='mm')
plot = pcp.Plot('data/down_sample',
                cla, output_path='output', write_ply=True, unit='mm')
# start auto_segmentation()
plot.pcd_classified = plot.remove_noise()
eps, min_points = plot.auto_dbscan_args(eps_grids=10)
seg = plot.dbscan_segment(eps=eps, min_points=min_points)
split = plot.rm_noise_by_kmeans()
reset_id = plot.sort_order(name_by='x', ascending=True)
plot.save_segment_result()
# end auto_segmentation()
df = plot.get_traits()