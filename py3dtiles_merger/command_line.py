#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import argparse
import base64
import os

from py3dtiles_merger.TilesetParser import TilesetParser
from py3dtiles_merger.TilesetMerger import TilesetMerger

def command_line():
    parser = argparse.ArgumentParser(description='Generate a global tileset given a list of 3dtiles subfolders generated with py3dtiles.')
    parser.add_argument("--rootpath", '-r', type=str, default='.', help="Root path to find subfolder")
    parser.add_argument('--verbose', '-v', action='count', help="Verbosity (-v simple info, -vv more info, -vvv spawn info)", default=0)
    parser.add_argument(
        'subfolders',
        nargs='*',
        help='Subfolders to merge. The folder must contain a 3dtiles tileset.json generated with py3dtiles.')
    args = parser.parse_args()
    if args.verbose > 2:
        print("Command line args : \n\t{}".format(vars(args)))
    parse_args(**vars(args))

def parse_args(subfolders=None, rootpath=None, verbose=None, **kwargs):
    if not subfolders:
        if verbose > 0:
            print("No subfolder specified. Auto detect subfolder from folder : {}".format(rootpath))
        subfolders = [name for name in os.listdir(rootpath) if os.path.isdir(os.path.join(rootpath, name))]

    if verbose > 0:
        print("Detected {} file{}".format(len(subfolders), 's' if len(subfolders) > 1 else ''))
    main(rootpath, subfolders, verbose=verbose)


def main(rootpath, subfolders, verbose=0, **kwargs):
    if verbose > 0:
        print("Prepare to merge {} file{}".format(len(subfolders), 's' if len(subfolders) > 1 else ''))
    global_tileset = os.path.normpath(os.path.join(rootpath, 'tileset.json'))
    for index, subfolder in enumerate(subfolders):
        if verbose > 0:
            print("Step {} / {}".format(index + 1, len(subfolders)))
            try:
                print("\t Tileset to merge : {}\n\t (base64-decoded): {}".format(subfolder, base64.b64decode(subfolder.encode()).decode('utf-8')))
            except Exception as _:
                print("\t Tileset to merge : {}".format(subfolder))
                pass
        tileset = os.path.normpath(os.path.join(rootpath, subfolder, "tileset.json"))

        tilesetparser = TilesetParser(tileset)

        geometricError = tilesetparser.geometricError
        bounds = tilesetparser.bounds

        TilesetMerger.append_child(bounds, geometricError, subfolder)

    TilesetMerger.save_to(global_tileset)
    print(global_tileset, "has been generated.")

if __name__ == "__main__":
    command_line()