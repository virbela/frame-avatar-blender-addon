from bpy.types import Panel, UIList

from ..props.baketarget import UV_ISLAND_MODES
from ..utils.helpers import get_homeomorphic_tool_state, require_bake_scene


class FABA_PT_bake_targets(Panel):
    bl_label = "Bake targets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"

    def draw(self, context):
        if HT := get_homeomorphic_tool_state(context):
            row = self.layout.row()
            rows = 3
            if HT.selected_bake_target != -1:
                rows = 5

            row.template_list("FABA_UL_bake_targets", "", HT,  "bake_target_collection", HT, "selected_bake_target", rows=rows)
            col = row.column(align=True)
            col.operator("faba.add_bake_target", icon="ADD", text="")
            col.operator("faba.remove_bake_target", icon="REMOVE", text="")
            col.separator()
            col.operator("faba.show_selected_bt", icon="EDITMODE_HLT", text="")
            col.operator("faba.clear_bake_targets", icon="X", text="")

            if HT.selected_bake_target != -1:
                et = HT.bake_target_collection[HT.selected_bake_target]
                col.prop(et, "export", toggle=True, text="", icon="EXPORT")

                if obj := HT.avatar_mesh:
                    if obj.data.shape_keys:
                        self.layout.prop_search(et, "shape_key_name", obj.data.shape_keys, "key_blocks")

                self.layout.prop(et, "uv_mode")
                if et.uv_mode == "UV_IM_NIL":
                    return
                if len(et.variant_collection):
                    variant = et.variant_collection[0]
                    if variant.workmesh:
                        self.layout.prop_search(variant, "uv_map", variant.workmesh.data, "uv_layers")
                    else:
                        self.layout.label(text="Select work mesh to choose UV map", icon="ERROR")

                    # TODO(ranjian0) Is this used for UV packing really?
                    # self.layout.prop(et, "uv_area_weight", text="UV Area")
                    if bake_scene := require_bake_scene():
                        self.layout.prop_search(variant, "workmesh", bake_scene, "objects")
                    else:
                        self.layout.label("Missing bake scene!", icon="ERROR")
                    self.layout.prop(variant, "image")

                    if et.uv_mode == "UV_IM_FROZEN":
                        self.layout.prop(et, "atlas")
                    #TODO - this should perhaps not be visible?
                    self.layout.prop(variant, "intermediate_atlas")
                    if variant.intermediate_atlas is None:
                        self.layout.label(text="Intermediate atlas: (not assigned)", icon="UNLINKED")



class FABA_UL_bake_variants(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.image:
            layout.prop(item, "name", icon_value=item.image.preview.icon_id, text="", emboss=False, translate=False)
        else:
            layout.prop(item, "name", icon="UNLINKED", text="", emboss=False, translate=False)


class FABA_UL_bake_targets(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", icon=UV_ISLAND_MODES.members[item.uv_mode].icon, text="", emboss=False, translate=False)