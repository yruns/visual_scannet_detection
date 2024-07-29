import numpy as np
import open3d as o3d

import utils

# 读取ply
ply_filename = "resources/scene0000_00_vh_clean_2.ply"
pcd = o3d.io.read_triangle_mesh(ply_filename)

# 将mesh按照axis_align_matrix进行变换
axis_align_matrix = utils.read_axis_align_matrix("resources/scene0000_00.txt")
mesh_vertices = np.asarray(pcd.vertices)
aligned_vertices = utils.align_point_vertices(mesh_vertices, axis_align_matrix)
pcd.vertices = o3d.utility.Vector3dVector(aligned_vertices)

pcd.compute_vertex_normals()

# Add BBox
bbox = np.array([1.48, 3.52, 1.85, 1.74, 0.231, 0.572])
center = bbox[:3]
size = bbox[3:]
# 转成min_bounds max_bounds
bbox = o3d.geometry.AxisAlignedBoundingBox(
    min_bound=np.array(center) - np.array(size) / 2,
    max_bound=np.array(center) + np.array(size) / 2
)

vis = o3d.visualization.Visualizer()
vis.create_window(visible=False, height=1080, width=1920)
vis.add_geometry(pcd)
vis.add_geometry(bbox)

axis = o3d.geometry.TriangleMesh().create_coordinate_frame(size=1, origin=[0, 0, 0])
vis.add_geometry(axis)

# 设置摄像头参数
ctr: o3d.visualization.ViewControl = vis.get_view_control()

camera_pose = np.array([2, 2, 1.6])
camera_lookat = np.array([-2, -1, 1.6])
up = np.array([0, 0, 1])
front_vector = camera_pose - camera_lookat
# front_vector = front_vector / np.linalg.norm(front_vector)

ctr.set_up(up)
ctr.set_front(front_vector)
ctr.set_lookat(camera_lookat)
ctr.set_zoom(0.45)

# 设置光照
# 设置渲染选项
opt = vis.get_render_option()
opt.background_color = np.asarray([0.98, 0.98, 0.98])  # 设置背景颜色

# 渲染一帧
vis.poll_events()
vis.update_renderer()

# 捕捉图像
# image = vis.capture_screen_float_buffer(do_render=True)
vis.capture_screen_image("rendered_image.png", do_render=True)
vis.destroy_window()

utils.plot_image("rendered_image.png")
