# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# This script is called from the sketchfab addon directly
# to pack and save the file from a blender instance
# so that the users file is left untouched.

import os
import bpy
import json
import sys


SKETCHFAB_EXPORT_DATA_FILENAME = 'sketchfab-export-data.json'

SKETCHFAB_EXPORT_TEMP_DIR = sys.argv[-1]
SKETCHFAB_EXPORT_DATA_FILE = os.path.join(
    bpy.utils.user_resource('SCRIPTS'),
    "presets",
    SKETCHFAB_EXPORT_DATA_FILENAME,
    )


# save a copy of the current blendfile
def save_blend_copy():
    import time

    filepath = SKETCHFAB_EXPORT_TEMP_DIR
    filename = time.strftime("Sketchfab_%Y_%m_%d_%H_%M_%S.blend",
                             time.localtime(time.time()))
    filepath = os.path.join(filepath, filename)
    bpy.ops.wm.save_as_mainfile(filepath=filepath,
                                compress=True,
                                copy=True)
    size = os.path.getsize(filepath)

    return (filepath, filename, size)


# change visibility statuses and pack images
def prepare_assets(export_settings):
    images = set()

    for ob in bpy.data.objects:

        # make sure settings are correct so that sketchfab won't reject the upload
        if ob.type in ('MESH', 'LIGHT'):
            if ob.hide_get() or ob.hide_viewport: # delete the ones that are hidden
                bpy.data.objects.remove(ob)
                continue
        else: # it's something else
            if ob.hide_viewport: # delete the ones that are disabled in viewport
                bpy.data.objects.remove(ob)
                continue
        if ob.hide_render: # make sure it's turned on for all objects or sketchfab will reject the upload
            ob.hide_render = False

        # prepare meshes
        if ob.type == 'MESH':
            
            # the current object is what we want
            if ((export_settings['models'] == 'SELECTION' and ob.select_get()) or
                export_settings['models'] == 'ALL'):
                
                # go through the materials
                for mat_slot in ob.material_slots:
                    # CYCLES RENDER and EEVEE
                    if bpy.context.scene.render.engine in ('CYCLES', 'BLENDER_EEVEE'):
                        if not mat_slot.material:
                            continue
                        if not mat_slot.material.node_tree:
                            continue
                        imgnodes = [n for n in mat_slot.material.node_tree.nodes if n.type == 'TEX_IMAGE']
                        for node in imgnodes:
                            if node.image is not None:
                                images.add(node.image)            
                    
            # it's not an object we want - so remove it
            else:
                bpy.data.objects.remove(ob)
                continue

        # go through the lights
        elif ob.type == 'LIGHT':
            
            # it's NOT a light that we want - remove it
            if ((export_settings['lights'] == 'SELECTION' and not ob.select_get()) or
                export_settings['lights'] == 'NONE'):
                bpy.data.objects.remove(ob)

    # prepare images
    for img in images:
        if not img.packed_file:
            try:
                img.pack()
            except:
                # can fail in rare cases
                import traceback
                traceback.print_exc()


def prepare_file(export_settings):
    prepare_assets(export_settings)
    return save_blend_copy()


def read_settings():
    with open(SKETCHFAB_EXPORT_DATA_FILE, 'r') as s:
        return json.load(s)


def write_result(filepath, filename, size):
    with open(SKETCHFAB_EXPORT_DATA_FILE, 'w') as s:
        json.dump({
                'filepath': filepath,
                'filename': filename,
                'size': size,
                }, s)

if __name__ == "__main__":
    try:
        export_settings = read_settings()
        filepath, filename, size = prepare_file(export_settings)
        write_result(filepath, filename, size)
    except:
        import traceback
        traceback.print_exc()

        sys.exit(1)
