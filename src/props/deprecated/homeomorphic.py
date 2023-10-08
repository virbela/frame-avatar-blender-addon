import bpy
from bpy.types import Context, PropertyGroup, Object, Image
from bpy.props import (
    IntProperty,
    StringProperty,
    PointerProperty,
    FloatProperty,
    EnumProperty,
    BoolProperty,
    CollectionProperty,
)

from .bakegroup import BakeGroup
from .effect import EffectProperty
from .baketarget import BakeTarget, BakeTargetMirrorEntry
from .animation import AnimationProperty, ExportAnimationJSONPathProperty

from ...utils.logging import log
from ...utils.constants import TARGET_UV_MAP
from ...utils.helpers import EnumDescriptor

BAKING_MODE = EnumDescriptor(
    ("COMBINED", "Combined", "Full bake", "", 0),
    ("DIFFUSE", "Color", "Color only bake", "", 1),
)


AVATAR_TYPE = EnumDescriptor(
    ("FLOATER", "Floater", "Export floater avatar", "", 0),
    ("FULLBODY", "Full body", "Export full body avatar", "", 1),
)


EXPORT_ANIMATION_SOURCE = EnumDescriptor(
    ("ACTION", "Export from Action", "Export animation from blender actions", "", 0),
    ("JSON", "Export from JSON", "Export animation from external JSON files", "", 1),
)


def update_atlas_size(self: "HomeomorphicProperties", context: Context) -> None:
    atlas_images = [im for im in bpy.data.images if "atlas_intermediate" in im.name]
    if atlas_images:
        ats = self.atlas_size
        for at in atlas_images:
            at.generated_color = (1.0, 1.0, 1.0, 1.0)
            if tuple(at.size) != (ats, ats):
                log.info(f"Resizing '{at.name}' from {tuple(at.size)} to {(ats, ats)}")
                if at.has_data:
                    at.scale(ats, ats)
                    at.update()


def update_debug_basis(HT: "HomeomorphicProperties", context: Context) -> None:
    HT.debug_animation_actions.clear()
    if basis := HT.debug_animation_avatar_basis:
        if metadata := basis.get("MorphSets_Avatar"):
            animation_meta = metadata["Animation"].to_dict()
            action_names = animation_meta["bone_transforms"].keys()
            for name in action_names:
                action = HT.debug_animation_actions.add()
                action.name = name
                action.checked = False


def update_export_progress(self: "HomeomorphicProperties", context: Context) -> None:
    # XXX Dirty Hack
    # bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
    pass


class HomeomorphicProperties(PropertyGroup):
    avatar_rig: PointerProperty(name="Avatar Rig", type=Object)  # type: ignore

    avatar_mesh: PointerProperty(name="Avatar Mesh", type=Object)  # type: ignore

    avatar_head_bone: StringProperty(  # type: ignore
        name="Head Bone", description="The bone to use for head transform calculation."
    )

    # Note that we use -1 to indicate that nothing is selected for integer selections
    effect_collection: CollectionProperty(type=EffectProperty)  # type: ignore

    selected_effect: IntProperty(name="Selected effect", default=-1)  # type: ignore

    bake_target_collection: CollectionProperty(type=BakeTarget)  # type: ignore

    selected_bake_target: IntProperty(name="Selected bake target", default=-1)  # type: ignore

    bake_target_mirror_collection: CollectionProperty(type=BakeTargetMirrorEntry)  # type: ignore

    selected_bake_target_mirror: IntProperty(name="Selected mirror entry", default=-1)  # type: ignore

    bake_group_collection: CollectionProperty(type=BakeGroup)  # type: ignore

    selected_bake_group: IntProperty(name="Selected bake group", default=-1)  # type: ignore

    source_object: StringProperty(name="Object name")  # type: ignore

    ### Atlas,textures, paint assist ###
    atlas_size: IntProperty(name="Atlas size", default=4096, update=update_atlas_size)  # type: ignore

    color_percentage: FloatProperty(name="Atlas color region percentage", default=25.0)  # type: ignore

    painting_size: IntProperty(name="Hand paint texture size", default=1024)  # type: ignore

    select_by_atlas_image: PointerProperty(name="Match atlas", type=Image)  # type: ignore

    ### Export options
    avatar_type: EnumProperty(items=tuple(AVATAR_TYPE), name="Avatar Type", default=1)  # type: ignore

    denoise: BoolProperty(name="Denoise Atlas", default=False)  # type: ignore

    export_atlas: BoolProperty(name="Export Atlas", default=True)  # type: ignore

    export_glb: BoolProperty(name="Export GLB", default=True)  # type: ignore

    export_animation: BoolProperty(name="Export Animation", default=False)  # type: ignore

    export_animation_source: EnumProperty(  # type: ignore
        items=tuple(EXPORT_ANIMATION_SOURCE), name="Export Source", default=0
    )

    export_animation_actions: CollectionProperty(type=AnimationProperty)  # type: ignore

    export_animation_json_paths: CollectionProperty(  # type: ignore
        name="JSON Paths", type=ExportAnimationJSONPathProperty
    )

    export_animation_preview: BoolProperty(  # type: ignore
        name="Export Animation Preview",
        default=False,
        description="Export an animation for preview",
    )

    export_progress: FloatProperty(  # type: ignore
        name="Export Progress",
        default=-1,
        subtype="PERCENTAGE",
        precision=1,
        min=-1,
        soft_min=0,
        soft_max=100,
        max=101,
        update=update_export_progress,
    )

    ### Baking options
    baking_target_uvmap: StringProperty(name="Bake UV map", default=TARGET_UV_MAP)  # type: ignore

    baking_options: EnumProperty(items=tuple(BAKING_MODE), name="Bake Mode", default=1)  # type: ignore

    ### Helpers Copy UV
    target_object_uv: PointerProperty(  # type: ignore
        name="Target", type=Object, description="Object to copy UV layers to"
    )

    source_object_uv: PointerProperty(  # type: ignore
        name="Source", type=Object, description="Object to copy UV layers from"
    )

    ### Debug bone animation
    debug_animation_show: BoolProperty(name="Show Debug Vis", default=False)  # type: ignore

    debug_animation_actions: CollectionProperty(type=AnimationProperty)  # type: ignore

    debug_animation_avatar_basis: PointerProperty(  # type: ignore
        name="Avatar Basis",
        type=Object,
        update=update_debug_basis,
        description="Avatar basis object with animation metadata",
    )

    ### Mirror Vertices Options
    mirror_distance: FloatProperty(  # type: ignore
        name="Mirror Distance",
        default=0.001,
        precision=4,
        description="Maximum distance to search for mirror a vertex",
    )

    mirror_verts_source: PointerProperty(  # type: ignore
        name="Mirror Source",
        type=Object,
        description="Object to copy vertex positions from",
    )

    mirror_verts_target: PointerProperty(  # type: ignore
        name="Mirror Target",
        type=Object,
        description="Object to copy vertex positions to",
    )

    ### Transfer Skin Weights Options
    transfer_skin_source: PointerProperty(  # type: ignore
        name="Transfer Source",
        type=Object,
        description="Object to copy vertex groups from",
    )

    transfer_skin_target: PointerProperty(  # type: ignore
        name="Transfer Target",
        type=Object,
        description="Object to copy vertex groups to",
    )

    def get_selected_effect(self) -> EffectProperty | None:
        if self.selected_effect:
            return self.effect_collection[self.selected_effect]
        return None

    def get_selected_bake_target(self) -> BakeTarget | None:
        if self.selected_bake_target != -1:
            return self.bake_target_collection[self.selected_bake_target]
        return None

    def get_selected_bake_group(self) -> BakeGroup | None:
        if self.selected_bake_group != -1:
            return self.bake_group_collection[self.selected_bake_group]
        return None

    def require_selected_bake_target(self) -> BakeTarget:
        if candidate := self.get_selected_bake_target():
            return candidate
        else:
            raise Exception()  # TODO - proper exception

    def get_selected_mirror(self) -> BakeTargetMirrorEntry | None:
        if self.selected_bake_target_mirror != -1:
            return self.bake_target_mirror_collection[self.selected_bake_target_mirror]
        return None

    def require_selected_mirror(self) -> BakeTargetMirrorEntry:
        if candidate := self.get_selected_mirror():
            return candidate
        else:
            raise Exception()  # TODO - proper exception

    def get_bake_target_index(self, target: BakeTarget) -> int:
        for index, bt in enumerate(self.bake_target_collection):
            if (
                bt == target
            ):  # note: We can't use identity comparison due to internal deferring
                # in blender
                return index
        return -1

    def export_progress_start(self) -> None:
        self.export_progress = 0

    def export_progress_end(self) -> None:
        self.export_progress = -1

    def export_progress_step(self, step: float) -> None:
        self.export_progress += step

    def should_export_animation_action(self) -> bool:
        return (
            str(self.avatar_type) == "FULLBODY"
            and self.export_animation
            and str(self.export_animation_source) == "ACTION"
        )

    def should_export_animation_json(self) -> bool:
        return (
            str(self.avatar_type) == "FULLBODY"
            and self.export_animation
            and str(self.export_animation_source) == "JSON"
        )
