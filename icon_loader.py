

import os
import bpy

# Function to load the custom icon
def load_custom_icon():
    # Path to the custom icon image

    print(__file__)
    

    icon_path = os.path.join(os.path.dirname(__file__), "icon/Cubio_Blender_Icon.png")

    # Load the icon image into Blender
    if not os.path.exists(icon_path):
        print(f"Icon file not found: {icon_path}")
        return None

    icon_image = bpy.data.images.load(icon_path)
    return icon_image

# # Custom operator with custom icon
# class OBJECT_OT_custom_icon_operator(bpy.types.Operator):
#     bl_idname = "object.custom_icon_operator"
#     bl_label = "Custom Icon Operator"
#     bl_description = "Operator with a custom icon"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         self.report({'INFO'}, "Custom Icon Operator executed")
#         return {'FINISHED'}

# # Panel to display the operator with custom icon
# class OBJECT_PT_custom_icon_panel(bpy.types.Panel):
#     bl_idname = "OBJECT_PT_custom_icon_panel"
#     bl_label = "Custom Icon Panel"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'Tool'

#     def draw(self, context):
#         layout = self.layout
#         col = layout.column()

#         # Load the custom icon
#         icon_image = load_custom_icon()
#         if icon_image:
#             custom_icon_id = bpy.app.icons.new_image(icon_image)
#             col.operator("object.custom_icon_operator", icon_value=custom_icon_id)
#         else:
#             col.label(text="Custom icon not found")

# def register():
#     bpy.utils.register_class(OBJECT_OT_custom_icon_operator)
#     bpy.utils.register_class(OBJECT_PT_custom_icon_panel)

# def unregister():
#     bpy.utils.unregister_class(OBJECT_OT_custom_icon_operator)
#     bpy.utils.unregister_class(OBJECT_PT_custom_icon_panel)

# if __name__ == "__main__":
#     register()