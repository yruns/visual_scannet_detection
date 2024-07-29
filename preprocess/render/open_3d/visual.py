import numpy as np
import open3d as o3d

from utils import read_axis_align_matrix, align_point_vertices, create_cylinder_mesh

# 读取ply
ply_filename = "resources/scene0025_00_vh_clean_2.ply"
mesh = o3d.io.read_triangle_mesh(ply_filename)

# 将mesh按照axis_align_matrix进行变换
axis_align_matrix = read_axis_align_matrix("resources/scene0025_00.txt")
mesh_vertices = np.asarray(mesh.vertices)
aligned_vertices = align_point_vertices(mesh_vertices, axis_align_matrix)
mesh.vertices = o3d.utility.Vector3dVector(aligned_vertices)


camera_pos = [-3, 1.3, 1.6]
camera_look_at = [2, 1.3, 1.6]

line_set = create_cylinder_mesh(camera_pos, camera_look_at, [0, 1, 0], radius=0.02, resolution=50, split=1)
# mesh += line_set

# 在场景中画出相机方向
camera_model = o3d.io.read_triangle_mesh("camera.ply")
camera_model.paint_uniform_color([1, 0, 0])  # 红色
camera_model.translate(camera_pos)
camera_model.scale(0.002, center=camera_pos)
# camera_model.rotate(axis_align_matrix)
camera_look_at_sphere = o3d.geometry.TriangleMesh().create_sphere(radius=0.1)
camera_look_at_sphere.translate(camera_look_at)
camera_look_at_sphere.paint_uniform_color([0, 1, 0])  # 绿色

z_rotation_matrix = camera_model.get_rotation_matrix_from_xyz((-np.pi / 2, 0, 0))
camera_model.rotate(z_rotation_matrix, center=camera_pos)

# 计算相机方向
direction = np.array(camera_look_at) - np.array(camera_pos)
direction = direction / np.linalg.norm(direction)  # 归一化方向向量

# 计算旋转矩阵
up = np.array([0, 0, 1])  # 设定一个上方向
right = np.cross(up, direction)
right = right / np.linalg.norm(right)
up = np.cross(direction, right)

rotation_matrix = np.vstack([right, up, direction]).T
camera_model.rotate(rotation_matrix, center=camera_pos)

# 在场景中画出坐标轴
axis = o3d.geometry.TriangleMesh().create_coordinate_frame(size=1.0, origin=[0, 0, 0])
# 标注x,y, z轴

vis = o3d.visualization.Visualizer()
vis.create_window(window_name="Open3D", width=1920, height=1080)

# 设置显示参数
render_option = vis.get_render_option()
render_option.point_size = 2.0
render_option.line_width = 1.0
render_option.background_color = np.array([1, 1, 1])  # 白色背景

# 给face加上shading
# mesh.compute_vertex_normals()
# mesh.compute_triangle_normals()


vis.add_geometry(mesh)
# vis.add_geometry(camera_model)
# vis.add_geometry(camera_look_at_sphere)
# vis.add_geometry(axis)
vis.run()
# vis.destroy_window()

# 写label，标注出红色点和绿色点的坐标
# o3d.visualization.draw_geometries([mesh, camera_model, camera_look_at_sphere, axis])
