import bpy
from bpy.app.handlers import persistent
from bpy.types import Context, AddonPreferences

from .ui import register_ui, unregister_ui
from .ops import register_ops, unregister_ops
from .props import register_props, unregister_props
from .utils.helpers import get_homeomorphic_tool_state

bl_info = {
    "name": "Frame Avatar Blender Addon (FABA)",
    "description": "Provides a set of tools for the creation of homeomorphic avatars.",
    "author": "VirBela Labs <hello@framevr.io>",
    "version": (0, 2, 4),
    "blender": (3, 3, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "https://github.com/virbela/frame-avatar-blender-addon",
    "tracker_url": "https://github.com/virbela/frame-avatar-blender-addon/issues",
    "support": "COMMUNITY",
    "category": "Avatar"
}

class FrameAvatarAddonPreferences(AddonPreferences):
    bl_idname = __package__

    log_target:                     bpy.props.StringProperty(name="Log File Name", subtype="FILE_NAME", default="fabalog")
    glb_export_dir:                 bpy.props.StringProperty(
                                        name="GLB Export Dir",
                                        subtype="DIR_PATH",
                                        description="Folder to use for glb export (default is current blendfile folder)."
                                    )
    atlas_export_dir:               bpy.props.StringProperty(
                                        name="Atlas Export Dir",
                                        subtype="DIR_PATH",
                                        description="Folder to use for atlas export (default is current blendfile folder)."
                                    )
    npy_export_dir:                 bpy.props.StringProperty(
                                        name="Npy Export Dir",
                                        subtype="DIR_PATH",
                                        description="Folder to use for animation (.npy) export (default is current blendfile folder)."
                                    )
    custom_frame_validation:        bpy.props.BoolProperty(
                                        default=False,
                                        name="Frame Validation",
                                        description="Enable validation for the frame avatars. (Frame artists only!)"
                                    )

    def draw(self, context: Context):
        layout = self.layout
        layout.prop(self, "log_target")
        layout.prop(self, "glb_export_dir")
        layout.prop(self, "atlas_export_dir")
        layout.prop(self, "npy_export_dir")
        layout.prop(self, "custom_frame_validation")


def timer_update_export_actions():
    """ Create a list of actions that can be exported.
    """
    HT = get_homeomorphic_tool_state(bpy.context)

    eactions = [ea.name for ea in HT.export_animation_actions]
    for action in bpy.data.actions:
        if "tpose" in action.name.lower() or action.name in eactions:
            continue

        item = HT.export_animation_actions.add()
        item.name = action.name
        item.checked = True

    for idx, eaction in enumerate(HT.export_animation_actions):
        if eaction.name not in [a.name for a in bpy.data.actions]:
            HT.export_animation_actions.remove(idx)
    return 2 # run every 2 seconds


@persistent
def refresh_timer_on_file_open(dummy):
    if not bpy.app.timers.is_registered(timer_update_export_actions):
        bpy.app.timers.register(timer_update_export_actions, first_interval=1)
        
@persistent
def migrate_props(dummy):
    """Migrate properties from scene.homeomorphic to window_manager.faba"""
    
    # -- first move the single value props
    scene = bpy.context.scene
    wm = bpy.context.window_manager
    props = [
        "avatar_rig",
        "avatar_mesh",
        "avatar_head_bone",
        "selected_effect",
        "source_object",
        "atlas_size",
        "color_percentage",
        "painting_size",
        "select_by_atlas_image",
        "avatar_type",
        "denoise",
        "export_atlas",
        "export_glb",
        "export_animation",
        "export_animation_source",
        "export_animation_preview",
        "export_progress",
        "baking_target_uvmap",
        "baking_options",
        "target_object_uv",
        "source_object_uv",
        "debug_animation_show",
        "debug_animation_avatar_basis",
        "mirror_distance",
        "mirror_verts_source",
        "mirror_verts_target",
        "transfer_skin_source",
        "transfer_skin_target",
    ]
    
    for prop in props:
        setattr(wm.faba, prop, getattr(scene.homeomorphic, prop))
        
    # -- now move the collections
    # effect_collection
    wm.faba.effect_collection.clear()
    for effect in scene.homeomorphic.effect_collection:
        item = wm.faba.effect_collection.add()
        item.name = effect.name
        item.type = effect.type
        item.target = effect.target
        
        # -- position effect
        if effect.type == "POSITION":
            for pos_effect in effect.positions:
                item2 = item.positions.add()
                item2.parent_shapekey = pos_effect.parent_shapekey
                item2.effect_shapekey = pos_effect.effect_shapekey
        elif effect.type == "COLOR":
            for color_effect in effect.colors:
                item2 = item.colors.add()
                item2.shape = color_effect.shape
                item2.color = color_effect.color
                item2.vert_group = color_effect.vert_group

    # bake_target_collection
    
    # export_animation_actions    
    # -- these are dynamically created, so we don't need to do anything here
    
    # export_animation_json_paths
    wm.faba.export_animation_json_paths.clear()
    for path in scene.homeomorphic.export_animation_json_paths:
        item = wm.faba.export_animation_json_paths.add()
        item.file = path.file
        item.export = path.export
        

    # debug_animation_actions
    wm.faba.debug_animation_actions.clear()
    for action in scene.homeomorphic.debug_animation_actions:
        item = wm.faba.debug_animation_actions.add()
        item.name = action.name
        item.checked = action.checked
    


# Addon registration
def register():
    # XXX Order Matters
    bpy.utils.register_class(FrameAvatarAddonPreferences)
    register_props()
    register_ops()
    register_ui()

    bpy.app.timers.register(timer_update_export_actions, first_interval=1)
    bpy.app.handlers.load_post.append(refresh_timer_on_file_open)


def unregister():
    unregister_ui()
    unregister_ops()
    unregister_props()
    bpy.utils.unregister_class(FrameAvatarAddonPreferences)

    bpy.app.timers.unregister(timer_update_export_actions)
    bpy.app.handlers.load_post.remove(refresh_timer_on_file_open)


if __name__ == "__main__":
    # XXX ScriptWatcher hook for local development
    import os 
    os.system("cls" if os.name == "nt" else "clear")

    try:
        unregister()
    except RuntimeError:
        pass # some class probably not registered
    except Exception:
        # show any other exception
        import traceback
        traceback.print_exc()

    register()
