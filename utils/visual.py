import copy
import os
import queue
import time
import threading

import numpy as np
import open3d as o3d
import uuid

from utils import agent, TempFile
from utils import comm
from utils.comm import generate_hash, remove_prefix, has_prefix
from utils import constants as const
from utils.scannet import align_point_vertices


def create_scene_with_bbox(
        scene_path, bboxes, axis_align_matrix, show_axis, bbox_line_width,
        camera_lookat, camera_pos, render_checkgroup
):
    if has_prefix(scene_path, const.prettify_prefix):
        scene_path = remove_prefix(scene_path, const.prettify_prefix)
    # 加载原始mesh
    mesh = o3d.io.read_triangle_mesh(scene_path)

    if axis_align_matrix is not None:
        # 将mesh按照axis_align_matrix进行变换
        mesh_vertices = np.asarray(mesh.vertices)
        aligned_vertices = align_point_vertices(mesh_vertices, axis_align_matrix)
        mesh.vertices = o3d.utility.Vector3dVector(aligned_vertices)

    mesh_scene_only = None
    if const.scene_only_option in render_checkgroup:
        mesh_scene_only = copy.deepcopy(mesh)

    # 添加坐标轴
    if show_axis:
        axis = o3d.geometry.TriangleMesh().create_coordinate_frame(size=1.0, origin=[0, 0, 0])
        mesh += axis

    # 添加bbox
    if bboxes is not None and len(bboxes) > 0:
        for bbox in bboxes:
            bbox_params, bbox_color = bbox["bbox_params"], bbox["color"]
            for i in range(bbox_params.shape[0]):
                bbox_lineset = create_bbox(bbox_params[i, :3], bbox_params[i, 3:], color=bbox_color, radius=bbox_line_width)
                for box_line in bbox_lineset:
                    mesh += box_line

    projection = None
    # 添加相机
    if camera_lookat is not None and camera_pos is not None:
        camera_model, camera_look_at_sphere, line_set = create_camera_with_lookat(camera_pos, camera_lookat)
        projection = render_projection(
            mesh_scene_only if const.scene_only_option in render_checkgroup else mesh,
            camera_pos, camera_lookat, render_checkgroup
        )
        # to numpy
        projection = np.asarray(projection)
        mesh += (camera_model + camera_look_at_sphere + line_set)

    mesh = prettify_mesh_for_gradio(mesh)

    file_name = generate_hash(scene_path, bboxes, axis_align_matrix, show_axis, bbox_line_width)
    model3d_path = os.path.join(const.temp_path, f"{file_name}.obj")
    o3d.io.write_triangle_mesh(model3d_path, mesh, write_vertex_colors=True)
    agent.add_temp_file(TempFile(model3d_path))

    return model3d_path, projection


def render_projection_macos(mesh, camera_pos, camera_lookat, render_checkgroup):
    if const.sharp_option in render_checkgroup:
        mesh.compute_vertex_normals()
    vis = o3d.visualization.Visualizer()
    vis.create_window(height=const.render_projection_size[1], width=const.render_projection_size[0], visible=False)
    vis.add_geometry(mesh)

    # 设置摄像头参数
    ctr = vis.get_view_control()
    ctr.set_up([0, 0, 1])
    ctr.set_front(camera_pos - camera_lookat)
    ctr.set_lookat(camera_lookat)
    ctr.set_zoom(const.render_zoom)

    # 设置渲染选项
    opt = vis.get_render_option()
    opt.background_color = np.asarray(const.render_projection_background_color[:3])  # 设置背景颜色

    # 渲染一帧
    vis.poll_events()
    vis.update_renderer()

    # 捕捉图像
    # file_path = os.path.join(const.temp_path, f"{uuid.uuid4()}.png")
    # vis.capture_screen_image(file_path, do_render=True)
    image = vis.capture_screen_float_buffer(do_render=True)
    vis.destroy_window()

    return image


def render_projection_linux(mesh, camera_pos, camera_lookat):
    from open3d.visualization import rendering

    render = rendering.OffscreenRenderer(height=const.render_projection_size[1], width=const.render_projection_size[0])

    grey = rendering.MaterialRecord()
    grey.base_color = const.render_projection_background_color
    grey.shader = "defaultLit"
    mesh.compute_vertex_normals()

    render.scene.add_geometry("mesh", mesh, grey)
    render.setup_camera(70.0, camera_lookat, camera_pos, [0, 0, 1])
    render.scene.scene.set_sun_light([0.707, 0.0, -.707], [1.0, 1.0, 1.0], 75000)
    render.scene.scene.enable_sun_light(False)

    img = render.render_to_image()
    # file_path = os.path.join(const.temp_path, f"{uuid.uuid4()}.png")
    # o3d.io.write_image(file_path, img, 9)

    return img


def render_projection(mesh, camera_pos, camera_lookat, render_checkgroup):
    os_type = comm.get_system_type()
    if os_type == comm.OsType.MacOS:
        return render_projection_macos(mesh, camera_pos, camera_lookat, render_checkgroup)
    elif os_type == comm.OsType.Linux:
        if const.precise_option in render_checkgroup:
            return render_projection_linux(mesh, camera_pos, camera_lookat)
        else:
            return render_projection_macos(mesh, camera_pos, camera_lookat, render_checkgroup)
    else:
        raise NotImplementedError(f"Unsupported OS type: {os_type} for rendering projection")


def prettify_mesh_for_gradio(mesh):
    # Define the transformation matrix
    T = np.array([[0, -1, 0, 0], [0, 0, 1, 0], [-1, 0, 0, 0], [0, 0, 0, 1]])

    # Apply the transformation
    mesh.transform(T)

    mesh.scale(10.0, center=mesh.get_center())

    bright_factor = 1  # Adjust this factor to get the desired brightness
    mesh.vertex_colors = o3d.utility.Vector3dVector(
        np.clip(np.asarray(mesh.vertex_colors) * bright_factor, 0, 1)
    )

    return mesh

def create_camera_with_lookat(camera_pos, camera_lookat):
    # 添加一条线，表示相机方向
    direction_line = create_cylinder_mesh(camera_pos, camera_lookat, [0, 1, 0], radius=0.01, resolution=50, split=1)

    # 在场景中画出相机方向
    camera_model = o3d.io.read_triangle_mesh(const.camera_model_path)
    camera_model.paint_uniform_color([1, 0, 0])  # 红色
    camera_model.translate(camera_pos)
    camera_model.scale(0.002, center=camera_pos)
    # camera_model.rotate(axis_align_matrix)
    camera_look_at_sphere = o3d.geometry.TriangleMesh().create_sphere(radius=0.1)
    camera_look_at_sphere.translate(camera_lookat)
    camera_look_at_sphere.paint_uniform_color([0, 1, 0])  # 绿色

    rotation_matrix = camera_model.get_rotation_matrix_from_xyz((-np.pi / 2, 0, 0))
    camera_model.rotate(rotation_matrix, center=camera_pos)

    # 计算相机方向
    direction = np.array(camera_lookat) - np.array(camera_pos)
    direction = direction / np.linalg.norm(direction)  # 归一化方向向量

    # 计算旋转矩阵
    up = np.array([0, 0, 1])  # 设定一个上方向
    right = np.cross(up, direction)
    right = right / np.linalg.norm(right)
    up = np.cross(direction, right)

    rotation_matrix = np.vstack([right, up, direction]).T
    camera_model.rotate(rotation_matrix, center=camera_pos)

    return camera_model, direction_line, camera_look_at_sphere


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


def create_bbox(center, extents, color=[1, 0, 0], radius=0.02):
    """Create a colored bounding box with given center, extents, and line thickness."""
    # ... [The same code as before to define corners and lines] ...
    sx, sy, sz = extents
    x_corners = [sx / 2, sx / 2, -sx / 2, -sx / 2, sx / 2, sx / 2, -sx / 2, -sx / 2]
    y_corners = [sy / 2, -sy / 2, -sy / 2, sy / 2, sy / 2, -sy / 2, -sy / 2, sy / 2]
    z_corners = [sz / 2, sz / 2, sz / 2, sz / 2, -sz / 2, -sz / 2, -sz / 2, -sz / 2]
    corners_3d = np.vstack([x_corners, y_corners, z_corners])
    corners_3d[0, :] = corners_3d[0, :] + center[0]
    corners_3d[1, :] = corners_3d[1, :] + center[1]
    corners_3d[2, :] = corners_3d[2, :] + center[2]
    corners_3d = np.transpose(corners_3d)

    lines = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [5, 6],
        [6, 7],
        [7, 4],
        [0, 4],
        [1, 5],
        [2, 6],
        [3, 7],
    ]
    cylinders = []
    for line in lines:
        p0, p1 = corners_3d[line[0]], corners_3d[line[1]]
        cylinders.append(create_cylinder_mesh(p0, p1, color, radius))
    return cylinders
