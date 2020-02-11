import __init__
import pytest
import phenotypy as pnt
import pandas as pd

@pytest.fixture(scope="session", autouse=True)
def plot_init_brocoli():
    cla = pnt.Classifier(path_list=['data/brocoli_train_plant1.ply',
                                    'data/brocoli_train_soil.ply',
                                    'data/brocoli_train_soil_gcp.ply'],
                         kind_list=[0, -1, -1], core='dtc')
    plot = pnt.Plot('data/brocoli.ply', cla, output_path='output')
    return plot

# def test_classsifier_apply(plot_init_brocoli):

@pytest.fixture(scope="session", autouse=True)
def plot_init():
    cla = pnt.Classifier(path_list=['data/weed_fore.png',
                                    'data/weed_back.png'],
                         kind_list=[0, -1], core='dtc')

    plot = pnt.Plot('data/weed.ply', cla, output_path='output')
    return plot

def test_plot_0_without_seg_traits(plot_init):
    with pytest.raises(LookupError) as excinfo:
        plot_init.get_traits(container_ht=0.06)
    print('\n', excinfo.value)
    assert "The plot has not been segmented yet" in str(excinfo.value)

def test_plot_0_without_seg_kmeans(plot_init):
    with pytest.raises(LookupError) as excinfo:
        plot_init.kmeans_split()
    print('\n', excinfo.value)
    assert "The plot has not been segmented yet, please do" in str(excinfo.value)

def test_plot_0_without_seg_save(plot_init):
    with pytest.raises(LookupError) as excinfo:
        plot_init.kmeans_split()
    print('\n', excinfo.value)
    assert "The plot has not been segmented yet, please do" in str(excinfo.value)

def test_plot_1_auto_segment_flow(plot_init):
    plot_init.pcd_classified = plot_init.remove_noise()
    eps, min_points = plot_init.auto_dbscan_args(eps_grids=10)
    seg = plot_init.dbscan_segment(eps=eps, min_points=min_points)
    split = plot_init.kmeans_split()
    reset_id = plot_init.sort_order(name_by='x', ascending=True)
    plot_init.save_segment_result()

def test_plot_2_output(plot_init):
    df = plot_init.get_traits(container_ht=0.057)
    print('\n', df)
    print('\n', list(df.columns))

# shp segmentation test
@pytest.fixture(scope="session", autouse=True)
def plot_init_potato():
    cla = pnt.Classifier(path_list=['data/potato_fore.png',
                                    'data/potato_back.png'],
                         kind_list=[0, -1], core='dtc')
    plot = pnt.Plot('data/potato.ply', cla, output_path='output')
    return plot

def test_plot_3_shp_segment(plot_init_potato):
    seg = plot_init_potato.shp_segment(shp_dir=['data/potato_field1plot.shp', 'data/potato_field2plot.shp'],
                                       correct_coord=(367912.000, 3955467.000, 98.000), rename=False)
    print('\n', type(seg), len(seg))
    for k in seg.keys():
        print(k, len(seg[k]))

def test_plot_4_shp_traits(plot_init_potato):
    df = plot_init_potato.get_traits()
    print('\n', list(df.columns))


if __name__ == '__main__':
    pytest.main()
