import cv2
import numpy as np
import open3d as o3d
from open3d.visualization import rendering

from utils import read_axis_align_matrix, align_point_vertices, plot_image

render = rendering.OffscreenRenderer(1920, 1080)

grey = rendering.MaterialRecord()
grey.base_color = [0.9, 0.9, 0.9, 1.0]
grey.shader = "defaultLit"

# 读取 PLY 文件
mesh = o3d.io.read_triangle_mesh("resources/scene0000_00_vh_clean_2.ply")
# 将mesh按照axis_align_matrix进行变换
axis_align_matrix = read_axis_align_matrix("resources/scene0000_00.txt")
mesh_vertices = np.asarray(mesh.vertices)
aligned_vertices = align_point_vertices(mesh_vertices, axis_align_matrix)
mesh.vertices = o3d.utility.Vector3dVector(aligned_vertices)
mesh.compute_vertex_normals()

render.scene.add_geometry("mesh", mesh, grey)
render.setup_camera(70.0, [1, 1, 1.6], [-2, -2, 1.6], [0, 0, 1])
# render.scene.scene.set_sun_light([0.707, 0.0, -.707], [1.0, 1.0, 1.0], 75000)
render.scene.scene.enable_sun_light(True)

bbox = np.array([1.48, 3.52, 1.85, 1.74, 0.231, 0.572])
# bbox = np.array([1.146, 2.198, 0.61649, 0.541, 2.534, 1.214])
center = bbox[:3]
size = bbox[3:]
# 转成min_bounds max_bounds
bbox = o3d.geometry.AxisAlignedBoundingBox(
    min_bound=np.array(center) - np.array(size) / 2,
    max_bound=np.array(center) + np.array(size) / 2
)

bbox_corners = np.asarray(bbox.get_box_points())
# 计算bbox在此视角下的投影坐标

# # Transform the bbox corners to the camera view
# camera: o3d.visualization.rendering.Camera = render.scene.camera

vis = o3d.visualization.Visualizer()
vis.create_window(visible=False, height=1080, width=1920)
# 设置摄像头参数
ctr: o3d.visualization.ViewControl = vis.get_view_control()

camera_pos = np.array([-2, -2, 1.6])
camera_lookat = np.array([1, 1.5, 1.6])
up = np.array([0, 0, 1])
front_vector = camera_pos - camera_lookat

ctr.set_up(up)
ctr.set_front(front_vector)
ctr.set_lookat(camera_lookat)
ctr.set_zoom(0.45)

# 创建一个PinholeCameraParameters对象
pinhole_camera_params = ctr.convert_to_pinhole_camera_parameters()

# 创建一个Camera对象
camera = o3d.visualization.rendering.Camera()

# 将PinholeCameraParameters的内参和外参应用到Camera对象
camera.look_at(pinhole_camera_params.extrinsic[:3, 3],  # 相机位置
               pinhole_camera_params.extrinsic[:3, 2],  # 目标点
               pinhole_camera_params.extrinsic[:3, 1])  # 上向量

# 设置Camera的投影矩阵
camera.set_projection(pinhole_camera_params.intrinsic.get_focal_length(),
                      pinhole_camera_params.intrinsic.width,
                      pinhole_camera_params.intrinsic.height,
                      pinhole_camera_params.intrinsic.get_principal_point())


view_matrix = camera.get_view_matrix()
projection_matrix = camera.get_projection_matrix()


def project_point(point, view_matrix, projection_matrix, screen_width, screen_height):
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

    print(projection_matrix)
    print(view_matrix)
    return x_screen, y_screen


projected_corners = np.array(
    [project_point(corner, view_matrix, projection_matrix, 1920, 1080) for corner in bbox_corners])
projected_corners = projected_corners.astype(int)

min_x, min_y = np.min(projected_corners, axis=0)
max_x, max_y = np.max(projected_corners, axis=0)
print(min_x, min_y, max_x, max_y)

# 读取渲染后的图像
img = render.render_to_image()
o3d.io.write_image("rendered_image.png", img, 9)
image = cv2.imread("rendered_image.png")

# 将2D BBox画在图像上
image = cv2.rectangle(image, (int(min_x), int(min_y)), (int(max_x), int(max_y)), (0, 255, 0), 2)
cv2.imwrite("rendered_image_with_bbox.png", image)

print("Saving image at final.png")

plot_image("rendered_image_with_bbox.png")
