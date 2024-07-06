import open3d as o3d
from open3d.visualization import rendering

render = rendering.OffscreenRenderer(800, 480)


grey = rendering.MaterialRecord()
grey.base_color = [0.9, 0.9, 0.9, 1.0]
grey.shader = "defaultLit"

# 读取 PLY 文件
mesh = o3d.io.read_triangle_mesh("../resources/scans/scene0000_00.ply")
mesh.compute_vertex_normals()

render.scene.add_geometry("mesh", mesh, grey)
render.setup_camera(70.0, [3, 3, 1.6], [6, 6, 1.6], [0, 0, 1])
render.scene.scene.set_sun_light([0.707, 0.0, -.707], [1.0, 1.0, 1.0], 75000)
render.scene.scene.enable_sun_light(True)
# render.scene.show_axes(True)

img = render.render_to_image()
o3d.io.write_image("images/final.png", img, 9)

# 显示img
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 5))
# 不显示横纵坐标
plt.axis('off')
# 显示图片
plt.imshow(img)
plt.show()
#
# render.setup_camera(60.0, [0, 0, 0], [-10, 0, 0], [0, 0, 1])
# img = render.render_to_image()
# print("Saving image at test2.png")
# o3d.io.write_image("images/test2.png", img, 9)
# plt.imshow(img)
# plt.show()