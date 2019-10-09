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