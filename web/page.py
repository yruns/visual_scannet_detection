import os.path

from utils.web import get_examples
from web.function import *

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
                                download_button = gr.DownloadButton(label="Download Scene", scale=1,
                                                                    value=agent.original_scene_path)

                            with gr.Row():
                                with gr.Tabs(selected=0):
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
                                with gr.Column():
                                    # bbox文件上传
                                    bbox_numpy_file = gr.File(label="Upload Bbox(only support .npy file)", type="filepath",
                                                              scale=1)
                                    with gr.Accordion(label="Examples for bbox numpy file:", open=False):
                                        gr.Examples(
                                            examples=[
                                                choice.replace("vh_clean_2.obj", "aligned_bbox.npy").replace(prettify_prefix, "")
                                                for choice in scene_choice
                                            ],
                                            inputs=bbox_numpy_file,
                                        )
                                with gr.Column():
                                    # axis-aligned matrix上传
                                    axis_aligned_matrix_file = gr.File(
                                        label="Upload Axis-Aligned Matrix(only support .txt file)", type="filepath",
                                        scale=1)
                                    with gr.Accordion(label="Examples for axis align matrix:", open=False):
                                        gr.Examples(
                                            examples=[
                                                choice.replace("_vh_clean_2.obj", ".txt").replace(
                                                    prettify_prefix, "")
                                                for choice in scene_choice
                                            ],
                                            inputs=axis_aligned_matrix_file,
                                        )

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

    # 事件绑定
    tab1_dropdown_scene.change(
        fn=select_scene,
        inputs=[tab1_dropdown_scene],
        outputs=[model_3d, download_button],
    )

    # 提交按钮
    submit_button.click(
        fn=submit_bbox_params,
        inputs=[bbox_color_picker, bbox_line_width_slider,
                bbox_numpy_file, axis_aligned_matrix_file, bbox_text, bbox_table],
        outputs=[model_3d, download_button],
    )

    submit_button2.click(
        fn=submit_bbox_params,
        inputs=[bbox_color_picker2, bbox_line_width_slider2,
                bbox_numpy_file2, axis_aligned_matrix_file2, bbox_text2, bbox_table2],
        outputs=[model_display, download_button2],
    )

    # 清除按钮
    clear_button.click(
        fn=clear_bbox_params_btn_tab1,
        inputs=[],
        outputs=[model_3d, download_button, bbox_color_picker, bbox_line_width_slider,
                 bbox_numpy_file, axis_aligned_matrix_file, bbox_text, bbox_table],
    )

    clear_button2.click(
        fn=clear_bbox_params_btn_tab2,
        inputs=[],
        outputs=[model_display, download_button2, bbox_color_picker2, bbox_line_width_slider2,
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
        inputs=[model_display],
        outputs=[model_display, download_button2],
    )
