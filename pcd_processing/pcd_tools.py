import numpy as np
import open3d as o3d
from plyfile import PlyData

def read_ply(file_path):
    pcd = o3d.io.read_point_cloud(file_path)
    if not pcd.has_colors():
        cloud_ply = PlyData.read(file_path)
        cloud_data = cloud_ply.elements[0].data
        ply_names = cloud_data.dtype.names

        if 'red' in ply_names:
            colors = np.vstack((cloud_data['red'] / 255, cloud_data['green'] / 255, cloud_data['blue'] / 255)).T
            pcd.colors = o3d.utility.Vector3dVector(colors)
        elif 'diffuse_red' in ply_names:
            colors = np.vstack((cloud_data['diffuse_red'] / 255, cloud_data['diffuse_green'] / 255,
                                cloud_data['diffuse_blue'] / 255)).T
            pcd.colors = o3d.utility.Vector3dVector(colors)
        else:
            print('Can not find color info in ', ply_names)

    return pcd

def merge_pcd(pcd_list):
    final_pcd = o3d.geometry.PointCloud()
    xyz = np.empty((0, 3))
    rgb = np.empty((0, 3))

    for pcd in pcd_list:
        pcd_xyz = np.asarray(pcd.points)
        pcd_rgb = np.asarray(pcd.colors)

        xyz = np.vstack([xyz, pcd_xyz])
        rgb = np.vstack([rgb, pcd_rgb])

    final_pcd.points = o3d.utility.Vector3dVector(xyz)
    final_pcd.colors = o3d.utility.Vector3dVector(rgb)

    return final_pcd

def pcd2dom(pcd, voxel_size):
    down_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)