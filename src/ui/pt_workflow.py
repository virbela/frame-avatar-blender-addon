import bpy
from bpy.types import Panel
from ..utils.logging import log
from ..utils.helpers import get_homeomorphic_tool_state, require_bake_scene


class FABA_PT_workflow(Panel):
    bl_label = "Workflow"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"
    bl_idname = "FABA_PT_workflow"

    def draw(self, context):
        layout = self.layout
        HT = get_homeomorphic_tool_state(context)

        layout.prop(HT, "avatar_mesh")
        layout.prop(HT, "avatar_rig")
        if HT.avatar_rig:
            layout.prop_search(HT, "avatar_head_bone", HT.avatar_rig.pose, "bones")


class FABA_PT_workflow_workmeshes(Panel):
    bl_label = "Work Meshes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"
    bl_parent_id = "FABA_PT_workflow"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        HT = get_homeomorphic_tool_state(context)
        layout = self.layout
        col = layout.column(align=True)
        col.operator("faba.create_workmeshes_for_all_shapekeys")
        col.operator("faba.create_workmeshes_for_selected_target")
        col = layout.column(align=True)
        col.operator("faba.workmesh_to_shapekey")
        col.operator("faba.all_workmesh_to_shapekey")
        col = layout.column(align=True)
        col.operator("faba.shapekey_to_workmesh")
        col.operator("faba.all_shapekey_to_workmesh")
        col = layout.column(align=True)
        col.operator("faba.update_all_workmeshes")
        col.operator("faba.workmesh_symmetrize")
        box = layout.box()
        box.label(text="Mirror Workmesh Vertices")
        col = box.column(align=True)
        col.prop(HT, "mirror_distance")
        col.prop(HT, "mirror_verts_source")
        col.prop(HT, "mirror_verts_target")
        col.operator("faba.mirror_workmesh_verts")


class FABA_PT_workflow_texture(Panel):
    bl_label = "Texture Atlas"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"
    bl_parent_id = "FABA_PT_workflow"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        HT = get_homeomorphic_tool_state(context)

        layout.prop(HT, "atlas_size")
        layout.prop(HT, "color_percentage")
        h = int(HT.color_percentage * HT.atlas_size / 100)
        layout.label(text=f"Color Region Height in pixels: {h}")

        layout.operator("faba.auto_assign_atlas")
        layout.operator("faba.pack_uv_islands")


class FABA_PT_workflow_materials(Panel):
    bl_label = "Work Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"
    bl_parent_id = "FABA_PT_workflow"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        HT = get_homeomorphic_tool_state(context)

        col = layout.column(align=True)
        col.operator("faba.update_all_materials")
        col.operator("faba.update_selected_material")

        layout.separator()
        col = layout.column(align=True)
        col.operator("faba.select_by_atlas")
        col.operator("faba.set_selected_workmesh_atlas")
        layout.prop(HT, "select_by_atlas_image")


class FABA_PT_workflow_baking(Panel):
    bl_label = "Baking"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"
    bl_parent_id = "FABA_PT_workflow"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        HT = get_homeomorphic_tool_state(context)


        bake_scene = require_bake_scene()
        selection = [o for o in context.selected_objects]
        try:
            col = layout.column(align=True)
            col.prop(bake_scene.cycles, "samples", text="Bake Samples")
            col.prop(bake_scene.render.bake, "margin", text="Bake Margin")
        except AttributeError as e:
            log.info(e)
            layout.label(text="Please ensure Cycles Render Engine is enabled in the addons list!", icon="ERROR")

        layout.row(align=True).prop(HT, "baking_options", expand=True)
        if selection and selection[0].type == "MESH":
            layout.prop_search(HT, "baking_target_uvmap", selection[0].data, "uv_layers")

        col = layout.column(align=True)
        col.operator("faba.bake_all")
        col.operator("faba.bake_selected_bake_target")
        if selection:
            col.operator("faba.bake_selected_workmeshes")
        else:
            layout.label(text="Please select a workmesh to bake from one!", icon="INFO")


class FABA_PT_workflow_helpers(Panel):
    bl_label = "Helpers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"
    bl_parent_id = "FABA_PT_workflow"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        HT = get_homeomorphic_tool_state(context)

        col = layout.column(align=True)
        col.operator("faba.reset_uv_transforms")
        col.separator()
        uv_col = col.box().column()
        uv_col.prop(HT, "source_object_uv")
        uv_col.prop(HT, "target_object_uv")
        uv_col.operator("faba.copy_uv_layers")


class FABA_PT_workflow_animation(Panel):
    bl_label = "Animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"
    bl_parent_id = "FABA_PT_workflow"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        HT = get_homeomorphic_tool_state(context)

        box = layout.box()
        box.label(text="Transfer Skin Weights")
        col = box.column(align=True)
        col.prop(HT, "transfer_skin_source", text="Source")
        col.prop(HT, "transfer_skin_target", text="Target")
        box.operator("faba.transfer_skin_weights")


class FABA_PT_workflow_debug(Panel):
    bl_label = "Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Avatar"
    bl_parent_id = "FABA_PT_workflow"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        HT = get_homeomorphic_tool_state(context)

        layout.label(text="Debug tools")
        layout.operator("faba.clear_bake_scene")
        layout.operator("faba.start_debugger")
        layout.label(text="Bone Animation Viz")
        col = layout.column(align=True)
        col.prop_search(HT, "debug_animation_avatar_basis", bpy.data, "objects")
        if basis := HT.debug_animation_avatar_basis:
            if "MorphSets_Avatar" not in basis:
                col.label(text="Avatar Basis does not have metadata", icon="ERROR")
            else:
                for action in HT.debug_animation_actions:
                    row = col.row(align=True)
                    row.prop(action, "checked")
                    row.label(text=action.name)

        op_text = "Stop Animation" if HT.debug_animation_show else "Show Animation"
        layout.operator("faba.debug_bone_animation", text=op_text)
        layout.operator("faba.custom_operator")
