import glob
import os

from utils import constants as const
from utils.convertor import ply_to_obj


def get_examples():
    """
    Find all example scenes in the const.examples_path directory.
    If the scene has an `.obj` file, return the path to the `.obj` file.
    If the scene has a `.ply` file, convert it to .obj and return the path to the `.obj` file.
    """
    examples = []

    for example_dir in sorted(glob.glob(os.path.join(const.examples_path, "scene*"))):
        scene_name = os.path.basename(example_dir)
        obj_file = os.path.join(example_dir, f"{const.prettify_prefix}{scene_name}_vh_clean_2.obj")
        if os.path.exists(obj_file):
            examples.append(obj_file)
        else:
            ply_file = os.path.join(example_dir, f"{scene_name}_vh_clean_2.ply")
            try:
                obj_file, prettify_file = ply_to_obj(ply_file, prettify_gradio=True)
                print(f"Converted {ply_file} to {prettify_file}")
                examples.append(prettify_file)
            except ValueError as e:
                os.remove(ply_file)
                print(f"Error converting {ply_file} to .obj: {e}, Removed {ply_file}!")

    return examples
