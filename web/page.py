import gradio as gr

from utils import agent
from utils.constants import background_color, bbox_color, bbox_line_width, examples_path, camera_position
from utils.web import get_examples
from web.function import select_scene, submit_bbox_params, clear_bbox_params, upload_scene

# Global Variables
scene_choice = get_examples()
if scene_choice:
    print(f"Found {len(scene_choice)} scenes: {scene_choice}")
else:
    raise Exception(f"No scene available! Check the path of the scene folder: {examples_path}.")
agent.original_scene_path = scene_choice[0]

with gr.Blocks() as demo:
    with gr.Tabs(selected=0):
        with gr.Tab("Visual Scene"):
            with gr.Column():
                with gr.Row():
                    with gr.Column(scale=5):
                        tab1_dropdown_scene = gr.Dropdown(
                            choices=[choice.split("/")[2] for choice in scene_choice],
                            value=agent.original_scene_path.split("/")[2],
                            interactive=True,
                            label="Select a scene",
                            allow_custom_value=True
                        )

                        model_3d = gr.Model3D(
                            value=agent.original_scene_path,
                            clear_color=background_color,
                            label="3D Model",
                            camera_position=camera_position,
                            zoom_speed=1,
                        )

                        # bbox选择模块
                        with gr.Column():
                            # bbox颜色选择器+线宽
                            with gr.Row():
                                # 颜色选择器
                                bbox_color_picker = gr.ColorPicker(label="Bbox Color", value=bbox_color, scale=1)
                                # bbox 线宽
                                bbox_line_width_slider = gr.Slider(minimum=0.01, maximum=0.1,
                                                                   value=bbox_line_width, label="Bbox Line Width",
                                                                   scale=4)

                            with gr.Row():
                                with gr.Tabs(selected=0):
                                    with gr.Tab("Textbox"):
                                        # bbox表格
                                        bbox_text = gr.Textbox(label="Bbox Table", lines=5, scale=5,
                                                               placeholder="bbox, eg. [ 1.48  3.52  1.85  1.74 0.231  0.572 ]")
                                    with gr.Tab("Table"):
                                        # bbox表格
                                        bbox_table = gr.Dataframe(
                                            headers=["x", "y", "z", "dx", "dy", "dz"],
                                            row_count=(1, "dynamic"),
                                            col_count=6,
                                            type="numpy",
                                            label="Bbox Table",
                                            scale=5,
                                        )

                                # bbox文件上传
                                bbox_numpy_file = gr.File(label="Upload Bbox(only support .npy file)", type="filepath",
                                                          scale=1)
                                # axis-aligned matrix上传
                                axis_aligned_matrix_file = gr.File(
                                    label="Upload Axis-Aligned Matrix(only support .txt file)", type="filepath",
                                    scale=1)

                            with gr.Row():
                                submit_button = gr.Button(value="Submit", scale=1, variant="primary")
                                clear_button = gr.Button(value="Clear", scale=1)

        with gr.Tab("Upload Scene"):
            model_display = gr.Model3D(
                camera_position=camera_position,
                # 背景设置为灰色
                clear_color=background_color,
            )

            # bbox选择模块
            with gr.Column():
                # bbox颜色选择器+线宽
                with gr.Row():
                    # 颜色选择器
                    bbox_color_picker2 = gr.ColorPicker(label="Bbox Color", value=bbox_color, scale=1)
                    # bbox 线宽
                    bbox_line_width_slider2 = gr.Slider(minimum=0.01, maximum=0.1,
                                                        value=bbox_line_width, label="Bbox Line Width", scale=4)

                with gr.Row():
                    with gr.Tabs(selected=0):
                        with gr.Tab("Textbox"):
                            # bbox表格
                            bbox_text2 = gr.Textbox(label="Bbox Table", lines=5, scale=5,
                                                    placeholder="bbox, eg. [ 1.48  3.52  1.85  1.74 0.231  0.572 ]")
                        with gr.Tab("Table"):
                            # bbox表格
                            bbox_table2 = gr.Dataframe(
                                headers=["x", "y", "z", "dx", "dy", "dz"],
                                row_count=(1, "dynamic"),
                                col_count=6,
                                type="numpy",
                                label="Bbox Table",
                                scale=5,
                            )

                    # bbox文件上传
                    bbox_numpy_file2 = gr.File(label="Upload Bbox(only support .npy file)", type="filepath", scale=1)
                    # axis-aligned matrix上传
                    axis_aligned_matrix_file2 = gr.File(label="Upload Axis-Aligned Matrix(only support .txt file)",
                                                        type="filepath", scale=1)

                with gr.Row():
                    submit_button2 = gr.Button(value="Submit", scale=1, variant="primary")
                    clear_button2 = gr.Button(value="Clear", scale=1)

    # 事件绑定
    tab1_dropdown_scene.change(
        fn=select_scene,
        inputs=[tab1_dropdown_scene],
        outputs=[model_3d],
    )

    # 提交按钮
    submit_button.click(
        fn=submit_bbox_params,
        inputs=[bbox_color_picker, bbox_line_width_slider,
                bbox_numpy_file, axis_aligned_matrix_file, bbox_text, bbox_table],
        outputs=[model_3d],
    )

    submit_button2.click(
        fn=submit_bbox_params,
        inputs=[bbox_color_picker2, bbox_line_width_slider2,
                bbox_numpy_file2, axis_aligned_matrix_file2, bbox_text2, bbox_table2],
        outputs=[model_display],
    )

    # 清除按钮
    clear_button.click(
        fn=clear_bbox_params,
        inputs=[model_3d],
        outputs=[model_3d, bbox_color_picker, bbox_line_width_slider,
                 bbox_numpy_file, axis_aligned_matrix_file, bbox_text, bbox_table],
    )

    clear_button2.click(
        fn=clear_bbox_params,
        inputs=[model_display],
        outputs=[model_display, bbox_color_picker2, bbox_line_width_slider2,
                 bbox_numpy_file2, axis_aligned_matrix_file2, bbox_text2, bbox_table2],
    )

    model_display.change(
        fn=upload_scene,
        inputs=[model_display],
        outputs=[model_display],
    )
