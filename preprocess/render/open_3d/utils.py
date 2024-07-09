"""
File: utils.py
Date: 2024/7/8
Author: yruns

Description: This file contains ...
"""
import cv2
import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d


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


def create_cylinder_mesh(p0, p1, color, radius=0.02, resolution=50, split=1):
    """Create a colored cylinder mesh between two points p0 and p1."""
    cylinder = o3d.geometry.TriangleMesh().create_cylinder(
        radius=radius, height=1, resolution=resolution, split=split
    )
    transformation = cylinder_frame(p0, p1)
    cylinder.transform(transformation)
    # Apply color
    cylinder.paint_uniform_color(color)
    return cylinder


def cylinder_frame(p0, p1):
    """Calculate the transformation matrix to position a unit cylinder between two points."""
    direction = np.asarray(p1) - np.asarray(p0)
    length = np.linalg.norm(direction)
    direction /= length
    # Computing rotation matrix using Rodrigues' formula
    rot_axis = np.cross([0, 0, 1], direction)
    rot_angle = np.arccos(np.dot([0, 0, 1], direction))
    rot_matrix = o3d.geometry.get_rotation_matrix_from_axis_angle(rot_axis * rot_angle)

    # Translation
    translation = (np.asarray(p0) + np.asarray(p1)) / 2

    transformation = np.eye(4)
    transformation[:3, :3] = rot_matrix
    transformation[:3, 3] = translation
    scaling = np.eye(4)
    scaling[2, 2] = length
    transformation = np.matmul(transformation, scaling)
    return transformation


def plot_image(image, figsize=(20, 11), axis=False):
    plt.figure(figsize=figsize)
    # 不显示横纵坐标
    plt.axis("on" if axis else "off")
    # 显示图片
    if isinstance(image, np.ndarray):
        plt.imshow(image)
    elif isinstance(image, str):
        plt.imshow(plt.imread(image))
    plt.show()


def add_order_to_image(
        image, order, top_left, size=(50, 50), font_color=(255, 255, 255), font_size=1,
        background_color=(0, 0, 255)
) -> np.ndarray:
    if isinstance(image, str):
        image = cv2.imread(image)
    # 定义颜色块的位置和尺寸
    width, height = size
    bottom_right = (top_left[0] + width, top_left[1] + height)

    # 在图像上画一个矩形作为颜色块
    cv2.rectangle(image, top_left, bottom_right, background_color, -1)  # -1 表示填充矩形

    # 添加数字
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = str(order)
    font_thickness = 3  # 文本粗细
    text_size = cv2.getTextSize(text, font, font_size, font_thickness)[0]
    text_x = top_left[0] + (width - text_size[0]) // 2
    text_y = top_left[1] + (height + text_size[1]) // 2
    cv2.putText(image, text, (text_x, text_y), font, font_size, font_color, font_thickness)

    return image


def project_bbox_with_pinhole_camera_parameters(
        camera_params: o3d.camera.PinholeCameraParameters,
        bbox: o3d.geometry.AxisAlignedBoundingBox
) -> tuple:
    bbox_corners = np.asarray(bbox.get_box_points())
    # 获取相机参数
    intrinsic = camera_params.intrinsic
    extrinsic = camera_params.extrinsic

    # 将 bbox 的 3D 点转换为齐次坐标
    bbox_points_homogeneous = np.hstack((bbox_corners, np.ones((bbox_corners.shape[0], 1))))

    # 将 3D 点从世界坐标系转换为相机坐标系
    camera_points = np.dot(extrinsic, bbox_points_homogeneous.T).T

    # 将相机坐标系的 3D 点转换为 2D 图像坐标
    fx, fy = intrinsic.get_focal_length()
    cx, cy = intrinsic.get_principal_point()
    camera_points_2d = np.zeros((camera_points.shape[0], 2))

    for i in range(camera_points.shape[0]):
        x, y, z = camera_points[i][:3]
        u = (fx * x / z) + cx
        v = (fy * y / z) + cy
        camera_points_2d[i] = [u, v]

    # 在图像上绘制2D BBox
    min_x, min_y = np.min(camera_points_2d, axis=0)
    max_x, max_y = np.max(camera_points_2d, axis=0)

    top_left = (int(min_x), int(min_y))
    bottom_right = (int(max_x), int(max_y))

    return top_left, bottom_right


def convert_bbox_to_o3d_format(bbox: np.ndarray, center_type=True) -> o3d.geometry.AxisAlignedBoundingBox:
    if center_type:
        center, size = bbox[:3], bbox[3:]
        # Create an o3d.geometry.AxisAlignedBoundingBox object
        return o3d.geometry.AxisAlignedBoundingBox(
            min_bound=np.array(center) - np.array(size) / 2,
            max_bound=np.array(center) + np.array(size) / 2
        )

    return o3d.geometry.AxisAlignedBoundingBox(min_bound=bbox[:3], max_bound=bbox[3:])


def project_bbox_with_view_projection_matrix(point, view_matrix, projection_matrix, screen_width, screen_height):
    # Transform the point to homogeneous coordinates
    point_h = np.append(point, 1)
    # Apply the view matrix followed by the projection matrix
    point_view = np.dot(view_matrix, point_h)
    point_proj = np.dot(projection_matrix, point_view)
    # Perform perspective division
    point_ndc = point_proj[:3] / point_proj[3]
    # Convert from NDC to screen coordinates
    x_screen = (point_ndc[0] * 0.5 + 0.5) * screen_width
    y_screen = (1 - point_ndc[1] * 0.5 - 0.5) * screen_height
    return x_screen, y_screen


def is_bbox_in_camera_view(
        camera_params: o3d.camera.PinholeCameraParameters, bbox: o3d.geometry.AxisAlignedBoundingBox
) -> bool:
    # 提取相机内参和外参
    intrinsics = camera_params.intrinsic.intrinsic_matrix
    extrinsics = camera_params.extrinsic

    # 获取包围盒的八个顶点
    bbox_vertices = np.array(bbox.get_box_points())

    # 将包围盒顶点从世界坐标系转换到相机坐标系
    ones = np.ones((bbox_vertices.shape[0], 1))
    bbox_vertices_homogeneous = np.hstack((bbox_vertices, ones))
    bbox_vertices_camera = np.dot(extrinsics, bbox_vertices_homogeneous.T).T

    # 将相机坐标系的顶点转换到像素坐标系
    fx, fy = intrinsics[0, 0], intrinsics[1, 1]
    cx, cy = intrinsics[0, 2], intrinsics[1, 2]

    bbox_vertices_camera = bbox_vertices_camera[:, :3]  # 去掉齐次坐标
    bbox_vertices_pixel = np.zeros((bbox_vertices_camera.shape[0], 2))
    bbox_vertices_pixel[:, 0] = (bbox_vertices_camera[:, 0] * fx / bbox_vertices_camera[:, 2]) + cx
    bbox_vertices_pixel[:, 1] = (bbox_vertices_camera[:, 1] * fy / bbox_vertices_camera[:, 2]) + cy

    # 检查顶点是否在图像范围内
    image_width, image_height = intrinsics[0, 2] * 2, intrinsics[1, 2] * 2
    in_view = np.all((bbox_vertices_pixel[:, 0] >= 0) & (bbox_vertices_pixel[:, 0] < image_width) &
                     (bbox_vertices_pixel[:, 1] >= 0) & (bbox_vertices_pixel[:, 1] < image_height) &
                     (bbox_vertices_camera[:, 2] > 0))

    return in_view
