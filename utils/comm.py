"""
File: comm.py
Date: 2024/6/9
Author: yruns

Description: This file contains ...
"""

import hashlib
import os
import platform
import pickle
import time
from collections import deque
from enum import Enum

import numpy as np


class Queue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if len(self.queue) < 1:
            return None
        return self.queue.popleft()

    def size(self):
        return len(self.queue)


class TempFile(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.timestamp = time.time()
        self.size = os.path.getsize(file_path)

    def __del__(self):
        if os.path.exists(self.file_path):
            print(f"Removing temp file: {self.file_path}")
            os.remove(self.file_path)

class OsType(Enum):
    Linux = "Linux"
    MacOS = "Darwin"
    Other = "Other"


def get_system_type():
    system = platform.system()
    if system == "Linux":
        return OsType.Linux
    elif system == "Darwin":
        return OsType.MacOS
    else:
        return OsType.Other


def generate_hash(*args):
    # 将数据组合成一个字符串
    data_str = pickle.dumps(args)

    # 使用 SHA-256 哈希算法计算哈希值
    hash_object = hashlib.sha256(data_str)

    # 返回哈希值的十六进制表示
    return hash_object.hexdigest()

def process_text_indices(bbox_indices: str):
    if bbox_indices.isnumeric():
        return [int(bbox_indices)]
    elif bbox_indices.startswith("[") and bbox_indices.endswith("]"):
        bbox_indices = bbox_indices.strip("[]")
        if "," in bbox_indices:
            return [int(i) for i in bbox_indices.split(",")]
        else:
            return [int(i) for i in bbox_indices.split()]
    else:
        return []


def process_2d_text_table(printed_array):
    if printed_array.count("[") == 1:
        # 一维转二维
        printed_array = "[" + printed_array + "]"
    # 将文本表格处理成列表
    # 用字符串处理函数将其转换为合适的形式
    array_str = printed_array.replace('[', '').replace(']', '').replace('\n', ' ').replace(',', ' ')
    array_str = array_str.split()

    # 使用numpy.fromstring()创建NumPy数组
    numpy_array = np.fromstring(' '.join(array_str), sep=' ')

    # 调整数组形状以匹配原始数组
    num_rows = printed_array.count("[") - 1
    numpy_array = numpy_array.reshape(num_rows, -1)

    return numpy_array.astype(np.float32)


def has_prefix(text, prefix):
    basename = os.path.basename(text)
    return basename.startswith(prefix)


def add_prefix(text, prefix):
    dirname = os.path.dirname(text)
    basename = os.path.basename(text)
    return os.path.join(dirname, f"{prefix}{basename}")


def remove_prefix(text, prefix):
    dirname = os.path.dirname(text)
    basename = os.path.basename(text)
    return os.path.join(dirname, basename[len(prefix):])
