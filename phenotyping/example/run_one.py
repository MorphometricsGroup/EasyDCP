import __init__
from base import *

cla = Classifier(path_list=['training_data/fore_rm_y.png',
                            'training_data/back.png'],
                 kind_list=[0, -1], core='dtc')

plot1 = Plot('S34.ply', cla, show_steps=False)   # size in meter
# save ply if necessary
plot1.write_ply()
plot1.write_fig()
print(plot1.traits)
plot1.traits.to_csv('plot1.csv')