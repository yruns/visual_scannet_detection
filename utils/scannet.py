"""
File: scannet.py
Date: 2024/6/9
Author: yruns

Description: This file contains ...
"""
import numpy as np


def align_point_vertices(mesh_vertices, axis_align_matrix):
    """
    Align the vertices of a mesh using the given axis align matrix.
    """
    pts = np.ones((mesh_vertices.shape[0], 4))
    pts[:, 0:3] = mesh_vertices[:, 0:3]
    pts = np.dot(pts, axis_align_matrix.transpose())  # Nx4
    aligned_vertices = np.copy(mesh_vertices)
    aligned_vertices[:, 0:3] = pts[:, 0:3]
    return aligned_vertices
