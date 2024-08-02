import bpy
import os
import re

class ImportGLBToEmptyOperator(bpy.types.Operator):
    bl_idname = "object.import_glb_to_empty"
    bl_label = "Import GLB to Empty"
    
    def execute(self, context):
        selected_object = bpy.context.active_object
        
        if selected_object is not None and selected_object.type == 'EMPTY':
            empty_name = selected_object.name
            
            # Store the empty object's name
            empty_name_before_import = empty_name
            
            # Construct the directory path using os.path.join()
            glb_directory = os.path.join(os.path.expanduser("~"), "AppData", "LocalLow", "01 Studio", "CitywarsSavage", "glbFiles")

            # Use regex to extract the name if "_prefab-" is present
            match = re.search(r"_prefab-(\d+)", empty_name)
            if match:
                actual_empty_name = match.group(1)
            else:
                actual_empty_name = empty_name

            glb_path = os.path.join(glb_directory, f"{actual_empty_name}.glb")
            
            if os.path.exists(glb_path):
                # Store the empty object's transformation properties
                empty_location = selected_object.location.copy()
                empty_rotation_euler = selected_object.rotation_euler.copy()
                empty_scale = selected_object.scale.copy()

                # Create a new collection for instances
                collection = bpy.data.collections.new(name=f"Instances_{empty_name}")
                bpy.context.scene.collection.children.link(collection)

                # Import the GLB file
                bpy.ops.import_scene.gltf(filepath=glb_path)

                # Apply the empty object's transformation properties to the imported object
                imported_object = bpy.context.active_object
                imported_object.location = empty_location
                imported_object.rotation_euler = empty_rotation_euler
                imported_object.scale = empty_scale
                
                # Set the parent collection for the imported object and its children
                bpy.context.collection.objects.unlink(imported_object)
                collection.objects.link(imported_object)

                # Link children of the imported object to the collection
                for child in imported_object.children:
                    collection.objects.link(child)
                
                # Set the position of items within the collection to (0, 0, 0)
                for obj in collection.objects:
                    obj.location = (0, 0, 0)
                
                # Join the imported object and its children
                bpy.ops.object.select_all(action='DESELECT')
                for obj in collection.objects:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = imported_object
                bpy.ops.object.join()

                # Make the joined object an instance in the collection
                instance = bpy.data.objects.new(name=f"Instance_{empty_name}", object_data=imported_object.data)
                instance.location = (0, 0, 0)  # Set the location to (0, 0, 0)
                instance.rotation_euler = empty_rotation_euler
                instance.scale = empty_scale
                collection.objects.link(instance)

                # Apply rotation transformation to the instance
                instance.rotation_euler[0] -= 1.5708  # -90 degrees in radians
                
                # Rename old empty prefab object
                temp_name = selected_object.name
                selected_object.name = f"{temp_name}_old"

                # Set up instancing for the empty object to display the corresponding mesh instance
                empty_instance = bpy.data.objects.new(name=empty_name_before_import, object_data=None)
                empty_instance.parent = selected_object.parent
                empty_instance.location = empty_location
                empty_instance.rotation_euler = empty_rotation_euler
                empty_instance.scale = empty_scale
                empty_instance.instance_collection = collection
                empty_instance.instance_type = 'COLLECTION'
                bpy.context.collection.objects.link(empty_instance)
                
                # Hide collection object
                bpy.ops.object.select_all(action='DESELECT')
                instance.select_set(True)
                bpy.ops.object.hide_view_set(unselected=False)

                #instance.hide_viewport = not instance.hide_viewport
                
                # Delete the original empty object
                bpy.ops.object.select_all(action='DESELECT')
                selected_object.select_set(True)
                bpy.ops.object.delete()

                # Delete the imported GLB outside the collection
                bpy.ops.object.select_all(action='DESELECT')
                imported_object.select_set(True)
                bpy.ops.object.delete()

        return {'FINISHED'}

class ReplaceWithEmptyOperator(bpy.types.Operator):
    bl_idname = "object.replace_with_empty"
    bl_label = "Replace with Empty"
    
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        
        for obj in selected_objects:
            if obj.type == 'MESH':
                # Store object's properties
                obj_name = obj.name
                obj_location = obj.location.copy()
                obj_rotation_euler = obj.rotation_euler.copy()
                obj_scale = obj.scale.copy()
                
                # Delete the mesh object
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.delete()

                # Create an empty object
                bpy.ops.object.empty_add(location=obj_location)
                empty_obj = bpy.context.active_object
                
                # Apply properties to the empty object
                empty_obj.name = obj_name
                empty_obj.rotation_euler = obj_rotation_euler
                empty_obj.scale = obj_scale

        return {'FINISHED'}

class GLBImportPanel(bpy.types.Panel):
    bl_label = "GLB Import Panel"
    bl_idname = "PT_GLBImportPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("object.import_glb_to_empty", text="Import GLB to Empty")
        
        row = layout.row()
        row.operator("object.replace_with_empty", text="Replace with Empty")

def register():
    bpy.utils.register_class(ImportGLBToEmptyOperator)
    bpy.utils.register_class(ReplaceWithEmptyOperator)
    bpy.utils.register_class(GLBImportPanel)

def unregister():
    bpy.utils.unregister_class(ImportGLBToEmptyOperator)
    bpy.utils.unregister_class(ReplaceWithEmptyOperator)
    bpy.utils.unregister_class(GLBImportPanel)

if __name__ == "__main__":
    register()
