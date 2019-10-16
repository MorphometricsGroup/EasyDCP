import imageio
import numpy as np
import open3d as o3d
from PIL import Image
from datetime import datetime
from plyfile import PlyData, PlyElement
from sklearn.tree import DecisionTreeClassifier

def read_ply(file_path):
    pcd = o3d.io.read_point_cloud(file_path)
    if not pcd.has_colors():
        cloud_ply = PlyData.read(file_path)
        cloud_data = cloud_ply.elements[0].data
        ply_names = cloud_data.dtype.names
        
        if 'red' in ply_names:
            colors = np.vstack((cloud_data['red']/255, cloud_data['green']/255, cloud_data['blue']/255)).T
            pcd.colors = o3d.utility.Vector3dVector(colors)
        elif 'diffuse_red' in ply_names:
            colors = np.vstack((cloud_data['diffuse_red']/255, cloud_data['diffuse_green']/255, cloud_data['diffuse_blue']/255)).T
            pcd.colors = o3d.utility.Vector3dVector(colors)
        else:
            print('Can not find color info in ',ply_names)
            
    return pcd

def read_png(file_path):
    img_ndarray = imageio.imread(file_path)
    h, w, d = img_ndarray.shape
    img_2d = img_ndarray.reshape(h * w, d)
    img_np = img_2d[img_2d[:,3] == 255, 0:3] / 255
    
    return img_np
    
def build_clf(fore_path, back_path):
    back_np = read_png(back_path)
    fore_np = read_png(fore_path)
    
    kind_back = np.array([0] * back_np.shape[0]) 
    kind_fore = np.array([1] * fore_np.shape[0])
    
    train_data = np.vstack([back_np, fore_np])
    train_kind = np.hstack([kind_back, kind_fore])
    
    clf = DecisionTreeClassifier(max_depth=20)
    clf = clf.fit(train_data, train_kind)
    
    return clf
    
def classifier_apply(pcd, clf):
    pcd_xyz_np = np.asarray(pcd.points)
    pcd_color_np = np.asarray(pcd.colors)
    
    pred_result = clf.predict(pcd_color_np)
    
    pcd_fore = o3d.geometry.PointCloud()
    pcd_fore.points = o3d.utility.Vector3dVector(pcd_xyz_np[pred_result == 1, :])
    pcd_fore.colors = o3d.utility.Vector3dVector(pcd_color_np[pred_result == 1, :])
    
    pcd_back = o3d.geometry.PointCloud()
    pcd_back.points = o3d.utility.Vector3dVector(pcd_xyz_np[pred_result != 1, :])
    pcd_back.colors = o3d.utility.Vector3dVector(pcd_color_np[pred_result != 1, :])
    
    return pcd_fore, pcd_back

def pcd_size(pcd):
    pcd_xyz = np.asarray(pcd.points)
    
    x_max = pcd_xyz[:,0].max()
    x_min = pcd_xyz[:,0].min()
    x_len = x_max - x_min
    
    y_max = pcd_xyz[:,1].max()
    y_min = pcd_xyz[:,1].min()
    y_len = y_max - y_min
    
    z_max = pcd_xyz[:,2].max()
    z_min = pcd_xyz[:,2].min()
    z_len = z_max - z_min
    
    shape_info = {'x_min':x_min, 'x_max':x_max, 'x_len': x_len, 
                  'y_min':y_min, 'y_max':y_max, 'y_len': y_len, 
                  'z_min':z_min, 'z_max':z_max, 'z_len': z_len}
    
    return shape_info


def pcd2voxel(pcd, part):
    # part: how many part of the shortest axis will be splitted?
    s = pcd_size(pcd)
    
    # convert point cloud to voxel
    voxel_size = min(s['x_len'], s['y_len'], s['z_len']) / part
    pcd_voxel = o3d.geometry.VoxelGrid().create_from_point_cloud(pcd, voxel_size=voxel_size)
    
    return pcd_voxel, voxel_size, s
    
def pcd2raster(pcd, part=500):
    '''
    Convert pcd to DOM and Depth DSM
    However, holes needs to be filled in the future
    '''
   
    # convert point cloud to voxel
    pcd_voxel, voxel_size, s = pcd2voxel(pcd, part)
    
    # generate the size of rasters image
    x_num = (np.ceil(s['x_len'] / voxel_size) + 1).astype(int)
    y_num = (np.ceil(s['y_len'] / voxel_size) + 1).astype(int)
    ## generate empty raster
    z_np = np.zeros((x_num, y_num))
    dom_np = np.zeros((x_num, y_num, 4))

    # loop for each voxel (open3d wrap voxel by list, not to numpy directly)
    print('Start Converting 3D to 2D, this may take some time')
    t0 = datetime.now()
    for i in pcd_voxel.voxels:
        x,y,z = i.grid_index
        rgb = (i.color * 255).astype(np.uint8)

        if z_np[x, y] < z:
            z_np[x, y] = z
            dom_np[x, y, 0:3] = rgb
            dom_np[x, y, 3] = 255

    print(datetime.now() - t0)
    
    # making dom to writable type
    dom_np = dom_np.astype(np.uint8)
    
    # normalize depth back to point cloud z value
    d_max = z_np.max()
    d_min = z_np.min()
    d_len = d_max - d_min
    depth = z_np / d_len * s['z_len'] - s['z_min']
    
    return dom_np, depth