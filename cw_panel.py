import bpy
from .external.VertexColorTools.operators.paint_gradient import EDITVERTCOL_OT_PaintGradient
from .external.ZorakExtensions.color_harmony import COLOR_OT_HarmonyPopover, COLOR_OT_AddHarmonyColors
from .external.ZorakExtensions.prefab_manager import PREFABMANAGER_OT_Popover  # Import the popover operator

class CWS_GLTF_PT_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Cubio Exporter v1.81"
    bl_category = "Cubio"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.label(text="Shading Tool")

        row = layout.row()
        row.operator('object.cw_gltf_ot_vertex_shading_add', text='Add 5%', icon='ADD')

        row = layout.row()
        row.operator('object.cw_gltf_ot_vertex_shading_remove', text='Remove 5%', icon='REMOVE')

        row = layout.row()
        row.label(text="Shading Tool (With Gradient)")

        row = layout.row()
        row.operator('object.cw_gltf_ot_vertex_shading_add_2', text='Add 5% 2', icon='ADD')

        row = layout.row()
        row.operator('object.cw_gltf_ot_vertex_shading_remove_2', text='Remove 5% 2', icon='REMOVE')

        row = layout.row()
        row.operator(EDITVERTCOL_OT_PaintGradient.bl_idname, text="Gradient", icon='NODE_TEXTURE')

        row = layout.row()
        row.operator("object.cw_shade_vertex_colors", text="Automatic Shading", icon='SHADERFX')

        row = layout.row()
        row.label(text="Misc Tools")

        row = layout.row()
        row.operator('paint.vertex_color_hsv', text="Adjust HSV", icon='MOD_HUE_SATURATION')
        
        row = layout.row()
        row.operator("prefab_manager.popover", text="Prefab Manager", icon='MESH_CUBE')

        row = layout.row()
        row.operator("object.remove_uv", text="Remove UV", icon='TRASH')

        row = layout.row()
        row.label(text="GLTF Export")

        row = layout.row()
        row.prop(context.scene, "cw_center_transform", text="Center transform")

        row = layout.row()
        row.operator('object.cw_gltf_ot_operator', text='Export', icon='EXPORT')


class CWS_PALETTE_PT_SubPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Color Palette"
    bl_category = "Cubio"
    bl_parent_id = "CWS_GLTF_PT_Panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        color_slots = scene.color_palette.colors

        if len(color_slots) < 5:
            row = layout.row(align=True)
            split = row.split(factor=0.9, align=True)
            button_row = split.row(align=True)
            button_row.operator('palette.add_color', text='', icon='ADD')
            button_row.operator('palette.remove_color', text='', icon='REMOVE')
            button_row.operator('palette.clear_palette', text='', icon='LOOP_BACK')
            button_row.operator('color.harmony_popover', text='', icon='COLOR')
            menu_row = split.row(align=True)
            menu_row.alignment = 'RIGHT'
            menu_row.menu("PALETTE_MT_manage", text="", icon='PREFERENCES')

        row = layout.row()
        col_main = row.column()
        col_buttons = row.column(align=True)

        col_count = 4

        for i in range(0, len(color_slots)):
            if i % col_count == 0:
                col_main_row = col_main.row(align=True)
            col = col_main_row.column(align=True)
            box = col.box()
            box.use_property_split = False
            box.use_property_decorate = False
            box.prop(color_slots[i], "color", text="")
            row_buttons = box.row(align=True)
            row_buttons.scale_x = 3.0
            assign_op = row_buttons.operator("palette.assign_color", text="", icon='PASTEDOWN')
            assign_op.color = color_slots[i].color
            row_buttons.operator("palette.remove_color", text="", icon='X').index = i

        if len(color_slots) >= 5:
            col_buttons.operator('palette.add_color', text='', icon='ADD')
            col_buttons.operator('palette.remove_color', text='', icon='REMOVE')
            col_buttons.operator('palette.clear_palette', text='', icon='LOOP_BACK')
            col_buttons.operator('color.harmony_popover', text='', icon='COLOR')
            col_buttons.separator()
            col_buttons.menu("PALETTE_MT_manage", text="", icon='PREFERENCES')

class PALETTE_MT_manage(bpy.types.Menu):
    bl_label = "Manage Palette"

    def draw(self, context):
        layout = self.layout
        layout.operator('palette.import_from_json', text='Import Palette', icon='IMPORT')
        layout.operator('palette.export_to_json', text='Export Palette', icon='EXPORT')

class COLOR_OT_HarmonyPopover(bpy.types.Operator):
    bl_idname = "color.harmony_popover"
    bl_label = "Harmony Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.window_manager
        return wm.invoke_popup(self, width=300)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        harmony_props = scene.color_harmony_props

        for i in range(len(harmony_props.harmony_colors)):
            color = harmony_props.harmony_colors[i]
            row = layout.row()
            row.prop(color, "color", text="")

        row = layout.row()
        row.operator("color.add_harmony_colors", text="Add Colors to Palette")
