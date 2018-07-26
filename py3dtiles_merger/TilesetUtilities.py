#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import numpy as np


class TilesetUtilities(object):
    def __init__(self):
        pass

    @classmethod
    def export_bounds_to_3dtiles_volumeBoundBox(cls, bounds):
        (_center, _vx, _vy, _vz) = cls._volumeBoundBox_creator_from_bounds(bounds)
        _stacked_volumeBoundBox = cls._stack_vectors_to_volumeBoundBox(_center, _vx, _vy, _vz)
        _3dtiles_bounds = cls._flatten_stacked_volumeBoundBox(_stacked_volumeBoundBox)
        return _3dtiles_bounds

    @classmethod
    def _volumeBoundBox_creator_from_bounds(cls, bounds):
        half_length_x_axis = (bounds.max_x - bounds.min_x) / 2
        half_length_y_axis = (bounds.max_y - bounds.min_y) / 2
        half_length_z_axis = (bounds.max_z - bounds.min_z) / 2

        vx = np.matrix([[half_length_x_axis], [0], [0], [1]])
        vy = np.matrix([[0], [half_length_y_axis], [0], [1]])
        vz = np.matrix([[0], [0], [half_length_z_axis], [1]])

        center = np.matrix([[bounds.min_x + half_length_x_axis], [bounds.min_y + half_length_y_axis], [bounds.min_z + half_length_z_axis], [1]])

        return (center, vx, vy, vz)

    @classmethod
    def _stack_vectors_to_volumeBoundBox(cls, center, vx, vy, vz):
        return np.vstack((center[:3], vx[:3], vy[:3], vz[:3]))

    @classmethod
    def _flatten_stacked_volumeBoundBox(cls, stacked_volumeBoundBox):
        json_list = stacked_volumeBoundBox.flatten('F').tolist()
        if (type(json_list[0]) is list):
            return json_list[0]
        return json_list
