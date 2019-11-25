import __init__
import pytest
import phenotypy as pnt
import pandas as pd
'''
@pytest.fixture(scope="session", autouse=True)
def plot_init():
    cla = pnt.Classifier(path_list=['data/weed_fore.png',
                                    'data/weed_back.png'],
                         kind_list=[0, -1], core='dtc')

    plot = pnt.Plot('data/weed.ply', cla, output_path='output')
    return plot

def test_plot_0_without_seg(plot_init):
    with pytest.raises(AttributeError) as excinfo:
        plot_init.get_traits(container_ht=0.06)
    print('\n', excinfo.value)
    assert "This plot have not been segmented" in str(excinfo.value)

def test_plot_1_auto_segmentation(plot_init):
    seg = plot_init.auto_segmentation()
    print('\n', type(seg), len(seg))
    for k in seg.keys():
        print(k, len(seg[k]))

def test_plot_2_output(plot_init):
    df = plot_init.get_traits(container_ht=0.057)
    print('\n', df)
    print('\n', list(df.columns))
'''

@pytest.fixture(scope="session", autouse=True)
def plot_init_potato():
    cla = pnt.Classifier(path_list=['data/potato_fore.png',
                                    'data/potato_back.png'],
                         kind_list=[0, -1], core='dtc')
    plot = pnt.Plot('data/potato.ply', cla, output_path='output')
    return plot

def test_plot_3_shp_segmentation(plot_init_potato):
    seg = plot_init_potato.shp_segmentation(shp_dir=['data/potato_field1plot.shp', 'data/potato_field2plot.shp'],
                                            correct_coord=(367912.000, 3955467.000, 98.000), rename=False)
    print('\n', type(seg), len(seg))
    for k in seg.keys():
        print(k, len(seg[k]))

def test_plot_4_shp_traits(plot_init_potato):
    df = plot_init_potato.get_traits()
    print('\n', df)
    print('\n', list(df.columns))


if __name__ == '__main__':
    pytest.main()
