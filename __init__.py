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

bl_info = {
    "name" : "Unofficial Sketchfab Exporter",
    "author" : "Bart Crouch - modified by Markus Berg",
    "description" : "Upload your model to Sketchfab",
    "version" : (2, 0, 3),
    "blender" : (2, 80, 0),
    "location" : "View3D > Sidebar",
    "warning" : "Still unofficial and might cause crashes",
    "wiki_url": "",
    "category" : "Object"
}

import bpy
import os
import tempfile
import threading
import subprocess

from bpy.app.handlers import persistent
from bpy.props import (
        StringProperty,
        EnumProperty,
        BoolProperty,
        PointerProperty,
        )

#SKETCHFAB_API_URL = "https://api.sketchfab.com"
#SKETCHFAB_API_MODELS_URL = SKETCHFAB_API_URL + "/v1/models"
#SKETCHFAB_API_TOKEN_URL = SKETCHFAB_API_URL + "/v1/users/claim-token"
SKETCHFAB_MODEL_URL_SHOW = "https://sketchfab.com/show/"
SKETCHFAB_EXPORT_FILENAME = "sketchfab-export.blend"

# api v1
SKETCHFAB_API_TOKEN_URL = "https://api.sketchfab.com/v1/users/claim-token" # to be able to receive email with token

# api v3
SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v3/models'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_MODEL_URL = 'https://{}/models/'.format(SKETCHFAB_DOMAIN)

_presets = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets")
SKETCHFAB_PRESET_FILENAME = os.path.join(_presets, "sketchfab.txt")
SKETCHFAB_EXPORT_DATA_FILE = os.path.join(_presets, "sketchfab-export-data.json")
del _presets

# Singleton for storing global state
class _SketchfabState:
    __slots__ = (
        "uploading",
        "token_reload",
        "size_label",
        "model_url",

        # store report args
        "report_message",
        "report_type",
        )

    def __init__(self):
        self.uploading = False
        self.token_reload = True
        self.size_label = ""
        self.model_url = ""

        self.report_message = ""
        self.report_type = ''

sf_state = _SketchfabState()
del _SketchfabState

# if True, no contact is made with the webserver
DEBUG_MODE = False

# change a bytes int into a properly formatted string
def format_size(size):
    size /= 1024
    size_suffix = "kB"
    if size > 1024:
        size /= 1024
        size_suffix = "mB"
    if size >= 100:
        size = "%d" % int(size)
    else:
        size = "%.1f" % size
    size += " " + size_suffix

    return size

# attempt to load token from presets
@persistent
def load_token(dummy=False):
    filepath = SKETCHFAB_PRESET_FILENAME
    if not os.path.exists(filepath):
        return

    token = ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            token = f.readline()
    except:
        import traceback
        traceback.print_exc()

    wm = bpy.context.window_manager
    wm.sketchfab.token = token

# save token to file
def update_token(self, context):
    token = context.window_manager.sketchfab.token
    filepath = SKETCHFAB_PRESET_FILENAME

    path = os.path.dirname(filepath)
    if not os.path.exists(path):
        os.makedirs(path)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(token)


def upload_report(report_message, report_type):
    sf_state.report_message = report_message
    sf_state.report_type = report_type

def print_current_settings(title, filename, props):
    print("***START DEBUG SETTINGS***")
    print("name", title)
    print("description", props.description)
    print("filename", filename)
    print("tags", props.tags)
    print("categories", [get_category_label(props.categories)])
    print("isPublished", props.isPublished)
    print("isInspectable", props.isInspectable)
    print("license", get_license_label(props.licenses))
    print("isDownloadable", props.isDownloadable)
    print("private", props.private,)
    print("***END DEBUG***")

# upload the blend-file to sketchfab
def upload(filepath, filename):
    import requests

    wm = bpy.context.window_manager
    props = wm.sketchfab

    title = props.title
    if not title:
        title = os.path.splitext(os.path.basename(bpy.data.filepath))[0]

    # for debugging
    #print_current_settings(title, filename, props)

    # make sure the license is set up properly
    theLicense = get_license_label(props.licenses) if props.isDownloadable else None

    data = {
        "name": title,
        "description": props.description,
        "filename": filename,
        "tags": props.tags,
        "categories" : [get_category_label(props.categories)],
        "isPublished" : props.isPublished,
        "isInspectable" : props.isInspectable,
        "license" : [theLicense],
        "isDownloadable" : props.isDownloadable,
        "private": props.private,
        "token": props.token,
        "source": "blender-exporter",
        }

    if props.private and props.password != "":
        data["password"] = props.password

    files = {
        "modelFile": open(filepath, 'rb'),
        }
    
    try:
        r = requests.post(SKETCHFAB_API_URL, data=data, files=files, verify=False)
    except requests.exceptions.RequestException as e:
        return upload_report("Upload failed. Error: %s" % str(e), 'WARNING')

    result = r.json()
    if r.status_code != requests.codes.created:
        return upload_report("Upload failed. Error: %s" % result["error"], 'WARNING')

    sf_state.model_url = SKETCHFAB_MODEL_URL_SHOW + result["uid"]
    return upload_report("Upload complete. Available on your sketchfab.com dashboard.", 'INFO')

# operator to export model to sketchfab
class ExportSketchfab_OT_Operator(bpy.types.Operator):
    """Upload your model to Sketchfab"""
    bl_idname = "export.sketchfab"
    bl_label = "Upload"
    bl_description = "Upload objects to Sketchfab"

    _timer = None
    _thread = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not self._thread.is_alive():
                wm = context.window_manager
                props = wm.sketchfab
                terminate(props.filepath)
                if context.area:
                    context.area.tag_redraw()

                # forward message from upload thread
                if not sf_state.report_type:
                    sf_state.report_type = 'ERROR'
                self.report({sf_state.report_type}, sf_state.report_message)

                wm.event_timer_remove(self._timer)
                self._thread.join()
                sf_state.uploading = False
                return {'FINISHED'}

        return {'PASS_THROUGH'}
    
    def execute(self, context):
        import json

        if sf_state.uploading:
            self.report({'WARNING'}, "Please wait till current upload is finished")
            return {'CANCELLED'}

        wm = context.window_manager
        sf_state.model_url = ""
        props = wm.sketchfab
        if not props.token:
            self.report({'ERROR'}, "Token is missing")
            return {'CANCELLED'}

        # Prepare to save the file
        binary_path = bpy.app.binary_path
        script_path = os.path.dirname(os.path.realpath(__file__))
        basename, ext = os.path.splitext(bpy.data.filepath)
        if not basename:
            basename = os.path.join(basename, "temp")
        if not ext:
            ext = ".blend"
        tempdir = tempfile.mkdtemp()
        filepath = os.path.join(tempdir, "export-sketchfab" + ext)

        try:
            # save a copy of actual scene but don't interfere with the users models
            bpy.ops.wm.save_as_mainfile(filepath=filepath, compress=True, copy=True)

            with open(SKETCHFAB_EXPORT_DATA_FILE, 'w') as s:
                json.dump({
                        "models": props.models,
                        "lights": props.lights,
                        }, s)

            subprocess.check_call([
                    binary_path,
                    "--background",
                    "-noaudio",
                    filepath,
                    "--python", os.path.join(script_path, "pack_for_export.py"),
                    "--", tempdir
                    ])

            os.remove(filepath)
            
            # read subprocess call results
            with open(SKETCHFAB_EXPORT_DATA_FILE, 'r') as s:
                r = json.load(s)
                size = r["size"]
                props.filepath = r["filepath"]
                filename = r["filename"]

        except Exception as e:
            self.report({'WARNING'}, "Error occured while preparing your file: %s" % str(e))
            return {'FINISHED'}
        
        sf_state.uploading = True
        sf_state.size_label = format_size(size)
        self._thread = threading.Thread(
                target=upload,
                args=(props.filepath, filename),
                )
        self._thread.start()
        
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(1.0, window=context.window)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        self._thread.join()

class VIEW3D_PT_sketchfab(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Sketchfab"
    bl_context = "objectmode"
    bl_category = "Sketchfab"
    
    def draw(self, context):
        wm = context.window_manager
        props = wm.sketchfab
        if sf_state.token_reload:
            sf_state.token_reload = False
            if not props.token:
                load_token()
        layout = self.layout

        layout.label(text="Export:")
        layout.prop(props, "models")
        layout.prop(props, "lights")
        
        layout.label(text="Model info:")
        layout.prop(props, "title")
        layout.prop(props, "description")
        layout.prop(props, "tags")
        layout.prop(props, "categories")
        layout.prop(props, "isPublished")
        layout.prop(props, "isInspectable")
        layout.prop(props, "isDownloadable")
        if props.isDownloadable:
            layout.prop(props, "licenses")
        layout.prop(props, "private")
        if props.private:
            layout.prop(props, "password")

        layout.label(text="Sketchfab account:")
        layout.prop(props, "token")
        row = layout.row()
        row.operator("wm.sketchfab_email_token", text="Claim Your Token")

        if sf_state.uploading:
            layout.operator("export.sketchfab", text="Uploading %s" % sf_state.size_label)
        else:
            layout.operator("export.sketchfab")

        model_url = sf_state.model_url
        if model_url:
            layout.operator("wm.url_open", text="View Online Model", icon='URL').url = model_url

# make sure the isDownloadable checkbox becomes unchecked if not publish or not inspectable
def update_isDownloadable(self, context):
    if not self.isInspectable or not self.isPublished:
        context.window_manager.sketchfab.isDownloadable = False

# check publish and inspectable if checking downloadable
def setting_downloadable(self, context):
    if self.isDownloadable:
        context.window_manager.sketchfab.isInspectable = True
        context.window_manager.sketchfab.isPublished = True
        if not self.isDownloadable: # to make sure it stays checked
            self.isDownloadable = True

# property group containing all properties for the user interface
class SketchfabProps(bpy.types.PropertyGroup):
    description : StringProperty(
            name="Description",
            description="Description of the model (optional)",
            default="")
    filepath : StringProperty(
            name="Filepath",
            description="internal use",
            default="",
            )
    lights : EnumProperty(
            name="Lights",
            items=(('ALL', "All", "Export all lights in the file"),
                   ('NONE', "None", "Don't export any lights"),
                   ('SELECTION', "Selection", "Only export selected lights")),
            description="Determines which lights are exported",
            default='ALL',
            )
    models : EnumProperty(
            name="Models",
            items=(('ALL', "All", "Export all meshes in the file"),
                   ('SELECTION', "Selection", "Only export selected meshes")),
            description="Determines which meshes are exported",
            default='SELECTION',
            )
    private : BoolProperty(
            name="Private",
            description="Upload as private (requires a pro account)",
            default=False,
            )
    isPublished : BoolProperty(
            name="Publish",
            description="Publish your uploaded model - uncheck for draft",
            default=True,
            update=update_isDownloadable,
            )
    isInspectable : BoolProperty(
            name="Inspectable",
            description="Make your model texture inspectable",
            default=False,
            update=update_isDownloadable,
            )
    isDownloadable : BoolProperty(
            name="Downloadable",
            description="Make your model downloadable for others",
            default=False,
            update=setting_downloadable,
            )
    licenses : EnumProperty(
            name="License",
            items=(('CC', "CC Attribution", "Author must be credited. Commercial use is allowed."),
            ('CCSA', "CC Attribution-ShareAlike", "Author must be credited. Modified versions must have the same license. Commercial use is allowed."),
            ('CCND', "CC Attribution-NoDerivs", "Author must be credited. Modified versions can not be distributed. Commercial use is allowed."),
            ('CCNC', "CC Attribution-NonCommercial", "Author must be credited. No commercial use."),
            ('CCNCSA', "CC Attribution-NonCommercial-ShareAlike", "Author must be credited. No commercial use. Modified versions must have the same license."),
            ('CCNCND', "CC Attribution-NonCommercial-NoDerivs", "Author must be credited. No commercial use. Modified versions can not be distributed.")),
            description="Determines the license of the uploaded model",
            default='CC',
            )
    password : StringProperty(
            name="Password",
            description="Password-protect your model (requires a pro account)",
            default="",
            subtype="PASSWORD"
            )
    tags : StringProperty(
            name="Tags",
            description="List of tags, separated by spaces (optional)",
            default="",
            )
    title : StringProperty(
            name="Title",
            description="Title of the model (determined automatically if left empty)",
            default="",
            )
    token : StringProperty(
            name="Api Key",
            description="You can find this on your dashboard at the Sketchfab website",
            default="",
            update=update_token,
            subtype="PASSWORD"
            )
    categories : EnumProperty(
            name="Categories",
            items=(('NONE', '', ""), 
                   ('ANIPET', 'Animals & pets', ""),
                   ('ARCHIT', 'Architecture', ""),
                   ('ARTABS', 'Art & abstract', ""),
                   ('CARVEH', 'Cars & vehicles', ""),
                   ('CHACRE', 'Characters & creatures', ""),
                   ('CULTHI', 'Cultural heritage & history', ""),
                   ('ELECGA', 'Electronics & gadgets', ""),
                   ('FASTYL', 'Fashion & style', ""),
                   ('FOODRI', 'Food & drink', ""),
                   ('FURHOM', 'Furniture & home', ""),
                   ('MUSIC', 'Music', ""),
                   ('NATUPL', 'Nature & plants', ""),
                   ('NEWPOL', 'News & politics', ""),
                   ('PEOPLE', 'People', ""),
                   ('PLATRA', 'Places & travel', ""),
                   ('SCITEC', 'Science & technology', ""),
                   ('SPORFI', 'Sports & fitness', ""),
                   ('WEAPMI', 'Weapons & military', "")),
            description="Determines what category for the meshes",
            default='NONE'
            )

def get_license_label(lic_id):
    if lic_id == 'CC':
        return "CC Attribution"
    if lic_id == 'CCSA':
        return "CC Attribution-ShareAlike"
    if lic_id == 'CCND':
        return "CC Attribution-NoDerivs"
    if lic_id == 'CCNC':
        return "CC Attribution-NonCommercial"
    if lic_id == 'CCNCSA':
        return "CC Attribution-NonCommercial-ShareAlike"
    if lic_id == 'CCNCND':
        return "CC Attribution-NonCommercial-NoDerivs"

def get_category_label(cat_id):
    if cat_id == 'NONE':
        return ''
    elif cat_id == 'ANIPET':
        return 'animals-pets'
    elif cat_id == 'ARCHIT':
        return 'architecture'
    elif cat_id == 'ARTABS':
        return 'art-abstract'
    elif cat_id == 'CARVEH':
        return 'cars-vehicles'
    elif cat_id == 'CHACRE':
        return 'characters-creatures'
    elif cat_id == 'CULTHI':
        return 'cultural-heritage-history'
    elif cat_id == 'ELECGA':
        return 'electronics-gadgets'
    elif cat_id == 'FASTYL':
        return 'fashion-style'
    elif cat_id == 'FOODRI':
        return 'food-drink'
    elif cat_id == 'FURHOM':
        return 'furniture-home'
    elif cat_id == 'MUSIC':
        return 'music'
    elif cat_id == 'NATUPL':
        return 'nature-plants'
    elif cat_id == 'NEWPOL':
        return 'news-politics'
    elif cat_id == 'PEOPLE':
        return 'people'
    elif cat_id == 'PLATRA':
        return 'places-travel'
    elif cat_id == 'SCITEC':
        return 'science-technology'
    elif cat_id == 'SPORFI':
        return 'sports-fitness'
    elif cat_id == 'WEAPMI':
        return 'weapons-military'

class SketchfabEmailToken_OT_Operator(bpy.types.Operator):
    bl_idname = "wm.sketchfab_email_token"
    bl_label = "Enter your email to get a sketchfab token"

    email : StringProperty(
            name="Email",
            default="you@example.com",
            )

    def execute(self, context):
        import re
        import requests

        EMAIL_RE = re.compile(r'[^@]+@[^@]+\.[^@]+')
        if not EMAIL_RE.match(self.email):
            self.report({'ERROR'}, "Wrong email format")
        try:
            r = requests.get(SKETCHFAB_API_TOKEN_URL + "?source=blender-exporter&email=" + self.email, verify=False)
        except requests.exceptions.RequestException as e:
            self.report({'ERROR'}, str(e))
            return {'FINISHED'}

        if r.status_code != requests.codes.ok:
            self.report({'ERROR'}, "An error occured. Check the format of your email")
        else:
            self.report({'INFO'}, "Your token was sent to your email address")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=550)

# remove file copy
def terminate(filepath):
    try:
        dir_path = os.path.dirname(filepath)
        for file in os.listdir(dir_path):
            if os.path.splitext(file)[-1] in (".blend", ".fbx"): # better safe than sorry
                os.remove(os.path.join(dir_path, file))
        #os.remove(filepath.rsplit('.', 1)[0] + '.blend')
        #os.remove(filepath)
        os.rmdir(dir_path)
    except Exception as e:
        print("Deletion error:", e)


# Add-ons Preferences Update Panel

# Define Panel classes for updating
panels = (
        VIEW3D_PT_sketchfab,
        )


def update_panel(self, context):
    message = "Sketchfab Exporter: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)
                
        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass

class SfabAddonPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category : StringProperty(
            name="Tab Category",
            description="Choose a name for the category of the panel",
            default="Sketchfab",
            update=update_panel
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.label(text="Tab Category:")
        col.prop(self, "category", text="")

# registration
classes = (
    ExportSketchfab_OT_Operator,
    SketchfabProps,
    SketchfabEmailToken_OT_Operator,
    VIEW3D_PT_sketchfab,
    SfabAddonPreferences,
    )
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.WindowManager.sketchfab = PointerProperty(
        type=SketchfabProps)

    load_token()
    bpy.app.handlers.load_post.append(load_token)
    update_panel(None, bpy.context)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.WindowManager.sketchfab


if __name__ == "__main__":
    register()
