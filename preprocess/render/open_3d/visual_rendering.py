import open3d as o3d
from open3d.visualization import rendering
import numpy as np


# 读取 PLY 文件
mesh = o3d.io.read_triangle_mesh("../scene0000_00_vh_clean_2.ply")
mesh.compute_vertex_normals()

vis = o3d.visualization.Visualizer()
vis.create_window(visible=True, height=1024, width=1024)
vis.add_geometry(mesh)

# 设置摄像头参数
ctr = vis.get_view_control()
ctr.set_up([0, 0, 1])
ctr.set_front([6, 6, 1.6])
ctr.set_lookat([3, 3, 1.6])
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
# vis.destroy_window()

# 将图像保存为文件
# o3d.io.write_image("rendered_image.png", image)
#
# # 显示img
# import matplotlib.pyplot as plt
# plt.figure(figsize=(8, 5))
# # 不显示横纵坐标
# plt.axis('off')
# # 显示图片
# plt.imshow(image)
# plt.show()
