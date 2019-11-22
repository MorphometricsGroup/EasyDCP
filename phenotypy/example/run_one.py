import __init__
import phenotypy as pnt
cla = pnt.Classifier(path_list=['training_data/fore_rm_y.png',
                            'training_data/back.png'],
                 kind_list=[0, -1], core='dtc')

plot1 = pnt.Plot('S34.ply', cla)   # size in meter
seg = plot1.auto_segmentation()
traits = plot1.get_traits(seg, container_ht=0.06)
traits.to_csv('S34/plot1.csv')