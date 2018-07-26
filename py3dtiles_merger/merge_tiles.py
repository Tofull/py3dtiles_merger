#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import shutil
import os
import math

import json
import numpy as np
from pprint import pprint  # TODO(tofull) to remove
import base64
# np.set_printoptions(precision=3)
np.set_printoptions(suppress=True, precision=15)

rootpath = "D:/data_py3dtiles/output_merged"
subfolders = [name for name in os.listdir(rootpath) if os.path.isdir(os.path.join(rootpath, name))]

for folder in subfolders:
    try:
        print(base64.b64decode(folder.encode()))
    except Exception as _:
        pass
# subfolders = [
#     "1_Des_Cedres",
#     "2_Des_Cedres"
# ]



# Copy each <subfolder>/tileset.json to allow modification.
# cp tileset.json tileset.jakarto_child.json
# for subfolder in subfolders:
#     old_tileset = os.path.normpath(os.path.join(rootpath, subfolder, "tileset.json"))
#     new_tileset = os.path.normpath(os.path.join(rootpath, subfolder, "tileset.jakarto_child.json"))
#     shutil.copy(old_tileset, new_tileset)
#     print(old_tileset, "has been saved to", new_tileset)

# Write tileset.json

# with open("template_tileset.json", mode="r") as f:
#     contentFile = f.readlines()

global_tileset = os.path.normpath(os.path.join(rootpath, 'tileset.json'))
# with open(global_tileset, mode="w") as f:
#     f.writelines(contentFile)
#     print(global_tileset, "has been generated.")



def parseTransformToMatrix(transform):
    # prepare matrix
    matrix = [[0 for _ in range(4)] for _ in range(4)]
    # fill matrix
    for i,value in enumerate(transform):
        matrix[i%4][i // 4] = float(value)
    # return numpy matrix
    return np.matrix(matrix)

def parseChildBoundingVolumeBox(childbvb):
    # prepare matrix
    center_matrix = [[0] for _ in range(4)]
    vx_matrix = [[0] for _ in range(4)]
    vy_matrix = [[0] for _ in range(4)]
    vz_matrix = [[0] for _ in range(4)]
    
    # homogeneous coordinates
    center_matrix[3][0] = 1
    vx_matrix[3][0] = 1
    vy_matrix[3][0] = 1
    vz_matrix[3][0] = 1

    center_matrix[0][0], center_matrix[1][0], center_matrix[2][0] = childbvb[0], childbvb[1], childbvb[2]
    vx_matrix[0][0] = childbvb[3]
    vy_matrix[1][0] = childbvb[7]
    vz_matrix[2][0] = childbvb[11]

    # return numpy matrix
    center = np.matrix(center_matrix)
    vx = np.matrix(vx_matrix)
    vy = np.matrix(vy_matrix)
    vz = np.matrix(vz_matrix)
    return center, vx, vy, vz

def boundingBoxCreator(root_tile_center, root_tile_vx, root_tile_vy, root_tile_vz):

    # return np.block([root_tile_center[:3]], [root_tile_vx[:3]])
    return np.vstack((root_tile_center[:3], root_tile_vx[:3], root_tile_vy[:3], root_tile_vz[:3]))

def boundingboxCalculator(bounds):
    demi_axe_x = (bounds.max_x - bounds.min_x) / 2 
    demi_axe_y = (bounds.max_y - bounds.min_y) / 2 
    demi_axe_z = (bounds.max_z - bounds.min_z) / 2 

    vx = np.matrix([[demi_axe_x], [0], [0], [1]])
    vy = np.matrix([[0], [demi_axe_y], [0], [1]])
    vz = np.matrix([[0], [0], [demi_axe_z], [1]])

    center = np.matrix([[bounds.min_x + demi_axe_x], [bounds.min_y + demi_axe_y], [bounds.min_z + demi_axe_z], [1]])

    return boundingBoxCreator(center, vx, vy, vz)

def boundsToJSON(boundingBoxMatrix):
    return boundingBoxMatrix.flatten('F').tolist()[0]

def unionbound(union_bounds, bounds):
    if union_bounds.max_x is None:
        return bounds
    if union_bounds.max_x < bounds.max_x:
        union_bounds.max_x = bounds.max_x
    if union_bounds.min_x > bounds.min_x:
        union_bounds.min_x = bounds.min_x
    if union_bounds.max_y < bounds.max_y:
        union_bounds.max_y = bounds.max_y
    if union_bounds.min_y > bounds.min_y:
        union_bounds.min_y = bounds.min_y
    if union_bounds.max_z < bounds.max_z:
        union_bounds.max_z = bounds.max_z
    if union_bounds.min_z > bounds.min_z:
        union_bounds.min_z = bounds.min_z
    return union_bounds

class NullObject(object):
    def __init__(self):
        pass

union_bounds = NullObject()
union_bounds.max_x = None
union_bounds.min_x = None
union_bounds.max_y = None
union_bounds.min_y = None
union_bounds.max_z = None
union_bounds.min_z = None

geometricerror_sum = 0
children = []
# Get child value
for subfolder in subfolders:
    new_tileset = os.path.normpath(os.path.join(rootpath, subfolder, "tileset.json"))

    with open(new_tileset) as f:
        data = json.load(f)

    transform_raw = data["root"]["transform"]
    childbvb_raw = data["root"]["boundingVolume"]['box']
    geometricerror = float(data["root"]["geometricError"][0])

    
    geometricerror_sum += geometricerror
    transform = parseTransformToMatrix(transform_raw)

    (center, vx, vy, vz) = parseChildBoundingVolumeBox(childbvb_raw)

    # extract only rotation matrix
    rot_transform = transform.copy()
    rot_transform[:, 3] = 0
    rot_transform[3, 3] = 1

    root_tile_center = transform * center
    root_tile_vx = rot_transform * vx
    root_tile_vy = rot_transform * vy
    root_tile_vz = rot_transform * vz

    bbt = boundingBoxCreator(root_tile_center, root_tile_vx, root_tile_vy, root_tile_vz)

    # right : +vx
    # left : -vx
    # top : +vy
    # bottom : -vy
    # back : +vz
    # front : -vz
    fronttopleft =      root_tile_center - root_tile_vx + root_tile_vy  - root_tile_vz
    fronttopright =     root_tile_center + root_tile_vx + root_tile_vy  - root_tile_vz
    frontbottomleft =   root_tile_center - root_tile_vx - root_tile_vy  - root_tile_vz
    frontbottomright =  root_tile_center + root_tile_vx - root_tile_vy  - root_tile_vz
    backtopleft =       root_tile_center - root_tile_vx + root_tile_vy  + root_tile_vz
    backtopright =      root_tile_center + root_tile_vx + root_tile_vy  + root_tile_vz
    backbottomleft =    root_tile_center - root_tile_vx - root_tile_vy  + root_tile_vz
    backbottomright =   root_tile_center + root_tile_vx - root_tile_vy  + root_tile_vz

    box = [fronttopleft, fronttopright, frontbottomleft, frontbottomright, backtopleft, backtopright, backbottomleft, backbottomright]

    bounds = NullObject()
    bounds.max_x = max(map(lambda x: x.item((0,0)), box))
    bounds.min_x = min(map(lambda x: x.item((0,0)), box))
    bounds.max_y = max(map(lambda x: x.item((1,0)), box))
    bounds.min_y = min(map(lambda x: x.item((1,0)), box))
    bounds.max_z = max(map(lambda x: x.item((2,0)), box))
    bounds.min_z = min(map(lambda x: x.item((2,0)), box))

    bbt_computed2 = boundingboxCalculator(bounds)

    union_bounds = unionbound(union_bounds, bounds)

    child = {}
    child['boundingVolume'] = {}
    child['boundingVolume']['box'] = boundsToJSON(bbt_computed2)
    child['geometricError'] = geometricerror
    child['content'] = {}
    child['content']['url'] = os.path.normpath(os.path.join(subfolder, "tileset.json")).replace("\\","/")
    child['children'] = []
    children.append(child)

final_box = boundingboxCalculator(union_bounds)

output = {}
output["asset"] = {
    "version": "1.0"
}
output["root"] = {}
output["geometricError"] = geometricerror_sum,

output["root"]['boundingVolume'] = {}
output["root"]['boundingVolume']['box'] = boundsToJSON(final_box)
output["root"]["geometricError"] = geometricerror_sum,

output['root']['children'] = children

global_tileset = os.path.normpath(os.path.join(rootpath, 'tileset.json'))
with open(global_tileset, mode="w") as f:
    json.dump(output, f, sort_keys=True, indent=4)
    print(global_tileset, "has been generated.")