import os
import gradio

# Gradio主题
theme = gradio.themes.Soft()

# 初始init_session_state
original_scene_path = "original_scene_path"
upload_scene_path = "upload_scene_path"
add_bbox_params = "add_bbox_params"

init_session_state = {
    original_scene_path: None,
    upload_scene_path: None,
    add_bbox_params: None
}

# Tab1 example 文件夹路径
examples_path = "data/example"
os.makedirs(examples_path, exist_ok=True)

# 临时文件夹路径
temp_path = "data/temp"
os.makedirs(temp_path, exist_ok=True)

# Tab1 checkgroup选项
axis_aligned_option = "Axis-Aligned"
show_axis_option = "Show Axis"
checkgroup_options = [axis_aligned_option, show_axis_option]
default_checkgroup_options = [axis_aligned_option]

# gr.Model3D背景颜色
background_color = (0.95, 0.95, 0.95, 1.0)

# gr.Model3D默认相机位置
camera_position = (-50, 65, 70)

# 默认bbox颜色
bbox_color = "#5CE6D5"   # "#6BC84A"
# 备用bbox_color
standby_bbox_color = ["#F12C1E", "#48E845", "#9372EE"]

# 默认bbox线宽
bbox_line_width = 0.03

# 渲染投影默认背景颜色及其尺寸
camera_model_path = "resources/camera.ply"
render_projection_background_color = [0.95, 0.95, 0.95, 1]  # 在MacOS平台上，透明度1不生效
render_projection_size = (1920, 1080)

scene_only_option = "Scene-Only"
sharp_option = "Sharp"
precise_option = "Precise"
render_checkgroup_options = ["Scene-Only", "Sharp", "Precise"]
default_render_checkgroup_options = ["Scene-Only"]

# prettify前缀
prettify_prefix = "prettify_"
