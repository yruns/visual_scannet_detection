import os
import shutil

import numpy as np

from utils import agent
from utils.comm import TempFile
from utils.comm import process_2d_text_table
from utils.constants import *
from utils.convertor import convert_hex_to_rgb, ply_to_obj
from utils.visual import create_scene_with_bbox


def select_scene(scene_name):
    print("Selected scene:", scene_name)
    scene_name = os.path.join(examples_path, scene_name, f"{scene_name}_vh_clean_2.obj")
    agent.original_scene_path = scene_name

    return (
        scene_name
    )


def upload_scene(scene_file):
    prettify_file = None
    if scene_file is not None and os.path.exists(scene_file):
        # 确保上传文件时才触发，删除文件时忽略
        shutil.move(scene_file, temp_path)
        scene_file = os.path.join(temp_path, os.path.basename(scene_file))
        print("Uploaded scene file:", scene_file)
        agent.add_temp_file(TempFile(scene_file))

        if scene_file.endswith('.ply'):
            scene_file, prettify_file = ply_to_obj(scene_file, prettify_gradio=True)
            agent.add_temp_file(TempFile(scene_file))
            agent.add_temp_file(TempFile(prettify_file))

    return (
        prettify_file if prettify_file is not None else scene_file
    )


def change_bbox_line_width(current_scene_path, bbox_line_width):
    print("Change bbox line width to:", bbox_line_width)

    return (
        current_scene_path
    )


def upload_bbox_file(current_scene_path, bbox_file):
    print("Uploaded bbox file:", bbox_file)

    return (
        current_scene_path
    )


def submit_bbox_params(bbox_color, bbox_line_width,
                       bbox_numpy_file, axis_aligned_matrix_file, bbox_text, bbox_table):
    # 读取bbox_numpy_file（binary）文件
    bbox_numpy, axis_align_matrix = None, None
    if bbox_numpy_file is not None:
        bbox_numpy = np.load(bbox_numpy_file)[:, :6]
        agent.add_temp_file(TempFile(bbox_numpy_file))
    if axis_aligned_matrix_file is not None:
        lines = open(axis_aligned_matrix_file).readlines()
        for line in lines:
            if 'axisAlignment' in line:
                axis_align_matrix = [float(x) for x in line.rstrip().strip('axisAlignment = ').split(' ')]
                axis_align_matrix = np.array(axis_align_matrix).reshape((4, 4))
        agent.add_temp_file(TempFile(axis_aligned_matrix_file))

    try:
        bbox_params = bbox_table.astype(np.float32)[:, :6]
    except ValueError:
        print(f"bbox_table is not valid, ignore it.")
        print(bbox_table)
        bbox_params = None

    if bbox_params is not None:
        bbox_numpy = np.concatenate([bbox_numpy, bbox_params], axis=0) if bbox_numpy is not None else bbox_params

    # 处理bbox_text
    try:
        if bbox_text.count("[") == 1:
            # 一维转二维
            bbox_text = "[" + bbox_text + "]"
        bbox_params = process_2d_text_table(bbox_text)[:, :6]
    except ValueError:
        print(f"bbox_text is not valid, ignore it.")
        print(bbox_table)
        bbox_params = None

    if bbox_params is not None:
        bbox_numpy = np.concatenate([bbox_numpy, bbox_params], axis=0) if bbox_numpy is not None else bbox_params

    new_scene_path = create_scene_with_bbox(
        agent.original_scene_path,
        bbox_numpy,
        axis_align_matrix,
        convert_hex_to_rgb(bbox_color, normalize=True),
        bbox_line_width
    )

    return (
        new_scene_path
    )


def clear_bbox_params(model_3d_path):
    # 将所有参数重置为默认值, 并返回原始场景路径
    return (
        agent.original_scene_path if model_3d_path.startswith(examples_path) else model_3d_path,
        bbox_color,
        bbox_line_width,
        None,
        None,
        None,
        None
    )
