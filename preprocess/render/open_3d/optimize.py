import open3d as o3d
import numpy as np
from scipy.optimize import minimize

# 定义目标物体的3D坐标
object_coords = np.array([
    [x1, y1, z1],
    [x2, y2, z2],
    # 更多的物体坐标
])

# 创建一个点云对象
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(object_coords)

# 计算包围盒
aabb = pcd.get_axis_aligned_bounding_box()
min_coords = aabb.get_min_bound()
max_coords = aabb.get_max_bound()
center = aabb.get_center()

# 初始摄像机位置
camera_distance = np.linalg.norm(max_coords - min_coords) * 1.5
camera_position = center + np.array([0, 0, camera_distance])

# 定义视图矩阵
def get_view_control(vis, camera_position):
    ctr = vis.get_view_control()
    ctr.set_lookat(center)
    ctr.set_up([0, 1, 0])
    ctr.set_front(camera_position - center)
    ctr.set_zoom(1.0)
    return ctr

# 目标函数：最小化所有物体距离视野边缘的距离
def objective_function(camera_position):
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False)
    vis.add_geometry(pcd)

    ctr = get_view_control(vis, camera_position)
    vis.poll_events()
    vis.update_renderer()

    image = vis.capture_screen_float_buffer(do_render=True)
    vis.destroy_window()

    projected_coords = np.array(image)
    distances = np.min([projected_coords[:, 0], 1 - projected_coords[:, 0], projected_coords[:, 1], 1 - projected_coords[:, 1]], axis=0)
    return -np.min(distances)

# 优化摄像机位置
result = minimize(objective_function, camera_position, method='Powell')
optimized_camera_position = result.x

# 创建Open3D可视化窗口并渲染场景
vis = o3d.visualization.Visualizer()
vis.create_window()
vis.add_geometry(pcd)

ctr = get_view_control(vis, optimized_camera_position)
vis.run()
vis.destroy_window()
