#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import json
import numpy as np

from py3dtiles_merger.NullObject import NullObject


class TilesetParser(object):
    """Parser for 3dtiles tileset.json file.

    Extract useful metadata like root.transform matrix, root.boundingVolume.box and root.geometricError metadata.

    Attributes:
        transform: 4x4 numpy matrix representing a transformation matrix between root system and its children.
        center: 4x1 numpy matrix (vector) representing the center point of the boundingVolume.
        vx: 4x1 numpy matrix (vector) representing the extend of boundingVolume.box through x-axis.
        vy: 4x1 numpy matrix (vector) representing the extend of boundingVolume.box through y-axis.
        vz: 4x1 numpy matrix (vector) representing the extend of boundingVolume.box through z-axis.
        geometricError: float representing the root item's geometric error of the tileset.
    """
    def __init__(self, tileset_path):
        with open(tileset_path, mode="r") as tileset:
            self._raw_data = json.load(tileset)
        self._split_raw_data()
        self._parse_raw_data()

    def _split_raw_data(self):
        self._raw_transform = self._raw_data["root"]["transform"]
        self._raw_boundingVolumeBox = self._raw_data["root"]["boundingVolume"]['box']
        self._raw_geometricError = self._raw_data["root"]["geometricError"]

    def _extract_rotation_matrix_only(self):
        # extract only rotation matrix
        rot_transform = self._transform.copy()
        rot_transform[:, 3] = 0
        rot_transform[3, 3] = 1
        return rot_transform

    def _parse_raw_data(self):
        # Parsed attributes
        self._transform = self._parse_transform_to_numpy_matrix()
        (self._center, self._vx, self._vy, self._vz) = self._parse_boundingVolumeBox_to_numpy_matrix()
        self._geometricError = self._parse_geometricError_to_scalar()

        # Computed attributes
        self._rotation_matrix = self._extract_rotation_matrix_only()
        self._bounds = self._compute_bounds_in_global_reference_system()

        # Public attributes
        self._expose_public_attributes()

    def _expose_public_attributes(self):
        self.bounds = self._bounds
        self.geometricError = self._geometricError

    def _parse_geometricError_to_scalar(self):
        if type(self._raw_geometricError) is list:
            if len(self._raw_geometricError) == 1:
                return float(self._raw_geometricError[0])
        return float(self._raw_geometricError)

    def _parse_transform_to_numpy_matrix(self):
        # Prepare the 4x4 transformation matrix
        matrix = [[0 for _ in range(4)] for _ in range(4)]
        # Fill matrix
        for i, value in enumerate(self._raw_transform):
            matrix[i % 4][i // 4] = value
        # Return numpy matrix
        return np.matrix(matrix)

    def _parse_boundingVolumeBox_to_numpy_matrix(self):
        # Prepare matrix
        center_matrix = [[0] for _ in range(4)]
        vx_matrix = [[0] for _ in range(4)]
        vy_matrix = [[0] for _ in range(4)]
        vz_matrix = [[0] for _ in range(4)]

        # Fill the matrix
        center_matrix[0][0] = self._raw_boundingVolumeBox[0]
        center_matrix[1][0] = self._raw_boundingVolumeBox[1]
        center_matrix[2][0] = self._raw_boundingVolumeBox[2]
        center_matrix[3][0] = 1

        vx_matrix[0][0] = self._raw_boundingVolumeBox[3]
        vx_matrix[1][0] = self._raw_boundingVolumeBox[4]
        vx_matrix[2][0] = self._raw_boundingVolumeBox[5]
        vx_matrix[3][0] = 1

        vy_matrix[0][0] = self._raw_boundingVolumeBox[6]
        vy_matrix[1][0] = self._raw_boundingVolumeBox[7]
        vy_matrix[2][0] = self._raw_boundingVolumeBox[8]
        vy_matrix[3][0] = 1

        vz_matrix[0][0] = self._raw_boundingVolumeBox[9]
        vz_matrix[1][0] = self._raw_boundingVolumeBox[10]
        vz_matrix[2][0] = self._raw_boundingVolumeBox[11]
        vz_matrix[3][0] = 1

        # return numpy matrix
        center = np.matrix(center_matrix)
        vx = np.matrix(vx_matrix)
        vy = np.matrix(vy_matrix)
        vz = np.matrix(vz_matrix)
        return center, vx, vy, vz

    def _compute_bounds_in_global_reference_system(self):
        # Change of basis
        root_tile_center = self._transform * self._center
        root_tile_vx = self._rotation_matrix * self._vx
        root_tile_vy = self._rotation_matrix * self._vy
        root_tile_vz = self._rotation_matrix * self._vz

        # Compute the 8 points of the boundingVolume.box from center and vx, vy, vz in the new base
        # right : +vx
        # left : -vx
        # top : +vy
        # bottom : -vy
        # back : +vz
        # front : -vz
        front_top_left = root_tile_center - root_tile_vx + root_tile_vy - root_tile_vz
        front_top_right = root_tile_center + root_tile_vx + root_tile_vy - root_tile_vz
        front_bottom_left = root_tile_center - root_tile_vx - root_tile_vy - root_tile_vz
        front_bottom_right = root_tile_center + root_tile_vx - root_tile_vy - root_tile_vz
        back_top_left = root_tile_center - root_tile_vx + root_tile_vy + root_tile_vz
        back_top_right = root_tile_center + root_tile_vx + root_tile_vy + root_tile_vz
        back_bottom_left = root_tile_center - root_tile_vx - root_tile_vy + root_tile_vz
        back_bottom_right = root_tile_center + root_tile_vx - root_tile_vy + root_tile_vz

        box = [front_top_left, front_top_right, front_bottom_left, front_bottom_right, back_top_left, back_top_right, back_bottom_left, back_bottom_right]

        # Detect extends
        bounds = NullObject()
        bounds.max_x = max(map(lambda x: x.item((0, 0)), box))
        bounds.min_x = min(map(lambda x: x.item((0, 0)), box))
        bounds.max_y = max(map(lambda x: x.item((1, 0)), box))
        bounds.min_y = min(map(lambda x: x.item((1, 0)), box))
        bounds.max_z = max(map(lambda x: x.item((2, 0)), box))
        bounds.min_z = min(map(lambda x: x.item((2, 0)), box))

        return bounds
