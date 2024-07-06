"""
File: picture_taker.py
Date: 2024/7/6
Author: yruns

Description: This file contains ...
"""
import gradio as gr
from functools import partial

from utils import logger, agent
from utils import constants as const
from web import function as bind_func


def create_tab(session_state, scene_choice):

    with gr.Tab("Picture Taker") as tab:
        picture_taker_model = gr.Model3D(
            value='data/example/scene0000_00/prettify_scene0000_00_vh_clean_2.obj',
            clear_color=const.background_color,
            label="Picture Taker",
            camera_position=const.camera_position,
            zoom_speed=1,
        )
        # with gr.Column(scale=5):
        #     tab2_dropdown_scene = gr.Dropdown(
        #         choices=[choice.split("/")[-2] for choice in scene_choice],
        #         value=agent.original_scene_path.split("/")[-2],
        #         interactive=True,
        #         label="Select a scene",
        #         allow_custom_value=True
        #     )
        #
        #
        #
        #
        #     download_button2 = gr.DownloadButton(label="Download Scene", scale=1, value=agent.original_scene_path)
        #
        #
        # tab2_dropdown_scene.change(
        #     fn=partial(bind_func.select_scene, tab="picture_taker"),
        #     inputs=[session_state, tab2_dropdown_scene],
        #     outputs=[session_state, picture_taker_model, download_button2],
        # )

    return tab
