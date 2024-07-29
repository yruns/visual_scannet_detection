import os

import cv2
import numpy as np
import open3d as o3d

import utils

scene_name = "scene0000_00"

# 读取ply
ply_filename = f"resources/{scene_name}_vh_clean_2.ply"
pcd: o3d.geometry.TriangleMesh = o3d.io.read_triangle_mesh(ply_filename)

# 将mesh按照axis_align_matrix进行变换
axis_align_matrix = utils.read_axis_align_matrix(f"resources/{scene_name}.txt")
mesh_vertices = np.asarray(pcd.vertices)
aligned_vertices = utils.align_point_vertices(mesh_vertices, axis_align_matrix)
pcd.vertices = o3d.utility.Vector3dVector(aligned_vertices)

# pcd.compute_vertex_normals()

# Add BBox
bbox1 = [1.146, 2.198, 0.61649, 0.541, 2.534, 1.214]
bbox1 = utils.Convertor.convert_bbox_to_o3d_format(bbox1, center_type=True)

bbox2 = [1.48, 3.52, 1.85, 1.74, 0.231, 0.572]
bbox2 = utils.Convertor.convert_bbox_to_o3d_format(bbox2, center_type=True)

vis = o3d.visualization.Visualizer()
vis.create_window(visible=False, height=1080, width=1920)
vis.add_geometry(pcd)

def create_view(camera_pos, camera_lookat):
    # 设置摄像头参数
    ctr: o3d.visualization.ViewControl = vis.get_view_control()

    front_vector = camera_pos - camera_lookat
    up = utils.compute_up_vector(front_vector)

    ctr.set_up(up)
    ctr.set_front(front_vector)
    ctr.set_lookat(camera_lookat)
    ctr.set_zoom(0.45)

    # 设置渲染选项
    opt = vis.get_render_option()
    opt.background_color = np.asarray([0.9, 0.9, 0.9])  # 设置背景颜色
    vis.poll_events()
    vis.update_renderer()

    # 捕捉图像
    image = vis.capture_screen_float_buffer(do_render=True)
    image = utils.Convertor.convert_o3d_image_to_cv2_image(image)

    # cv2.imshow("rendered_image", image)
    # cv2.waitKey(0)

    bbox_corners_2d = utils.project_bbox_with_pinhole_camera_parameters(
        camera_params=ctr.convert_to_pinhole_camera_parameters(),
        bboxes=[bbox1, bbox2], return_wherther_in_view=True
    )

    # 将2D BBox画在图像上
    for idx, (top_left, bottom_right, is_in_view) in enumerate(bbox_corners_2d):
        print("is_in_view: ", is_in_view)
        image = cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), thickness=3)

        # 添加order
        image = utils.add_order_to_image(
            image=image, order=idx, top_left=top_left, size=(30, 40), return_rgb=False
        )

    # 显示图像
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    utils.plot_image(image)

    return image

center = pcd.get_center()
max_bound = pcd.get_max_bound()
min_bound = pcd.get_min_bound()

scene_circle_r = max(np.max(np.abs(min_bound - center)[:2]), np.max(np.abs(max_bound - center)[:2]))

os.makedirs("views", exist_ok=True)
view_nums = 6
for view_idx in range(view_nums):
    camera_lookat = pcd.get_center()
    z_height = 3
    angle = view_idx * 2 * np.pi / view_nums
    camera_pos = np.array([scene_circle_r * np.sin(angle), scene_circle_r * np.cos(angle), z_height])

    image = create_view(camera_pos, camera_lookat)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    cv2.imwrite(f"views/view_{view_idx}.png", image)


