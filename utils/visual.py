import os

import numpy as np
import open3d as o3d

from utils import agent, TempFile
from utils.comm import generate_hash, remove_prefix, has_prefix
from utils import constants as const
from utils.scannet import align_point_vertices


def create_scene_with_bbox(scene_path, bboxes, axis_align_matrix, bbox_line_width):
    if has_prefix(scene_path, const.prettify_prefix):
        scene_path = remove_prefix(scene_path, const.prettify_prefix)
    # 加载原始mesh
    mesh = o3d.io.read_triangle_mesh(scene_path)

    if axis_align_matrix is not None:
        # 将mesh按照axis_align_matrix进行变换
        mesh_vertices = np.asarray(mesh.vertices)
        aligned_vertices = align_point_vertices(mesh_vertices, axis_align_matrix)
        mesh.vertices = o3d.utility.Vector3dVector(aligned_vertices)

    # 添加bbox
    if bboxes is not None and len(bboxes) > 0:
        for bbox in bboxes:
            bbox_params, bbox_color = bbox["bbox_params"], bbox["color"]
            for i in range(bbox_params.shape[0]):
                bbox_lineset = create_bbox(bbox_params[i, :3], bbox_params[i, 3:], color=bbox_color, radius=bbox_line_width)
                for box_line in bbox_lineset:
                    mesh += box_line

    mesh = prettify_mesh_for_gradio(mesh)

    file_name = generate_hash(scene_path, bboxes, axis_align_matrix, bbox_line_width)
    file_path = os.path.join(const.temp_path, f"{file_name}.obj")
    o3d.io.write_triangle_mesh(file_path, mesh, write_vertex_colors=True)
    agent.add_temp_file(TempFile(file_path))

    return file_path


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


def create_cylinder_mesh(p0, p1, color, radius=0.02, resolution=50, split=1):
    """Create a colored cylinder mesh between two points p0 and p1."""
    cylinder = o3d.geometry.TriangleMesh.create_cylinder(
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
