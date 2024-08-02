import bpy
import socket
import sys
from ftplib import FTP_TLS

from . cw_utils import *

class CW_GLTF_Export:

  def __init__(self, op_panel, context):
    self.__op_panel = op_panel
    self.__context = context
    self.__export_folder = context.scene.cw_export_folder
    self.__center_transform = context.scene.cw_center_transform
    #self.__apply_transform = context.scene.apply_transform
    self.__export_objects = context.selected_objects
  
  def do_center(self, obj):
    if self.__center_transform:
      loc = get_object_loc(obj)
      set_object_to_loc(obj, (0,0,0))
      return loc

    return None
    
  def do_export(self):
  
    def int_to_bytes(x: int) -> bytes:
      return x.to_bytes(4, 'little')
    
    def int_from_bytes(xbytes: bytes) -> int:
      return int.from_bytes(xbytes, 'big')

    bpy.ops.object.mode_set(mode='OBJECT')
    saved_active = bpy.context.view_layer.objects.active
    def removeAttr(el):
        try:
            toRemove1 = el.data.attributes["sharp_face"]
            el.data.attributes.remove(toRemove1)
        except Exception as err:
          print(err)

        try:
            toRemove2 = el.data.attributes["sharp_edge"]
            el.data.attributes.remove(toRemove2)
        except Exception as err:
          print(err)

    for obj in bpy.data.objects:
        removeAttr(obj)
    incr = 0
    for obj in self.__export_objects:
      bpy.ops.object.select_all(action='DESELECT') 
      obj.select_set(state=True)

      # Center selected object
      old_pos = self.do_center(obj)

      # Select children if exist
      for child in get_children(obj):
        child.select_set(state=True)
        
      if obj.parent is not None:
        if old_pos is not None:
          set_object_to_loc(obj, old_pos)
        continue

      nameArr = obj.name.split("_")
      
      # Common parameters
      export_params = {
        "export_format": 'GLB',
        "filter_glob": "*.glb;*.gltf",
        "filepath": bpy.app.tempdir + "/" + nameArr[0] + ".glb",
        "use_selection": True,
        "check_existing": False,
        "export_materials": 'NONE',
        "export_nla_strips": False,
        "export_extras": True,
        "export_draco_mesh_compression_enable": False,
      }

      # Check Blender version
      blender_version = bpy.app.version

      if blender_version >= (4, 2, 0):
        # New parameters for Blender 4.2 and above
        export_params["export_vertex_color"] = 'ACTIVE'
        #export_params["export_active_vertex_color_when_no_material"] = False
        #export_params["export_all_vertex_colors"] = False
      else:
        # Old parameter for versions below 4.2
        export_params["export_colors"] = True

      if blender_version >= (4, 0, 0):
        # Add export_try_sparse_sk only if Blender version is 3.3 or newer
        export_params["export_try_sparse_sk"] = False
        
      # Use the expanded parameters in the function call
      bpy.ops.export_scene.gltf(**export_params)
      
      if not nameArr[0].isnumeric():
        self.__op_panel.report({'ERROR'}, "Error "+nameArr[0]+" is not a number")
        continue

      objectId = int(nameArr[0])
      objectIdArr = int_to_bytes(objectId)
      delimiter = bytearray([75,120,246,143])
      
      #printing debug stuff here
      print(", ".join(hex(b) for b in objectIdArr))
      print("id: "+str(objectId))
      print("playerId: "+str(bpy.context.scene.CW_PlayerId))
      
      filename = bpy.app.tempdir + "/" + nameArr[0] + ".glb"
      glbFile = open(filename, "rb")
      data = glbFile.read()
      glbFile.close()
      
      #playerNameBytes = bpy.context.scene.CW_PlayerId.encode()
      #playerNameLen = len(playerNameBytes).to_bytes(1, 'little')
      
      #number_of_bytes = (bpy.context.scene.CW_PlayerId.bit_length() + 7)
      playerIdBytes = int_to_bytes(bpy.context.scene.CW_PlayerId)
      
      dataLen = len(data)
      dataLenBytes = int_to_bytes(dataLen)
      maxLen = 249000
      sizeInMb = round(dataLen/1000000, 2)
      
      if dataLen > maxLen:
        sizeOver = round((dataLen-maxLen)/1000000, 2)
        self.__op_panel.report({'ERROR'}, "Error MAX SIZE EXCEEDED | Reduce Object #"+str(objectId)+" of "+str(sizeOver)+"mb. "+str(sizeInMb)+"mb/0.25mb")
        incr += 1
        continue
      
      s = socket.socket()
      s.connect((bpy.context.scene.CW_Address, bpy.context.scene.CW_Port))
      
      packet = bytearray()
      packet.append(11)
      
      packet = packet + objectIdArr + playerIdBytes + dataLenBytes + data + delimiter
      
      s.send(packet)
      s.close()
      
      incr += 1
      
      self.__op_panel.report({'INFO'}, "Exported #"+str(objectId)+", total size: " + str(sizeInMb)+"mb/0.25mb")

      if old_pos is not None:
        set_object_to_loc(obj, old_pos)
    
    if incr < 0:
      self.__op_panel.report({'ERROR'}, "Error while exporting, No Objects found")
      
    #self.__op_panel.report({'INFO'}, "Exported " + str(incr) + " glb to " + self.__export_folder)
    #else:
    
    bpy.ops.object.select_all(action='DESELECT')
    for obj in self.__export_objects:
        obj.select_set(state=True)
    
    bpy.context.view_layer.objects.active = saved_active
