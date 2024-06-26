"""
File: prepare_scannet.py
Date: 2024/6/10
Author: yruns

Description: This file contains ...
"""

# !/usr/bin/env python
# encoding: utf-8
'''
@author: Xu Yan
@file: prepare_data.py
@time: 2020/10/14 14:28
'''

import argparse
import datetime
import os
import os.path as osp

import numpy as np
import pandas as pd
from multiprocessing import Pool

import scannet_utils
from load_scannet_data import read_aggregation, read_segmentation

SCAN_NAMES = sorted([line.rstrip() for line in open('meta_data/scannetv2_train.txt')])
LABEL_MAP_FILE = 'meta_data/scannetv2-labels.combined.tsv'
DONOTCARE_CLASS_IDS = np.array([])
OBJ_CLASS_IDS = np.array(
    [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
     34, 35, 36, 37, 38, 39, 40])  # exclude wall (1), floor (2), ceiling (22)
MAX_NUM_POINT = -1


def parse_args():
    parser = argparse.ArgumentParser('Data Preparision')
    parser.add_argument('--multi_thread', action='store_true')
    parser.add_argument('--split', type=str, default='train', choices=['train', 'val', 'test'])
    parser.add_argument('--scannet_path', type=str, default='/data3/ysh/Datasets/ScanNet/scans/')
    parser.add_argument('--pointgroupinst_path', type=str,
                        default='/data2/shyue/ysh/paper-code/lang-point/ZSVG3D/data/scanrefer/PointGroupInst/')
    parser.add_argument('--output_path', type=str,
                        default='/data2/shyue/ysh/paper-code/lang-point/ZSVG3D/data/scanrefer/pointgroup_data')

    return parser.parse_args()


def export(mesh_file, agg_file, seg_file, meta_file, label_map_file, pointgroup_file=None):
    scene = meta_file.split('/')[-1].split('.')[0]

    label_map = scannet_utils.read_label_mapping(label_map_file, label_from='raw_category', label_to='nyu40id')
    mesh_vertices = scannet_utils.read_mesh_vertices_rgb_normal(mesh_file)

    # Load scene axis alignment matrix
    axis_align_matrix = scannet_utils.read_axis_align_matrix(meta_file)
    if axis_align_matrix is not None:
        aligned_vertices = scannet_utils.axis_align_point_cloud(mesh_vertices, axis_align_matrix)
    else:
        print("No axis alignment matrix found")
        aligned_vertices = mesh_vertices

    # Load semantic and instance labels
    object_id_to_segs, label_to_segs = read_aggregation(agg_file)
    seg_to_verts, num_verts = read_segmentation(seg_file)

    label_ids = np.zeros(shape=num_verts, dtype=np.uint32)  # 0: unannotated
    object_id_to_label_id = {}
    for label, segs in label_to_segs.items():
        label_id = label_map[label]
        for seg in segs:
            verts = seg_to_verts[seg]
            label_ids[verts] = label_id
    instance_ids = np.zeros(shape=num_verts, dtype=np.uint32)  # 0: unannotated
    num_instances = len(np.unique(list(object_id_to_segs.keys())))
    for object_id, segs in object_id_to_segs.items():
        for seg in segs:
            verts = seg_to_verts[seg]
            instance_ids[verts] = object_id
            if object_id not in object_id_to_label_id:
                object_id_to_label_id[object_id] = label_ids[verts][0]

    instance_bboxes = np.zeros((num_instances, 8))  # also include object id
    aligned_instance_bboxes = np.zeros((num_instances, 8))  # also include object id
    for obj_id in object_id_to_segs:
        label_id = object_id_to_label_id[obj_id]

        # bboxes in the original meshes
        obj_pc = mesh_vertices[instance_ids == obj_id, 0:3]
        if len(obj_pc) == 0: continue
        bbox = scannet_utils.compute_bbox(obj_pc)
        # concatenate label id and instance id
        bbox = np.concatenate((bbox, [label_id, obj_id - 1]))
        # NOTE: this assumes obj_id is in 1,2,3,.,,,.NUM_INSTANCES
        instance_bboxes[obj_id - 1, :] = bbox

        # bboxes in the aligned meshes
        obj_pc = aligned_vertices[instance_ids == obj_id, 0:3]
        if len(obj_pc) == 0: continue
        bbox = scannet_utils.compute_bbox(obj_pc)
        # concatenate label id and instance id
        bbox = np.concatenate((bbox, [label_id, obj_id - 1]))
        # NOTE: this assumes obj_id is in 1,2,3,.,,,.NUM_INSTANCES
        aligned_instance_bboxes[obj_id - 1, :] = bbox

    return_values = [mesh_vertices, aligned_vertices, label_ids, instance_ids, instance_bboxes, aligned_instance_bboxes]

    if pointgroup_file is not None:
        pointgroup_folder = osp.join(pointgroup_file, split)
        pointgroup_instance = pd.read_table(pointgroup_folder + "/" + scene + '.txt', header=None)

        label_ids_pg = np.zeros(shape=num_verts, dtype=np.uint32)
        instance_ids_pg = np.zeros(shape=num_verts, dtype=np.uint32)  # 0: unannotated
        aligned_instance_bboxes_pg = np.zeros((len(pointgroup_instance[0]), 8))

        for inst_id, inst_pg in enumerate(pointgroup_instance[0]):
            txt_path, cls, _ = inst_pg.split(' ')
            if int(cls) not in OBJ_CLASS_IDS:
                raise ValueError(f"Skipping object with label {cls}")
            inst_pred = np.loadtxt(os.path.join(str(pointgroup_folder), txt_path))
            instance_ids_pg[inst_pred != 0] = inst_id + 1
            label_ids_pg[inst_pred != 0] = cls

            # bboxes in the aligned meshes
            obj_pc = aligned_vertices[inst_pred != 0, 0:3]
            if len(obj_pc) == 0: continue
            bbox = scannet_utils.compute_bbox(obj_pc)
            # concatenate label id and instance id
            bbox = np.concatenate((bbox, [cls, inst_id - 1]))
            aligned_instance_bboxes_pg[inst_id - 1, :] = bbox

        return_values.extend([label_ids_pg, instance_ids_pg, aligned_instance_bboxes_pg])

    return return_values


def export_one_scan(scan_name):
    output_filename_prefix = str(os.path.join(OUTPUT_FOLDER, scan_name))
    mesh_file = os.path.join(SCANNET_DIR, scan_name, scan_name + '_vh_clean_2.ply')
    agg_file = os.path.join(SCANNET_DIR, scan_name,
                            scan_name + '.aggregation.json')  # NOTE must use the aggregation file for the low-res mesh
    seg_file = os.path.join(SCANNET_DIR, scan_name, scan_name + '_vh_clean_2.0.010000.segs.json')

    meta_file = os.path.join(SCANNET_DIR, scan_name,
                             scan_name + '.txt')  # includes axisAlignment info for the train set scans.

    mesh_vertices, aligned_vertices, semantic_labels, instance_labels, instance_bboxes, \
        aligned_instance_bboxes, semantic_labels_pg, instance_labels_pg, aligned_instance_bboxes_pg = (
            export(mesh_file, agg_file, seg_file, meta_file, LABEL_MAP_FILE, POINTGROUP_DIR))

    mask = np.logical_not(np.in1d(semantic_labels, DONOTCARE_CLASS_IDS))
    mesh_vertices = mesh_vertices[mask, :]
    aligned_vertices = aligned_vertices[mask, :]
    semantic_labels = semantic_labels[mask]
    instance_labels = instance_labels[mask]

    if instance_bboxes.shape[0] > 1:
        num_instances = len(np.unique(instance_labels))
        print('Num of instances: ', num_instances)

        # bbox_mask = np.in1d(instance_bboxes[:,-1], OBJ_CLASS_IDS)
        bbox_mask = np.in1d(instance_bboxes[:, -2], OBJ_CLASS_IDS)  # match the mesh cap
        instance_bboxes = instance_bboxes[bbox_mask, :]
        aligned_instance_bboxes = aligned_instance_bboxes[bbox_mask, :]
        print('Num of care instances: ', instance_bboxes.shape[0])
    else:
        print("No semantic/instance annotation for test scenes")

    N = mesh_vertices.shape[0]
    if N > MAX_NUM_POINT != -1:
        choices = np.random.choice(N, MAX_NUM_POINT, replace=False)
        mesh_vertices = mesh_vertices[choices, :]
        aligned_vertices = aligned_vertices[choices, :]
        semantic_labels = semantic_labels[choices]
        instance_labels = instance_labels[choices]

    print("Shape of points: {}".format(mesh_vertices.shape))
    np.save(output_filename_prefix + '_vert.npy', mesh_vertices)
    np.save(output_filename_prefix + '_aligned_vert.npy', aligned_vertices)
    np.save(output_filename_prefix + '_sem_label.npy', semantic_labels)
    np.save(output_filename_prefix + '_ins_label.npy', instance_labels)
    np.save(output_filename_prefix + '_sem_label_pg.npy', semantic_labels_pg)
    np.save(output_filename_prefix + '_ins_label_pg.npy', instance_labels_pg)
    np.save(output_filename_prefix + '_bbox.npy', instance_bboxes)
    np.save(output_filename_prefix + '_aligned_bbox.npy', aligned_instance_bboxes)
    np.save(output_filename_prefix + '_aligned_bbox_pg.npy', aligned_instance_bboxes_pg)


def batch_export(multi_thread):
    if not os.path.exists(OUTPUT_FOLDER):
        print('Creating new data folder: {}'.format(OUTPUT_FOLDER))
        os.mkdir(OUTPUT_FOLDER)


    if multi_thread:
        with Pool() as pool:
            pool.map(export_one_scan, SCAN_NAMES)

    else:
        for scan_name in SCAN_NAMES:
            print(scan_name)
            print('-' * 20 + 'begin')
            print(datetime.datetime.now())
            print(scan_name)
            export_one_scan(scan_name)
            print('-' * 20 + 'done')


if __name__ == '__main__':
    args = parse_args()
    split = args.split
    SCANNET_DIR = args.scannet_path
    POINTGROUP_DIR = args.pointgroupinst_path
    OUTPUT_FOLDER = args.output_path

    SCAN_NAMES = sorted([line.rstrip() for line in open('meta_data/scannetv2_%s.txt' % split)])
    batch_export(multi_thread=args.multi_thread)
