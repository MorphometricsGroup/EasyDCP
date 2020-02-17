import __init__
import pytest
import numpy as np
import phenotypy as pnt

def test_pcd_read_ply():
    ply = pnt.read_ply('data/potato.ply')
    print('\n', ply)

def test_pcd_read_plys():
    ply_merged = pnt.read_plys(['data/weed.plant0.ply', 'data/weed.cleanedbg.ply'])
    ply1 = pnt.read_ply('data/weed.plant0.ply')
    ply2 = pnt.read_ply('data/weed.cleanedbg.ply')
    assert len(ply1.points) + len(ply2.points) == len(ply_merged.points)

def test_pcd_read_ply_unit():
    units = ['m', 'dm', 'cm', 'mm', 'km']
    divider = [1, 10, 100, 1000, 0.001]
    for i, u in enumerate(units):
        ply = pnt.read_ply('data/potato.ply', unit=u)
        p1 = np.asarray(ply.points)[0, 1]
        assert (11/divider[i]) < p1 and p1 < (12/divider[i])

    wrong_units = ['pm', 0, 'asd', 0.001]
    for wu in wrong_units:
        with pytest.raises(TypeError) as excinfo:
            ply = pnt.read_ply('data/potato.ply', unit=wu)
            print('\n', excinfo.value)
        assert "as unit, please only tape m, cm, mm, or km." in str(excinfo.value)

def test_pcd_read_planteye_wrong_unit():
    ply = pnt.read_ply('data/down_sample/down_sample_M.ply', unit='m')

def test_pcd_read_planteye_right_unit():
    ply = pnt.read_ply('data/down_sample/down_sample_M.ply', unit='mm')


@pytest.fixture(scope="session", autouse=True)
def shp_config():
    p1 = 'data/potato_field1plot.shp'
    p2 = 'data/potato_field2plot.shp'
    cc = (367912.000, 3955467.000, 98.000)

    return {'p1':p1, 'p2':p2, 'cc':cc}

def test_shp_read_shp(shp_config):
    shp = pnt.read_shp(shp_config['p1'])
    print('\n', shp.keys())

def test_shp_read_shps(shp_config):
    shp1 = pnt.read_shp(shp_config['p1'])
    shp2 = pnt.read_shp(shp_config['p2'])
    shp_merge = pnt.read_shps([shp_config['p1'], shp_config['p2']])
    assert len(shp_merge) == len(shp1) + len(shp2)

def test_shp_read_shps_overwrite(shp_config):
    shp_merge = pnt.read_shps([shp_config['p1'], shp_config['p1']], rename=False)

def test_shp_read_shps_correct_coord_one4all(shp_config):
    shp_merge = pnt.read_shps([shp_config['p1'], shp_config['p2']], shp_config['cc'])

def test_shp_read_shps_correct_coord_wrong4all(shp_config):
    with pytest.raises(ValueError) as excinfo:
        shp_merge = pnt.read_shps([shp_config['p1'], shp_config['p2']], [shp_config['cc'], ])
        print('\n', excinfo.value)
    assert "The number of shp files" in str(excinfo.value)