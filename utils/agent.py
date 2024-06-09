"""
File: agent.py
Date: 2024/6/9
Author: yruns

Description: This file contains ...
"""
from utils.comm import Queue


class Agent(object):

    def __init__(self):
        self.original_scene_path = None
        self.upload_scene_path = None

        self.temp_files = Queue()
        self.current_temp_size = 0
        self.max_temp_size = 1024 * 1024 * 100  # 100MB
        self.delete_rate = 0.5

    def add_temp_file(self, file):
        self.temp_files.enqueue(file)
        self.current_temp_size += file.size

        if self.current_temp_size > self.max_temp_size:
            self.delete_temp_files()

    def delete_temp_files(self):
        delete_size = self.max_temp_size * self.delete_rate
        while self.current_temp_size > self.max_temp_size - delete_size and self.temp_files.size() > 1:
            # 确保最新的文件不会被删除
            temp_file = self.temp_files.dequeue()
            self.current_temp_size -= temp_file.size
            del temp_file

    def __del__(self):
        # 删除所有临时文件
        while self.temp_files.size() > 0:
            temp_file = self.temp_files.dequeue()
            del temp_file
