import imageio
import numpy as np
import open3d as o3d
from plyfile import PlyData, PlyElement

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