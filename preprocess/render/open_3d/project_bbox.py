import cv2
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
bbox = utils.Convertor.convert_bbox_to_o3d_format(bbox, center_type=True)
bbox_corners = np.asarray(bbox.get_box_points())

vis = o3d.visualization.Visualizer()
vis.create_window(visible=False, height=1080, width=1920)
vis.add_geometry(pcd)

# axis = o3d.geometry.TriangleMesh().create_coordinate_frame(size=1, origin=[0, 0, 0])
# vis.add_geometry(axis)


# 设置摄像头参数
ctr: o3d.visualization.ViewControl = vis.get_view_control()

camera_pos = np.array([-2, -2, 0.5])
camera_lookat = np.array([1, 1.5, 1.6])
# camera_pose = np.array([-2.5, 1.3, 2])
# camera_lookat = np.array([2, 1.3, 1.7])
front_vector = camera_pos - camera_lookat
up = utils.compute_up_vector(front_vector)

ctr.set_up(up)
ctr.set_front(front_vector)
ctr.set_lookat(camera_lookat)
ctr.set_zoom(0.42)

# 设置渲染选项
opt = vis.get_render_option()
opt.background_color = np.asarray([0.9, 0.9, 0.9])  # 设置背景颜色
vis.poll_events()
vis.update_renderer()

# 捕捉图像
# image = vis.capture_screen_float_buffer(do_render=True)
vis.capture_screen_image("rendered_image.png", do_render=True)
vis.destroy_window()


top_left, bottom_right = utils.project_bbox_with_pinhole_camera_parameters(
    camera_params=ctr.convert_to_pinhole_camera_parameters(),
    bboxes=bbox
)

# 读取渲染后的图像
image = cv2.imread("rendered_image.png")
# 将2D BBox画在图像上
image = cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), 2)

# 添加order
image = utils.add_order_to_image(
    image=image, order=2, top_left=top_left, size=(30, 40), return_rgb=True
)

# 显示图像
cv2.imshow('Image with Rectangle', image)
utils.plot_image(image)


