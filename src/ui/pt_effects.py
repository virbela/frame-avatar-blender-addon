from bpy.types import Panel, UIList, Context

from ..utils.helpers import get_homeomorphic_tool_state


class FABA_UL_effects(UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        layout.prop(
            item,
            "name",
            icon="FORCE_TURBULENCE",
            text="",
            emboss=False,
            translate=False,
        )


class FABA_PT_effects(Panel):
    bl_label = "Effects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Frame Avatar"

    def draw(self, context: Context) -> None:
        if HT := get_homeomorphic_tool_state(context):
            ob = HT.avatar_mesh
            self.layout.template_list(
                "FABA_UL_effects", "", HT, "effect_collection", HT, "selected_effect"
            )
            effect_actions = self.layout.row(align=True)
            effect_actions.operator("faba.add_effect")
            effect_actions.operator("faba.remove_effect")

            if HT.selected_effect != -1:
                et = HT.effect_collection[HT.selected_effect]
                self.layout.prop(et, "type")

                key = ob.data.shape_keys
                if et.type == "POSITION":
                    for idx, pos in enumerate(et.positions):
                        box = self.layout.box()
                        row = box.row()
                        row.prop_search(
                            pos, "parent_shapekey", key, "key_blocks", text=""
                        )
                        row.label(icon="TRIA_RIGHT")
                        row.prop_search(
                            pos, "effect_shapekey", key, "key_blocks", text=""
                        )
                        row.operator(
                            "faba.remove_position_effect", icon="X", text=""
                        ).index = idx
                    self.layout.operator("faba.add_position_effect")

                elif et.type == "COLOR":
                    for idx, col in enumerate(et.colors):
                        box = self.layout.box()
                        row = box.row()
                        row.prop_search(col, "shape", key, "key_blocks", text="")
                        row.label(icon="TRIA_RIGHT")
                        row.prop(col, "color", text="")
                        row.operator(
                            "faba.remove_color_effect", icon="X", text=""
                        ).index = idx
                        box.prop_search(col, "vert_group", ob, "vertex_groups", text="")
                    self.layout.operator("faba.add_color_effect")
