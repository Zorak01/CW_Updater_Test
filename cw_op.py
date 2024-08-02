import bpy
import bmesh
import math
import mathutils
import json
import os
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, EnumProperty, StringProperty, IntProperty, FloatVectorProperty

from .cw_export import CW_GLTF_Export

# Existing operators
class PALETTE_OT_add_color(bpy.types.Operator):
    bl_idname = "palette.add_color"
    bl_label = "Add Color"

    def execute(self, context):
        palette = context.scene.color_palette
        new_color = palette.colors.add()
        new_color.color = (1.0, 1.0, 1.0, 1.0)
        return {'FINISHED'}

class PALETTE_OT_clear_palette(bpy.types.Operator):
    bl_idname = "palette.clear_palette"
    bl_label = "Clear Palette"

    def execute(self, context):
        palette = context.scene.color_palette
        palette.colors.clear()
        return {'FINISHED'}

class PALETTE_OT_remove_color(bpy.types.Operator):
    bl_idname = "palette.remove_color"
    bl_label = "Remove Color"
    
    index: bpy.props.IntProperty()

    def execute(self, context):
        palette = context.scene.color_palette
        palette.colors.remove(self.index)
        return {'FINISHED'}

class PALETTE_OT_assign_color(bpy.types.Operator):
    bl_idname = "palette.assign_color"
    bl_label = "Assign Color"
    
    color: bpy.props.FloatVectorProperty(subtype='COLOR', size=4)

    def execute(self, context):
        bpy.context.tool_settings.vertex_paint.brush.color = self.color[:3]
        return {'FINISHED'}

class PALETTE_OT_export_to_json(bpy.types.Operator):
    bl_idname = "palette.export_to_json"
    bl_label = "Export Palette to JSON"

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        palette = context.scene.color_palette
        colors = [list(color.color) for color in palette.colors]
        data = {"colors": colors}

        if not self.filepath.endswith(".json"):
            self.filepath += ".json"

        with open(self.filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        self.report({'INFO'}, f"Color palette exported to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = "color_palette.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class PALETTE_OT_import_from_json(bpy.types.Operator):
    bl_idname = "palette.import_from_json"
    bl_label = "Import Palette from JSON"

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        with open(self.filepath, 'r') as infile:
            data = json.load(infile)
        
        palette = context.scene.color_palette
        palette.colors.clear()
        
        for color in data["colors"]:
            new_color = palette.colors.add()
            new_color.color = color

        self.report({'INFO'}, f"Color palette imported from {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = "color_palette.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Existing Operators

class GLTF_OT_Operator(Operator):
    bl_idname = "object.cw_gltf_ot_operator"
    bl_label = "Batch Export"
    bl_description = "Export selected objects as glb" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        gltf_export = CW_GLTF_Export(self, context)
        gltf_export.do_export()
        return {'FINISHED'}

class GLTF_OT_Vertex_Alpha(Operator):
    bl_idname = "object.cw_gltf_ot_vertex_alpha"
    bl_label = "Color Vertex Alpha"
    bl_description = "Color selected vertex alpha" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        mesh = bpy.context.active_object.data
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')

        selected_verts = []
        for vert in mesh.vertices:
            if vert.select == True:
                selected_verts.append(vert)

        for polygon in mesh.polygons:
            for selected_vert in selected_verts:
                for i, index in enumerate(polygon.vertices):
                    if selected_vert.index == index:
                        loop_index = polygon.loop_indices[i]
                        curColor = mesh.vertex_colors.active.data[loop_index].color
                        mesh.vertex_colors.active.data[loop_index].color = (curColor[0], curColor[1], curColor[2], context.scene.cw_vertex_alpha_value)

        bpy.ops.object.mode_set(mode = 'EDIT')
        
        return {'FINISHED'}

class GLFT_OT_ClearSplitNormalsData(Operator):
    bl_idname = "object.cw_gltf_ot_clear_custom_split_normals"
    bl_label = "Clear Custom Split Normals Data"
    bl_description = "Clear Custom Split Normals Data" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        selection = bpy.context.selected_objects
        for o in selection:
            bpy.context.view_layer.objects.active = o
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
        return {'FINISHED'}

class GLTF_OT_Vertex_Shading_Add(Operator):
    bl_idname = "object.cw_gltf_ot_vertex_shading_add"
    bl_label = "Brighten Vertex Color"
    bl_description = "Brighten by 5% current selected faces" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        mesh = bpy.context.active_object.data
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()

        selected_verts = []
        for face in bm.faces:
            allVertSelected = True
            for loop in face.loops:
                vert = loop.vert
                if vert.select == False:
                    allVertSelected = False
                    break
            
            if allVertSelected == True:
                for loop in face.loops:
                    vert = loop.vert
                    if vert.select == True:
                        colorArr = mesh.vertex_colors.active.data[loop.index].color
                        curColor = mathutils.Color((colorArr[0], colorArr[1], colorArr[2]))
                        curColor.v = curColor.v * 1.05;
                        if curColor.v > 1:
                            curColor.v = 1
                        mesh.vertex_colors.active.data[loop.index].color = (curColor.r, curColor.g, curColor.b, colorArr[3])
        
        return {'FINISHED'}

class GLTF_OT_Vertex_Shading_Remove(Operator):
    bl_idname = "object.cw_gltf_ot_vertex_shading_remove"
    bl_label = "Darken Vertex Color"
    bl_description = "Darken by 5% current selected faces" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        mesh = bpy.context.active_object.data
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()

        selected_verts = []
        for face in bm.faces:
            allVertSelected = True
            for loop in face.loops:
                vert = loop.vert
                if vert.select == False:
                    allVertSelected = False
                    break
            
            if allVertSelected == True:
                for loop in face.loops:
                    vert = loop.vert
                    if vert.select == True:
                        colorArr = mesh.vertex_colors.active.data[loop.index].color
                        curColor = mathutils.Color((colorArr[0], colorArr[1], colorArr[2]))
                        curColor.v = curColor.v * 0.95;
                        if curColor.v < 0:
                            curColor.v = 0
                        mesh.vertex_colors.active.data[loop.index].color = (curColor.r, curColor.g, curColor.b, colorArr[3])
        
        return {'FINISHED'}

class GLTF_OT_Vertex_Shading_Add_2(Operator):
    bl_idname = "object.cw_gltf_ot_vertex_shading_add_2"
    bl_label = "Brighten Vertex Color 2"
    bl_description = "Brighten by 5% current selected faces" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        mesh = obj.data

        # Ensure we're in vertex paint mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Create a BMesh from the active object's mesh data
        bm = bmesh.from_edit_mesh(mesh)

        # Get the active color layer, or create a new one if necessary
        color_layer = bm.loops.layers.color.active
        if color_layer is None:
            color_layer = bm.loops.layers.color.new("Color")
        
        # Iterate over all faces
        for vert in bm.verts:
            # Only continue if any vertices of this face are selected
            if vert.select:
                # Set the color for each loop in the face
                for loop in vert.link_loops:
                    colorArr = loop[color_layer]
                    curColor = mathutils.Color((colorArr[0], colorArr[1], colorArr[2]))
                    curColor.v = curColor.v * 1.05;
                    if curColor.v > 1:
                        curColor.v = 1
                    new_color = (curColor.r, curColor.g, curColor.b, colorArr[3])
                    loop[color_layer] = new_color

        # Write the changes back to the mesh
        bmesh.update_edit_mesh(mesh)
        
        # Switch back to vertex paint
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        return {'FINISHED'}        

class GLTF_OT_Vertex_Shading_Remove_2(Operator):
    bl_idname = "object.cw_gltf_ot_vertex_shading_remove_2"
    bl_label = "Darken Vertex Color 2"
    bl_description = "Darken by 5% current selected faces" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        obj = bpy.context.active_object
        
        mesh = obj.data

        # Ensure we're in vertex paint mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Create a BMesh from the active object's mesh data
        bm = bmesh.from_edit_mesh(mesh)

        # Get the active color layer, or create a new one if necessary
        color_layer = bm.loops.layers.color.active
        if color_layer is None:
            color_layer = bm.loops.layers.color.new("Color")
        
        # Iterate over all faces
        for vert in bm.verts:
            # Only continue if any vertices of this face are selected
            if vert.select:
                # Set the color for each loop in the face
                for loop in vert.link_loops:
                    colorArr = loop[color_layer]
                    curColor = mathutils.Color((colorArr[0], colorArr[1], colorArr[2]))
                    curColor.v = curColor.v * 0.95;
                    if curColor.v < 0:
                        curColor.v = 0
                    new_color = (curColor.r, curColor.g, curColor.b, colorArr[3])
                    loop[color_layer] = new_color

        # Write the changes back to the mesh
        bmesh.update_edit_mesh(mesh)
        
        # Switch back to vertex paint
        bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        return {'FINISHED'}

class GLTF_OT_Fix_Particle_Rotation(Operator):
    bl_idname = "object.fix_particle_rotation"
    bl_label = "Fix Particle Rotation"
    bl_description = "Used to fix the particle rotation from the switch to new vertex color particles" 
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        num_objects = len(context.selected_objects)
        
        for obj in context.selected_objects:
            # Ensure the object's rotation mode is 'XYZ' Euler for simplicity
            obj.rotation_mode = 'XYZ'
            # Correct the rotation by -90 degrees on the X-axis
            obj.rotation_euler.x = (obj.rotation_euler.x + math.radians(90)) % (2 * math.pi)
            # If rotation is 2*pi (equivalent to 360 degrees), set it to 0
            if obj.rotation_euler.x == 2 * math.pi:
                obj.rotation_euler.x = 0
            # Current scale
            current_scale = obj.scale.copy()
            # Adjust the scale to preserve the object's dimensions
            obj.scale = (current_scale.x, current_scale.z, current_scale.y)
        
        # Report the number of objects processed
        self.report({'INFO'}, "Fixed rotation for {} selected objects".format(num_objects))
        return {'FINISHED'}

class GLTF_OT_UV_REMOVE(Operator):
    bl_idname = "object.remove_uv"
    bl_label = "Remove UV" 
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            for obj in bpy.context.selected_objects:
                if(len(obj.data.uv_layers)):
                    obj.data.uv_layers.remove(obj.data.uv_layers["UVMap"])
        except:
            pass
        return {'FINISHED'}

class ShadeVertexColorsOperator(Operator):
    bl_idname = "object.cw_shade_vertex_colors"
    bl_label = "Automatic Vertex Shading"
    bl_options = {'REGISTER', 'UNDO'}

    shading_mode: EnumProperty(
        name="Shading Mode",
        description="Choose shading mode",
        items=[
            ('DIRECTIONAL', "Directional", "Shading based on fixed directions"),
            ('INTERPOLATE', "Interpolate", "Shading based on angle interpolation")
        ],
        default='DIRECTIONAL'
    )

    smooth_vertex_colors: BoolProperty(
        name="Smooth Vertex Colors",
        description="Smooth vertex colors after shading",
        default=False
    )

    use_dirt_vertex_colors: BoolProperty(
        name="Use Dirt Vertex Colors",
        description="Add procedural variation to vertex colors after shading",
        default=False
    )
    
    add_gradient_top_bottom: BoolProperty(
        name="Add Gradient Top/Bottom",
        description="Add gradient shading from top to bottom",
        default=False
    )
    
    selected_only: BoolProperty(
        name="Selected Only",
        description="Apply shading only to selected faces",
        default=False
    )

    direction_threshold: FloatProperty(
        name="Direction Threshold",
        description="Threshold for additional shading directions (in degrees)",
        default=30.0,
        min=0.0,
        max=90.0,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "shading_mode")
        layout.prop(self, "smooth_vertex_colors")
        layout.prop(self, "use_dirt_vertex_colors")
        layout.prop(self, "add_gradient_top_bottom")
        layout.prop(self, "selected_only")
        if self.shading_mode == 'INTERPOLATE':
            layout.prop(self, "direction_threshold")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        current_obj = context.active_object 
        if not current_obj or current_obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}
        
        mesh = current_obj.data
        
        # Create or get the active vertex color layer
        if mesh.vertex_colors:
            vcol_layer = mesh.vertex_colors.active
        else:
            vcol_layer = mesh.vertex_colors.new()

        # Create a bmesh to access face data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        if self.shading_mode == 'DIRECTIONAL':
            for face in bm.faces:
                if self.selected_only and not face.select:
                    continue

                shading_factor = 0.0

                # Determine shading based on direction
                if face.normal.z > 0.5:
                    shading_factor -= 0.2  # Top (20% lighter)
                elif face.normal.z < -0.5:
                    shading_factor += 0.3  # Bottom (30% darker)
                elif face.normal.y > 0.5:
                    shading_factor += 0.0  # Front (No change)
                elif face.normal.y < -0.5:
                    shading_factor -= 0.0  # Back (No change)
                elif face.normal.x > 0.5:
                    shading_factor += 0.15  # Right (15% darker)
                elif face.normal.x < -0.5:
                    shading_factor += 0.15  # Left (15% darker)

                for loop in face.loops:
                    color = vcol_layer.data[loop.index].color
                    new_color = (
                        max(0.0, min(1.0, color[0] * (1.0 - shading_factor))),
                        max(0.0, min(1.0, color[1] * (1.0 - shading_factor))),
                        max(0.0, min(1.0, color[2] * (1.0 - shading_factor))),
                        color[3]
                    )
                    vcol_layer.data[loop.index].color = new_color

        elif self.shading_mode == 'INTERPOLATE':
            # Convert direction threshold to radians
            direction_threshold_rad = math.radians(self.direction_threshold)

            for face in bm.faces:
                if self.selected_only and not face.select:
                    continue

                shading_factor = 0.0

                for direction in [(0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0)]:
                    angle = face.normal.angle(mathutils.Vector(direction))
                    if angle < direction_threshold_rad:
                        shading_factor += (1.0 - (angle / direction_threshold_rad)) * 0.1

                for loop in face.loops:
                    color = vcol_layer.data[loop.index].color
                    new_color = (
                        max(0.0, min(1.0, color[0] * (1.0 - shading_factor))),
                        max(0.0, min(1.0, color[1] * (1.0 - shading_factor))),
                        max(0.0, min(1.0, color[2] * (1.0 - shading_factor))),
                        color[3]
                    )
                    vcol_layer.data[loop.index].color = new_color

        bm.free()

        # Update mesh and viewport
        mesh.update()
        context.view_layer.update()

        # Optionally smooth vertex colors
        if self.smooth_vertex_colors:
            try:
                bpy.ops.paint.vertex_color_smooth()
            except Exception as e:
                self.report({'ERROR'}, f"Failed to smooth vertex colors: {str(e)}")

        # Optionally add procedural variation to vertex colors
        if self.use_dirt_vertex_colors:
            try:
                bpy.ops.paint.vertex_color_dirt()
            except Exception as e:
                self.report({'ERROR'}, f"Failed to add procedural variation to vertex colors: {str(e)}")

        # Handle add_gradient_top_bottom option
        if self.add_gradient_top_bottom:
            self.report({'INFO'}, "Automatic Shading Applied")
            global_matrix = current_obj.matrix_world
            local_coords = [global_matrix @ vert.co for vert in mesh.vertices]
            min_z = min(local_coords, key=lambda v: v.z)
            max_z = max(local_coords, key=lambda v: v.z)

            # Use same X and Y coordinates for both points, only differ in Z
            position_x = max_z.x
            position_y = max_z.y

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.edit_vertex_colors.paint_gradient(
                color_begin=(0.58, 0.58, 0.58, 1),
                color_end=(0.0322445, 0.0322445, 0.0322445, 1),
                position_begin=(position_x, position_y, max_z.z),  # adjusted
                position_end=(position_x, position_y, min_z.z),    # adjusted
                blend_mode='SOFT_LIGHT',
                factor_end=0.578125, # adjusted
                selected_only=self.selected_only
            )
            bpy.ops.object.mode_set(mode='VERTEX_PAINT')

        return {'FINISHED'}
