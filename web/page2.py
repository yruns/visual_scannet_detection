"""
File: page2.py
Date: 2024/6/11
Author: yruns

Description: This file contains ...
"""
import os.path
from functools import partial

from utils.web import get_examples
from web.function import *

# Global Variables
scene_choice = get_examples()
if scene_choice:
    print(f"Found {len(scene_choice)} scenes: {scene_choice}")
else:
    raise Exception(f"No scene available! Check the path of the scene folder: {examples_path}.")
agent.original_scene_path = scene_choice[0]

# bbox_upload css 占整个页面的1/3
css = """
.bbox_upload {
    width: 30%;
}

.bbox_tabs {
    width: 70%;
}
"""


with gr.Blocks(title="Visual ScanNet's Detection", theme=theme, css=css) as demo:
    init_session_state["original_scene_path"] = scene_choice[0]
    session_state = gr.State(value=init_session_state)

    with gr.Tabs(selected=0):
        with gr.Tab("Visual Scene"):
            with gr.Column():
                with gr.Row():
                    with gr.Column(scale=5):
                        tab1_dropdown_scene = gr.Dropdown(
                            choices=[choice.split("/")[-2] for choice in scene_choice],
                            value=agent.original_scene_path.split("/")[-2],
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
                                bbox_color_picker = gr.ColorPicker(label="Bbox Color", value=bbox_color, scale=1, min_width=130)
                                checkgroup = gr.CheckboxGroup(
                                    label="Settings",
                                    choices=checkgroup_options,
                                    value=default_checkgroup_options,
                                    scale=5,
                                )
                                bbox_line_width_slider = gr.Slider(minimum=0.01, maximum=0.1,
                                                                   value=bbox_line_width, label="Bbox Line Width",
                                                                   scale=6)


                                download_button = gr.DownloadButton(label="Download Scene", scale=3,
                                                                    value=agent.original_scene_path)
                                with gr.Row():
                                    submit_button = gr.Button(value="Submit", scale=3, variant="primary")
                                    clear_button = gr.Button(value="Clear", scale=3)

                            with gr.Row():
                                with gr.Tabs(selected=0, elem_classes="bbox_tabs"):
                                    with gr.Tab("Textbox"):
                                        # bbox表格
                                        bbox_text = gr.Textbox(label="Bbox Table", lines=5, scale=5,
                                                               placeholder="bbox, eg. [ 1.48  3.52  1.85  1.74 0.231  0.572 ]")
                                        with gr.Accordion(label="Examples for Textbox:", open=False):
                                            bbox_table_example = gr.Examples(
                                                examples=[
                                                    ["[ 1.48  3.52  1.85  1.74 0.231  0.572 ]"],
                                                    ["[[ 1.14655101e+00  2.19867110e+00  6.16495669e-01  \
                                                        5.41841269e-01\n2.53463078e+00  1.21447623e+00]\n[ 2.91681337e+00\
                                                          2.50163722e+00  9.72237706e-01  6.16974354e-01\n1.84280431e+00\
                                                            2.86974430e-01]]"],
                                                ],
                                                inputs=bbox_text,
                                            )
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
                                    with gr.Tab("Add box"):
                                        box_nums = gr.Slider(minimum=1, maximum=10, value=1, step=1, label="Number of boxes you want to add")



                                with gr.Column(elem_classes="bbox_upload"):
                                    # bbox文件上传
                                    bbox_numpy_file = gr.File(label="Upload Bbox(only support .npy file)",
                                                              type="filepath",
                                                              scale=1)
                                    with gr.Accordion(label="Examples for bbox numpy file:", open=False):
                                        gr.Examples(
                                            examples=[
                                                choice.replace("vh_clean_2.obj", "aligned_bbox.npy").replace(
                                                    prettify_prefix, "")
                                                for choice in scene_choice
                                            ],
                                            inputs=bbox_numpy_file,

                                        )




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
                    download_button2 = gr.DownloadButton(label="Download Scene", scale=1)

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

    @gr.render(inputs=box_nums)
    def render_box_want_to_add(box_nums):
        items = []
        for i in range(box_nums):
            items.append([
                gr.Textbox(label=f"Box {i+1}", placeholder="bbox, eg. [ 1.48  3.52  1.85  1.74 0.231  0.572 ]"),
                gr.ColorPicker(label=f"Color {i+1}", value=bbox_color),
            ])



    # 事件绑定
    tab1_dropdown_scene.change(
        fn=select_scene,
        inputs=[session_state, tab1_dropdown_scene],
        outputs=[session_state, model_3d, download_button],
    )

    # 提交按钮
    submit_button.click(
        fn=partial(submit_bbox_params, btn_id='tab1'),
        inputs=[session_state, bbox_color_picker, bbox_line_width_slider,
                bbox_numpy_file, checkgroup, bbox_text, bbox_table],
        outputs=[session_state, model_3d, download_button],
    )

    submit_button2.click(
        fn=partial(submit_bbox_params, btn_id='tab2'),
        inputs=[session_state, bbox_color_picker2, bbox_line_width_slider2,
                bbox_numpy_file2, axis_aligned_matrix_file2, bbox_text2, bbox_table2],
        outputs=[session_state, model_display, download_button2],
    )

    # 清除按钮
    clear_button.click(
        fn=partial(clear_bbox_params, clear_btn_id="tab1"),
        inputs=[session_state,],
        outputs=[session_state, model_3d, download_button, checkgroup, bbox_color_picker, bbox_line_width_slider,
                 bbox_numpy_file, bbox_text, bbox_table],
    )

    clear_button2.click(
        fn=partial(clear_bbox_params, clear_btn_id="tab2"),
        inputs=[session_state,],
        outputs=[session_state, model_display, download_button2, checkgroup, bbox_color_picker2, bbox_line_width_slider2,
                 bbox_numpy_file2, axis_aligned_matrix_file2, bbox_text2, bbox_table2],
    )

    download_button.click(
        fn=download_scene,
        inputs=[model_3d, download_button],
        outputs=[download_button]
    )

    download_button2.click(
        fn=download_scene,
        inputs=[model_display, download_button2],
        outputs=[download_button2]
    )

    model_display.change(
        fn=upload_scene,
        inputs=[session_state, model_display],
        outputs=[session_state, model_display, download_button2],
    )
