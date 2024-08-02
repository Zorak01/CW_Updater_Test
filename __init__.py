bl_info = {
    "name": "Cubio GLB Exporter",
    "author": "01 Studio",
    "description": "Batch export as GLTF",
    "blender": (3, 0, 0),
    "version": (1, 7, 6),
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
from .external.ZorakExtensions.color_harmony import *
from .external.ZorakExtensions.prefab_manager import *

from .external.VertexColorTools.init import register as reg, unregister as unreg

# When bpy is already in local, we know this is not the initial import...
# Should reload stuff
if "bpy" in locals():
    # ...so we need to reload our submodule(s) using importlib
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

# Path to the folder containing your .glb files
glb_path = os.path.expanduser("~\\AppData\\LocalLow\\01 Studio\\CitywarsSavage\\glbFiles")

# Function to create color previews
def create_color_previews():
    for i in range(5):  # Assuming a maximum of 5 color previews
        setattr(bpy.types.Scene, f"color_preview_{i}", FloatVectorProperty(
            name=f"Color Preview {i+1}",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(0.5, 0.5, 0.5)
        ))

# Function to remove color previews
def remove_color_previews():
    for i in range(5):
        delattr(bpy.types.Scene, f"color_preview_{i}")

def on_prefab_display_type_update(self, context):
    update_display_type(context.scene.prefab_display_type)

def on_show_instancer_update(self, context):
    toggle_instancer_visibility(context.scene.show_instancer)

bpy.types.Scene.cw_export_folder = StringProperty(
    name="Export folder", 
    subtype="DIR_PATH", 
    description="Directory to export the glb files into"
)

bpy.types.Scene.cw_center_transform = BoolProperty(
    name="Center transform",
    default=True,
    description="Set the pivot point of the object to the center"
)

bpy.types.Scene.cw_vertex_alpha_value = FloatProperty(
    name="Vertex Alpha Value",
    default=1, 
    min=0, 
    max=1
)

# Adding new properties for player id
bpy.types.Scene.CW_PlayerId = IntProperty(
    name="Cubio Player Id",
    description="Player Id for Cubio",
    default=0
)

# Adding new properties for port, and address
bpy.types.Scene.CW_Port = IntProperty(
    name="Cubio Port",
    description="Port for Cubio",
    default=0
)

bpy.types.Scene.CW_Address = StringProperty(
    name="Cubio Address",
    description="Address for Cubio",
    default="")

bpy.types.Scene.prefab_display_type = EnumProperty(
    name="Display As",
    description="Display type for prefab objects",
    items=[
        ('BOUNDS', "Bounds", "Display the bounds of the object"),
        ('WIRE', "Wire", "Display the object as a wireframe"),
        ('TEXTURED', "Vertex Color", "Display the object with textures (if textures are enabled in the viewport)")
    ],
    default='TEXTURED',  # Default to "Vertex Color"
    update=on_prefab_display_type_update
)

bpy.types.Scene.show_instancer = BoolProperty(
    name="Show Instancer",
    description="Toggle the visibility of the instancer for the viewport",
    default=True,  # Default to True
    update=on_show_instancer_update
)

bpy.types.Scene.prefab_manager_list_index = IntProperty(
    name="Prefab Manager List Index",
    default=0
)
# Remember to register new operators. They must be imported too
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
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    reg()
    # Add the color palette and harmony properties to the scene
    bpy.types.Scene.color_palette = bpy.props.PointerProperty(type=ColorPalette)
    bpy.types.Scene.color_harmony_props = bpy.props.PointerProperty(type=ColorHarmonyProperties)
    create_color_previews()
    print("Registered all classes")

def unregister():
    # Remove the color palette and harmony properties from the scene
    del bpy.types.Scene.color_palette
    del bpy.types.Scene.color_harmony_props
    remove_color_previews()
    for cls in classes:
        bpy.utils.unregister_class(cls)
    unreg()
    print("Unregistered all classes")

if __name__ == "__main__":
    register()
