from bpy.types import Context, Panel 

class FABA_PT_workmesh(Panel):
    bl_label = "FABA Workmesh"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    @classmethod
    def poll(self, context):
        return context.mesh
    
    def draw(self, context: Context):
        layout = self.layout
        avatar_mesh = context.window_manager.faba.avatar_mesh.data
        mesh = context.object.data
        
        row = layout.row()
        row.prop_search(mesh.faba_workmesh, "parent_shapekey", avatar_mesh.shape_keys, "key_blocks")
        # layout.prop(mesh.faba_workmesh, "source_uv_map")
        layout.prop(mesh.faba_workmesh, "uv_mode")
        layout.prop(mesh.faba_workmesh, "uv_channel")
