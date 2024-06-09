import os

# Tab1 example 文件夹路径
examples_path = "data/example"
os.makedirs(examples_path, exist_ok=True)

# 临时文件夹路径
temp_path = "data/temp"
os.makedirs(temp_path, exist_ok=True)

# gr.Model3D背景颜色
background_color = (0.95, 0.95, 0.95, 1.0)

# gr.Model3D默认相机位置
camera_position = (-50, 65, 70)

# 默认bbox颜色
bbox_color = "#6BC84A"

# 默认bbox线宽
bbox_line_width = 0.04

prettify_prefix = "prettify_"
