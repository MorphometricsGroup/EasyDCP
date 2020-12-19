import __init__
import pytest
import easydcp as dcp

@pytest.fixture(scope="session", autouse=True)
def plant_init():
    plant = dcp.Plant('data/weed.plant0.ply', indices=0, ground_pcd='data/weed.cleanedbg.ply',
                      cut_bg=True, container_ht=0.06)
    return plant

def test_plant_height(plant_init):
    print(plant_init.pctl_ht)

def test_draw_plant(plant_init):
    plant_init.draw_3d_results('output/weed')