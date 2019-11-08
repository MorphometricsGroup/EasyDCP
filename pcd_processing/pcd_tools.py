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
    pass

def pcd2binary(pcd, dpi=10):
    # dpi suggest < 20
    pcd_xyz = np.asarray(pcd.points)
    x = pcd_xyz[:, 0]
    y = pcd_xyz[:, 1]
    x_length_m = x.max() - x.min()
    y_length_m = y.max() - y.min()
    px_num_per_cm = int(dpi / 2.54)
    width = int(np.ceil(x_length_m * 100 * px_num_per_cm))
    height = int(np.ceil(y_length_m * 100 * px_num_per_cm))
    ref_x = (x - x.min()) / x_length_m * width
    ref_y = (y - y.min()) / y_length_m * height
    ref_pos = np.vstack([ref_x, ref_y]).T.astype(int)
    ref_pos_rm_dup = np.unique(ref_pos, axis=0)

    out_img = np.zeros((width + 1, height + 1))
    out_img[ref_pos_rm_dup[:, 0], ref_pos_rm_dup[:, 1]] = 1
    out_img = out_img.astype(int)

    return out_img, px_num_per_cm, x.min(), y.min()