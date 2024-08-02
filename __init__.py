bl_info = {
    "name": "Cubio GLB Exporter",
    "author": "01 Studio",
    "description": "Batch export as GLTF",
    "blender": (3, 0, 0),
    "version": (1, 7, 8),
    "location": "Cubio panel",
    "warning": "",
    "category": "Import-Export"
}

import bpy
from bpy.props import *
from .cw_panel import *
from .cw_op import *
from .cw_folder_op import *
from .cw_export import *
from .cw_utils import *
from .cw_updater import check_for_updates  # Importing only the necessary functions from cw_updater
from .external.ZorakExtensions.color_harmony import *
from .external.ZorakExtensions.prefab_manager import *
from .external.VertexColorTools.init import register as reg, unregister as unreg

# When bpy is already in local, we know this is not the initial import...
# Should reload stuff
if "bpy" in locals():
    import importlib
    if "cw_panel" in locals():
        importlib.reload(cw_panel)
    if "cw_op" in locals():
        importlib.reload(cw_op)
    if "cw_folder_op" in locals():
        importlib.reload(cw_folder_op)
    if "cw_export" in locals():
        importlib.reload(cw_export)
    if "cw_utils" in locals():
        importlib.reload(cw_utils)
    if "cw_updater" in locals():
        importlib.reload(cw_updater)
    if "external.ZorakExtensions.color_harmony" in locals():
        importlib.reload(color_harmony)
    if "external.ZorakExtensions.prefab_manager" in locals():
        importlib.reload(prefab_manager)

# Define the PropertyGroups for the color palette
class ColorSlot(bpy.types.PropertyGroup):
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0)
    )

class ColorPalette(bpy.types.PropertyGroup):
    colors: bpy.props.CollectionProperty(type=ColorSlot)
    color_index: bpy.props.IntProperty()

# Define the Update Operator
class CUBIO_OT_UpdateAddon(bpy.types.Operator):
    bl_idname = "cubio.update_addon"
    bl_label = "Update Cubio Addon"

    def execute(self, context):
        check_for_updates()  # Call the update function from cw_updater
        return {'FINISHED'}

# Define the Addon Preferences Panel with Update Button
class CUBIO_PT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.operator("cubio.update_addon", text="Check for Update")

classes = (
    CWS_GLTF_PT_Panel,
    CWS_PALETTE_PT_SubPanel,
    PALETTE_MT_manage,
    GLTF_OT_Operator,
    GLTF_OT_Vertex_Alpha,
    GLFT_OT_ClearSplitNormalsData,
    GLTF_OT_Vertex_Shading_Add,
    GLTF_OT_Vertex_Shading_Remove,
    GLTF_OT_Vertex_Shading_Add_2,
    GLTF_OT_Vertex_Shading_Remove_2,
    GLTF_OT_Fix_Particle_Rotation,
    GLTF_OT_UV_REMOVE,
    ShadeVertexColorsOperator,
    ColorSlot,
    ColorPalette,
    PALETTE_OT_add_color,
    PALETTE_OT_clear_palette,
    PALETTE_OT_remove_color,
    PALETTE_OT_assign_color,
    PALETTE_OT_export_to_json,
    PALETTE_OT_import_from_json,
    ColorHarmonyProperties,
    COLOR_OT_HarmonyPopover,  
    COLOR_OT_AddHarmonyColors,  
    PREFABMANAGER_UL_List,
    PREFABMANAGER_OT_Popover,
    PREFABMANAGER_OT_RemoveInstances,
    PREFABMANAGER_OT_ToggleVisibility,
    OBJECT_OT_InstantiateObjects,
    CUBIO_OT_UpdateAddon,  # Include the update operator here
    CUBIO_PT_AddonPreferences  # Include the preferences panel here
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    reg()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    unreg()

if __name__ == "__main__":
    register()
