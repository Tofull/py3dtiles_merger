#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import json
import os

from py3dtiles_merger.TilesetUtilities import TilesetUtilities


class TilesetMerger(object):
    union_bounds = None
    children = []
    geometricError_sum = 0

    def __init__(self):
        pass

    @classmethod
    def append_child(cls, bounds, geometricError, subfolder):
        child = {}
        child['boundingVolume'] = {}
        child['boundingVolume']['box'] = TilesetUtilities.export_bounds_to_3dtiles_volumeBoundBox(bounds)
        child['geometricError'] = geometricError
        child['content'] = {}
        child['content']['url'] = os.path.normpath(os.path.join(subfolder, "tileset.json")).replace("\\", "/")
        child['children'] = []
        cls.geometricError_sum += geometricError
        cls.unionbound(bounds)
        cls.children.append(child)

    @classmethod
    def unionbound(cls, bounds):
        if cls.union_bounds is None:
            cls.union_bounds = bounds
        if cls.union_bounds.max_x < bounds.max_x:
            cls.union_bounds.max_x = bounds.max_x
        if cls.union_bounds.min_x > bounds.min_x:
            cls.union_bounds.min_x = bounds.min_x
        if cls.union_bounds.max_y < bounds.max_y:
            cls.union_bounds.max_y = bounds.max_y
        if cls.union_bounds.min_y > bounds.min_y:
            cls.union_bounds.min_y = bounds.min_y
        if cls.union_bounds.max_z < bounds.max_z:
            cls.union_bounds.max_z = bounds.max_z
        if cls.union_bounds.min_z > bounds.min_z:
            cls.union_bounds.min_z = bounds.min_z
        return cls.union_bounds

    @classmethod
    def export_merged_tileset(cls):
        if cls.union_bounds is None:
            raise Exception("Union bounds is empty. Please, merge at least one tileset with {} function.".format(cls.append_child.__name__))

        output = {}
        output["asset"] = {
            "version": "1.0"
        }
        output["root"] = {}
        output["geometricError"] = cls.geometricError_sum,

        output["root"]['boundingVolume'] = {}
        output["root"]['boundingVolume']['box'] = TilesetUtilities.export_bounds_to_3dtiles_volumeBoundBox(cls.union_bounds)
        output["root"]["geometricError"] = cls.geometricError_sum
        output["root"]["refine"] = "ADD"

        output['root']['children'] = cls.children
        return output

    @classmethod
    def save_to(cls, filepath, minified=False):
        indent = 4
        if minified:
            indent = 0

        output = cls.export_merged_tileset()
        with open(filepath, mode="w") as tileset:
            json.dump(output, tileset, sort_keys=True, indent=indent)
