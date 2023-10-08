import typing
from bpy.types import Object, Image, AnyType

from .bakegroup import BakeGroup
from .effect import EffectProperty
from .baketarget import BakeTarget, BakeTargetMirrorEntry
from .animation import AnimationProperty, ExportAnimationJSONPathProperty


class HomeomorphicProperties:
    avatar_rig: Object
    avatar_mesh: Object
    avatar_head_bone: str
    effect_collection: typing.Sequence[EffectProperty]
    selected_effect: int
    bake_target_collection: typing.Sequence[BakeTarget]
    selected_bake_target: int
    bake_target_mirror_collection: typing.Sequence[BakeTargetMirrorEntry]
    selected_bake_target_mirror: int
    bake_group_collection: typing.Sequence[BakeGroup]
    selected_bake_group: int
    source_object: str
    atlas_size: int
    color_percentage: float
    painting_size: int
    select_by_atlas_image: Image
    avatar_type: str
    denoise: bool
    export_atlas: bool
    export_glb: bool
    export_animation: str
    export_animation_source: str
    export_animation_actions: typing.Sequence[AnimationProperty]
    export_animation_json_paths: typing.Sequence[ExportAnimationJSONPathProperty]
    export_animation_preview: bool
    export_progress: float
    baking_target_uvmap: str
    baking_options: str
    target_object_uv: Object
    source_object_uv: Object
    debug_animation_show: bool
    debug_animation_actions: typing.Sequence
    debug_animation_avatar_basis: Object
    mirror_distance: float
    mirror_verts_source: Object
    mirror_verts_target: Object
    transfer_skin_source: Object
    transfer_skin_target: Object

    def as_any(self) -> AnyType:
        return typing.cast(AnyType, self)
