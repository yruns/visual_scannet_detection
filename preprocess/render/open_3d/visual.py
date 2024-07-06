import os
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


# 读取ply
ply_filename = "scene0000_00_vh_clean_2.ply"
pcd = o3d.io.read_triangle_mesh(ply_filename)

# 将mesh按照axis_align_matrix进行变换
axis_align_matrix = read_axis_align_matrix("scene0000_00.txt")
mesh_vertices = np.asarray(pcd.vertices)
aligned_vertices = align_point_vertices(mesh_vertices, axis_align_matrix)
pcd.vertices = o3d.utility.Vector3dVector(aligned_vertices)

camera_pos = [-3, 1.3, 1.6]
camera_look_at = [2, 1.3, 1.6]

line_set = create_cylinder_mesh(camera_pos, camera_look_at, [0, 1, 0], radius=0.02, resolution=50, split=1)
pcd += line_set

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

# 写label，标注出红色点和绿色点的坐标
o3d.visualization.draw_geometries([pcd, camera_model, camera_look_at_sphere, axis])


