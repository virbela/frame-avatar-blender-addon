import bpy
from ..utils.helpers import get_homeomorphic_tool_state

class FABA_PT_export(bpy.types.Panel):
    bl_label = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"

    def draw(self, context):
        if HT := get_homeomorphic_tool_state(context):
            self.layout.prop(HT, "avatar_type", expand=True)
            self.layout.prop(HT, "export_glb")
            self.layout.prop(HT, "export_atlas")
            if HT.export_atlas:
                sp = self.layout.split(factor=0.05)
                _ = sp.column()
                col = sp.column()
                col.prop(HT, "denoise")


            anim = self.layout.row(align=True)
            anim.enabled = HT.avatar_type == "FULLBODY"
            anim.prop(HT, "export_animation")

            if HT.export_animation:
                self.layout.prop(HT, "export_animation_source", expand=True)

                if HT.should_export_animation_action():
                    if not HT.export_animation_actions:
                        self.layout.label(text="No actions found!", icon="ERROR")
                    else:
                        sp = self.layout.split(factor=0.05)
                        _ = sp.column()
                        col = sp.column()
                        col.prop(HT, "export_animation_preview", toggle=True, text="Preview Only")
                        for ea in sorted(HT.export_animation_actions, key=lambda a: a.name):
                            col.prop(ea, "checked", text=ea.name)


                if HT.should_export_animation_json():
                    for idx, path in enumerate(HT.export_animation_json_paths):
                        box = self.layout.box()
                        row = box.row(align=True)
                        row.prop(path, "file", text="JSON")
                        row.separator()
                        row.prop(path, "export", icon="EXPORT", text="")
                        row.operator("faba.remove_json_path", icon="CANCEL", text="").index = idx
                    
                    cf = self.layout.column_flow(columns=3, align=True)
                    cf.label() # Dummy to fill first column
                    cf.operator("faba.add_json_path")
    
            row = self.layout.box()
            row.scale_y = 1.5
            row.operator("faba.export", text="Export")
            # if HT.export_progress > -1:
            #     self.layout.prop(HT, "export_progress", slider=True)
            # else:
            #     self.layout.operator("faba.export", text="Export")
