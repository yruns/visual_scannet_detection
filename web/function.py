import shutil
import os

import numpy as np
import gradio as gr

from utils import agent, logger
from utils.comm import TempFile, process_2d_text_table
from utils import constants as const
from utils.convertor import convert_hex_to_rgb, ply_to_obj
from utils.visual import create_scene_with_bbox
from utils import scannet as scannet_utils


def select_scene(session_state, scene_name):
    logger.info("Selected scene:", scene_name)
    scene_name = os.path.join(const.examples_path, scene_name, f"{const.prettify_prefix}{scene_name}_vh_clean_2.obj")
    session_state[const.original_scene_path] = scene_name

    return (
        session_state, scene_name, scene_name
    )


def upload_scene(session_state, scene_file):
    prettify_file = None
    if scene_file is not None and os.path.exists(scene_file):
        # 确保上传文件时才触发，删除文件时忽略
        if os.path.exists(os.path.join(const.temp_path, os.path.basename(scene_file))):
            os.remove(os.path.join(const.temp_path, os.path.basename(scene_file)))
        shutil.move(scene_file, const.temp_path)
        scene_file = os.path.join(const.temp_path, os.path.basename(scene_file))
        logger.info("Uploaded scene file:", scene_file)
        agent.add_temp_file(TempFile(scene_file))

        if scene_file.endswith('.ply'):
            scene_file, prettify_file = ply_to_obj(scene_file, prettify_gradio=True)
            agent.add_temp_file(TempFile(scene_file))
            agent.add_temp_file(TempFile(prettify_file))

    session_state[const.upload_scene_path] = prettify_file if prettify_file is not None else scene_file
    return (
        session_state,
        session_state[const.upload_scene_path],
        session_state[const.upload_scene_path],
    )

def download_scene(current_scene_path, download_btn):
    if download_btn is None:
        gr.Warning("Now there is no scene to download.")
    logger.info("Downloaded scene file:", current_scene_path)
    return (
        current_scene_path
    )

def submit_add_box(session_state, *bbox_params):
    if len(bbox_params) % 3 != 0:
        gr.Warning("The number of parameters is not correct, ignore it.")
        return (
            session_state
        )
    session_state[const.add_bbox_params] = []
    for i in range(len(bbox_params) // 3):
        bbox_param = {
            "color": bbox_params[int(i * 3)],
            "array_str": bbox_params[int(i * 3 + 1)],
            "show": bbox_params[int(i * 3 + 2)]
        }
        session_state[const.add_bbox_params].append(bbox_param)

    return (
        session_state
    )

def clear_add_box(session_state, *bbox_params):
    session_state[const.add_bbox_params] = None
    if len(bbox_params) % 3 != 0:
        gr.Warning("The number of parameters is not correct, ignore it.")
        return (
            session_state
        )

    bbox_params_return = []
    for i in range(len(bbox_params) // 3):
        bbox_params_return.append(const.standby_bbox_color[i])
        bbox_params_return.append("")
        bbox_params_return.append(True)

    return (
        session_state,
        *bbox_params_return
    )

def submit_bbox_params(session_state, bbox_color, bbox_line_width, bbox_numpy_file, checkgroup,
                       bbox_text, camera_pos, camera_lookat, render_checkgroup, btn_id):
    # 读取bbox_numpy_file文件
    bbox_numpy, axis_align_matrix = None, None
    if bbox_numpy_file is not None:
        bbox_numpy = np.load(bbox_numpy_file)[:, :6]
        agent.add_temp_file(TempFile(bbox_numpy_file))

    if const.axis_aligned_option in checkgroup:
        meta_file = session_state[const.original_scene_path].replace(const.prettify_prefix, "").replace("_vh_clean_2.obj", ".txt")
        if os.path.exists(meta_file):
            axis_align_matrix = scannet_utils.read_axis_align_matrix(meta_file)
        else:
            gr.Warning("A meta file is not found for the scene {}".format(session_state[const.original_scene_path].split("/")[-2]))

    # 处理Picture Taker
    try:
        camera_pos = process_2d_text_table(camera_pos)[0]
        assert camera_pos.shape == (3,), "camera_pos.shape = {}".format(camera_pos.shape)
        camera_lookat = process_2d_text_table(camera_lookat)[0]
        assert camera_lookat.shape == (3,), "camera_lookat.shape = {}".format(camera_lookat.shape)
    except Exception:
        logger.info(f"camera_pos or camera_lookat is not valid, ignore it.\n" + camera_pos + "\n" + camera_lookat)
        if not (camera_pos == "" and camera_lookat == ""):
            gr.Warning('Camera position or camera lookat is not valid, ignore it.')

    # 处理bbox_text
    try:
        bbox_params = process_2d_text_table(bbox_text)[:, :6]
        assert bbox_params.shape[1] >= 6
    except Exception:
        logger.info(f"bbox_text is not valid, ignore it.\n" + bbox_text)
        if bbox_text != "":
            gr.Warning('Textbox is not valid, ignore it.')
        bbox_params = None

    if bbox_params is not None:
        bbox_numpy = np.concatenate([bbox_numpy, bbox_params], axis=0) if bbox_numpy is not None else bbox_params

    bboxes = []
    if bbox_numpy is not None:
        bboxes.append({
            "color": convert_hex_to_rgb(bbox_color, normalize=True),
            "bbox_params": bbox_numpy,
        })

    # 处理add_bbox_params
    extra_bbox_params = session_state[const.add_bbox_params]
    if extra_bbox_params is not None:
        for bbox in extra_bbox_params:
            if bbox["show"]:
                try:
                    bbox_params = process_2d_text_table(bbox["array_str"])[:, :6]
                    assert bbox_params.shape[1] >= 6
                    bboxes.append({
                        "color": convert_hex_to_rgb(bbox["color"], normalize=True),
                        "bbox_params": bbox_params,
                    })
                except Exception:
                    logger.info(f"add bbox is not valid, ignore it.\n" + bbox["array_str"])
                    continue

    new_scene_path, projcetion_path = create_scene_with_bbox(
        session_state[const.original_scene_path] if btn_id == 'tab1' else session_state[const.upload_scene_path],
        bboxes,
        axis_align_matrix,
        const.show_axis_option in checkgroup,
        bbox_line_width,
        camera_lookat if isinstance(camera_lookat, np.ndarray) else None,
        camera_pos if isinstance(camera_pos, np.ndarray) else None,
        render_checkgroup
    )

    return (
        session_state, new_scene_path, new_scene_path, projcetion_path
    )


def clear_bbox_params(session_state, clear_btn_id):
    # 将所有参数重置为默认值, 并返回原始场景路径
    return (
        session_state,
        session_state[const.original_scene_path] if clear_btn_id == 'tab1' else session_state[const.upload_scene_path],
        session_state[const.original_scene_path] if clear_btn_id == 'tab1' else session_state[const.upload_scene_path],
        const.default_checkgroup_options,
        const.bbox_color,
        const.bbox_line_width,
        None,
        None,
        None,
        None,
        None,
        const.default_render_checkgroup_options
    )
