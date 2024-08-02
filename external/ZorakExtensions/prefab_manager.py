import bpy
import os
import re

# Path to the folder containing your .glb files
glb_path = os.path.expanduser("~\\AppData\\LocalLow\\01 Studio\\CitywarsSavage\\glbFiles")

def instantiate_glb(glb_file, collection_name):
    # Import the GLB file
    bpy.ops.import_scene.gltf(filepath=glb_file)
    
    # The imported objects will be selected, so we can move them to a new collection
    imported_objects = bpy.context.selected_objects
    
    # Create a new collection named after the root object
    new_collection = bpy.data.collections.new(collection_name)
    
    # Move the imported objects to the new collection
    for obj in imported_objects:
        new_collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)
    
    return new_collection

def exclude_collection_from_view_layer(view_layer, collection_name):
    layer_collection = view_layer.layer_collection
    collections = [layer_collection]
    while collections:
        collection = collections.pop()
        if collection.name == collection_name:
            collection.exclude = True
        else:
            collections.extend(collection.children)

def include_all_collections(view_layer):
    layer_collection = view_layer.layer_collection
    collections = [layer_collection]
    while collections:
        collection = collections.pop()
        collection.exclude = False
        collections.extend(collection.children)

def instantiate_objects():
    # Create or get the master collection "Instances"
    if "Instances" not in bpy.data.collections:
        instances_collection = bpy.data.collections.new("Instances")
        bpy.context.scene.collection.children.link(instances_collection)
    else:
        instances_collection = bpy.data.collections["Instances"]

    # Get the current view layer
    view_layer = bpy.context.view_layer

    # Dictionary to store prefab_id to collection mapping
    collection_mapping = {}

    # Iterate through all objects in the scene
    for obj in bpy.context.scene.objects:
        if obj.type == 'EMPTY' and re.search(r"_prefab-\d+(\.\d+)?", obj.name):
            # Extract the ID from the empty object name
            match = re.search(r"_prefab-(\d+)", obj.name)
            if match:
                prefab_id = match.group(1)
                if prefab_id not in collection_mapping:
                    glb_file = os.path.join(glb_path, f"{prefab_id}.glb")
                    
                    # Check if the GLB file exists
                    if os.path.exists(glb_file):
                        new_collection = instantiate_glb(glb_file, prefab_id)
                        if new_collection:
                            instances_collection.children.link(new_collection)
                            exclude_collection_from_view_layer(view_layer, new_collection.name)
                            collection_mapping[prefab_id] = new_collection

    # Instantiate collections on empty objects with matching numbers
    for obj in bpy.context.scene.objects:
        if obj.type == 'EMPTY' and re.search(r"_prefab-\d+(\.\d+)?", obj.name):
            # Extract the ID from the empty object name
            match = re.search(r"_prefab-(\d+)", obj.name)
            if match:
                prefab_id = match.group(1)
                if prefab_id in collection_mapping:
                    obj.instance_type = 'COLLECTION'
                    obj.instance_collection = collection_mapping[prefab_id]

    # Check for nested _prefab-<ID> objects in imported collections
    for collection in instances_collection.children:
        check_nested_prefabs(collection, collection_mapping, instances_collection, view_layer)

    # Set show_instancer to True by default after instantiation
    bpy.context.scene.show_instancer = True
    toggle_instancer_visibility(True)
    
    # Set the default display type to 'TEXTURED' (Vertex Color) for all _prefab-# objects
    update_display_type('TEXTURED')

def check_nested_prefabs(collection, collection_mapping, instances_collection, view_layer):
    for obj in collection.objects:
        if obj.type == 'EMPTY' and re.search(r"_prefab-\d+(\.\d+)?", obj.name):
            match = re.search(r"_prefab-(\d+)", obj.name)
            if match:
                prefab_id = match.group(1)
                if prefab_id not in collection_mapping:
                    glb_file = os.path.join(glb_path, f"{prefab_id}.glb")
                    if os.path.exists(glb_file):
                        new_collection = instantiate_glb(glb_file, prefab_id)
                        if new_collection:
                            collection.children.link(new_collection)  # Link to parent collection
                            exclude_collection_from_view_layer(view_layer, new_collection.name)
                            collection_mapping[prefab_id] = new_collection
                            obj.instance_type = 'COLLECTION'
                            obj.instance_collection = new_collection
                            check_nested_prefabs(new_collection, collection_mapping, instances_collection, view_layer)

def remove_instances():
    if "Instances" in bpy.data.collections:
        instances_collection = bpy.data.collections["Instances"]
        # Unlink and remove all objects in the Instances collection and its children
        for sub_collection in list(instances_collection.children):
            for obj in list(sub_collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(sub_collection)
        # Clean up orphaned data blocks
        orphan_cleanup()
        # Set show_instancer back to True
        bpy.context.scene.show_instancer = True
        toggle_instancer_visibility(True)

def orphan_cleanup():
    # Remove orphaned meshes
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    # Remove orphaned materials
    for material in bpy.data.materials:
        if material.users == 0:
            bpy.data.materials.remove(material)
    # Remove orphaned textures
    for texture in bpy.data.textures:
        if texture.users == 0:
            bpy.data.textures.remove(texture)
    # Remove orphaned images
    for image in bpy.data.images:
        if image.users == 0:
            bpy.data.images.remove(image)
    # Remove orphaned collections
    for collection in bpy.data.collections:
        if collection.users == 0:
            bpy.data.collections.remove(collection)
    # Purge all unused data blocks
    bpy.ops.outliner.orphans_purge()

def get_prefab_collections():
    collections = []
    if "Instances" in bpy.data.collections:
        instances_collection = bpy.data.collections["Instances"]
        for collection in instances_collection.children:
            collections.append(collection)
    return collections

def toggle_visibility(collection_name):
    view_layer = bpy.context.view_layer
    layer_collection = view_layer.layer_collection
    collections = [layer_collection]
    while collections:
        collection = collections.pop()
        if collection.name == collection_name:
            collection.exclude = not collection.exclude
        else:
            collections.extend(collection.children)

    # Update the custom property for UI icon change
    collection = bpy.data.collections[collection_name]
    collection["is_visible"] = not collection.get("is_visible", True)

def update_display_type(display_type):
    view_layer = bpy.context.view_layer
    instances_collection = bpy.data.collections.get("Instances")

    if instances_collection:
        # Include all collections in the view layer
        include_all_collections(view_layer)

        # Update the display type for all _prefab-# objects
        prefab_pattern = re.compile(r"_prefab-\d+(\.\d+)?")
        for obj in bpy.context.scene.objects:
            if prefab_pattern.match(obj.name):
                obj.display_type = display_type

        # Re-exclude all collections in the Instances collection
        for collection in instances_collection.children:
            exclude_collection_from_view_layer(view_layer, collection.name)

def toggle_instancer_visibility(show_instancer):
    prefab_pattern = re.compile(r"_prefab-\d+(\.\d+)?")
    for obj in bpy.context.scene.objects:
        if prefab_pattern.match(obj.name) and obj.instance_type == 'COLLECTION':
            obj.show_instancer_for_viewport = show_instancer

class PREFABMANAGER_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        collection = item
        if collection.name != "Instances":
            layout.prop(collection, "name", text="", emboss=False)
            icon = 'HIDE_OFF' if collection.get("is_visible", True) else 'HIDE_ON'
            row = layout.row(align=True)
            op = row.operator("prefab_manager.toggle_visibility", text="", icon=icon)
            op.collection_name = collection.name

class PREFABMANAGER_OT_Popover(bpy.types.Operator):
    bl_label = "Prefab Manager"
    bl_idname = "prefab_manager.popover"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.operator("object.instantiate_objects", text="Instantiate Prefabs")
        layout.operator("prefab_manager.remove_instances", text="Remove Instances")
        
        prefab_collections = get_prefab_collections()
        if prefab_collections:
            layout.label(text="Prefab Collections:")
            row = layout.row()
            row.template_list("PREFABMANAGER_UL_List", "prefab_collections", bpy.data, "collections", context.scene, "prefab_manager_list_index")
            layout.label(text="Display Options:")
            layout.prop(context.scene, "prefab_display_type", text="")
            layout.label(text="Instancer Visibility:")
            layout.prop(context.scene, "show_instancer", text="")

class PREFABMANAGER_OT_RemoveInstances(bpy.types.Operator):
    bl_label = "Remove Instances"
    bl_idname = "prefab_manager.remove_instances"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_instances()
        return {'FINISHED'}

class PREFABMANAGER_OT_ToggleVisibility(bpy.types.Operator):
    bl_label = "Toggle Visibility"
    bl_idname = "prefab_manager.toggle_visibility"
    bl_options = {'REGISTER', 'UNDO'}
    
    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        toggle_visibility(self.collection_name)
        return {'FINISHED'}

class OBJECT_OT_InstantiateObjects(bpy.types.Operator):
    bl_label = "Instantiate Prefabs"
    bl_idname = "object.instantiate_objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        instantiate_objects()
        return {'FINISHED'}
