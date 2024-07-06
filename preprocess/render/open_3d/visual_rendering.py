import open3d as o3d
from open3d.visualization import rendering
import numpy as np

def align_point_vertices(mesh_vertices, axis_align_matrix):
    """
    Align the vertices of a mesh using the given axis align matrix.
    """
    pts = np.ones((mesh_vertices.shape[0], 4))
    pts[:, 0:3] = mesh_vertices[:, 0:3]
    pts = np.dot(pts, axis_align_matrix.transpose())  # Nx4
    aligned_vertices = np.copy(mesh_vertices)
    aligned_vertices[:, 0:3] = pts[:, 0:3]
    return aligned_vertices

def read_axis_align_matrix(meta_file):
    """
    Read axis alignment matrix from meta file
    e.g. meta_file = scene0000_00.txt
    """
    axis_align_matrix = None
    lines = open(meta_file).readlines()
    for line in lines:
        if 'axisAlignment' in line:
            axis_align_matrix = [float(x) for x in line.rstrip().strip('axisAlignment = ').split(' ')]
            axis_align_matrix = np.array(axis_align_matrix).reshape((4, 4))

    return axis_align_matrix


# 读取ply
ply_filename = "scene0000_00_vh_clean_2.ply"
pcd = o3d.io.read_triangle_mesh(ply_filename)

# 将mesh按照axis_align_matrix进行变换
axis_align_matrix = read_axis_align_matrix("scene0000_00.txt")
mesh_vertices = np.asarray(pcd.vertices)
aligned_vertices = align_point_vertices(mesh_vertices, axis_align_matrix)
pcd.vertices = o3d.utility.Vector3dVector(aligned_vertices)

vis = o3d.visualization.Visualizer()
vis.create_window(visible=False, height=1080, width=1920)
vis.add_geometry(pcd)

axis = o3d.geometry.TriangleMesh().create_coordinate_frame(size=1, origin=[0, 0, 0])
vis.add_geometry(axis)

# 设置摄像头参数
ctr = vis.get_view_control()
ctr.set_up([0, 0, 1])
ctr.set_front([2, 2, 1.6])
ctr.set_lookat([-2, -1, 1.6])
ctr.set_zoom(0.5)

# 设置光照
# 设置渲染选项
opt = vis.get_render_option()
opt.background_color = np.asarray([0.9, 0.9, 0.9])  # 设置背景颜色

# 渲染一帧
vis.poll_events()
vis.update_renderer()

# 捕捉图像
# image = vis.capture_screen_float_buffer(do_render=True)
vis.capture_screen_image("rendered_image.png", do_render=True)
vis.destroy_window()

import matplotlib.pyplot as plt
plt.figure(figsize=(20, 11))
plt.axis('off')
image = plt.imread("rendered_image.png")
plt.imshow(image)
plt.show()

# # 显示img
# import matplotlib.pyplot as plt
# plt.figure(figsize=(20, 11))
# # 不显示横纵坐标
# plt.axis('off')
# # 显示图片
# plt.imshow(image)
# plt.show()
