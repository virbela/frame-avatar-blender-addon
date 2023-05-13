import bpy
import typing 
from typing import TYPE_CHECKING


from .bakevariant import BakeVariant
from ..utils.logging import log_writer as log
from ..utils.constants import MIRROR_TYPE, TARGET_UV_MAP
from ..utils.helpers import popup_message, get_named_entry, require_named_entry, enum_descriptor


if TYPE_CHECKING:
    from .homeomorphic import HomeomorphicProperties


UV_ISLAND_MODES = enum_descriptor(
    ('UV_IM_MONOCHROME',    'Grayscale',        'This UV island will be channel packed to a grayscale segment of the atlas',
        'IMAGE_ZDEPTH',     0),

    ('UV_IM_COLOR',         'Color',            'This UV island will end up on the color segment of the atlas',
        'COLOR',            1),

    ('UV_IM_NIL',           'Nil UV island',    'This UV island will have zero area (unshaded)',
        'DOT',              2),

    ('UV_IM_FROZEN',        'Frozen',           'This UV island will not be modified by the packer',
        'FREEZE',           3),
)


UV_BAKE_MODE = enum_descriptor(
    ('UV_BM_REGULAR',        'Regular',            'This is a regular, non mirrored, bake target',
        'OBJECT_DATA',       0),

    ('UV_BM_MIRRORED',       'Mirrored',           'This bake target will be mirrored upon another target along the U axis',
        'MOD_MIRROR',        1),
)


class BakeTargetMirrorEntry(bpy.types.PropertyGroup):
    primary:            bpy.props.IntProperty(name='Primary bake target identifier', default=-1)
    secondary:          bpy.props.IntProperty(name='Secondary bake target identifier', default=-1)


def get_baketarget_name(self: 'BakeTarget'):
    return self.get("name", 'Untitled bake target')


def set_baketarget_name(self: 'BakeTarget', value: str):
    if not self.source_object:
        # Initial name set from the create bake targets operator
        self['name'] = value
        return

    # This is manual user name editing (remove leading 'Avatar_')
    newname = value.lstrip(f"{self.source_object.name}_")

    # -- rename shapekey
    keys = self.source_object.data.shape_keys.key_blocks
    shapekey = keys.get(self.shape_key_name)
    if not shapekey:
        # -- error shapekey was not found
        popup_message(f"Shapekey {self.shape_key_name} was not found!", "ShapekeyError")
        return
    shapekey.name = newname
    self.shape_key_name = newname

    # for each variant in this bake target
    # -- rename workmesh
    for variant in self.variant_collection:
        variantname = newname
        if self.multi_variants:
            variantname = f"{newname}.{variant.name}"
        if variant.workmesh:
            variant.workmesh.name = variantname

    self['name'] = value
    log.info(f"Renaming baketarget to {value} ... ")


class BakeTarget(bpy.types.PropertyGroup):

    name:                 bpy.props.StringProperty(
                            name = "Bake target name", default='Untitled bake target', 
                            get=get_baketarget_name, set=set_baketarget_name
                        )

    object_name:          bpy.props.StringProperty(
                            name = "Object name",
                            description = "The object that is used for this bake target.\n"
                                          "Once selected it is possible to select a specific shape key",
                        )

    # source info
    source_object:        bpy.props.PointerProperty(name='Source object', type=bpy.types.Object)
    shape_key_name:       bpy.props.StringProperty(name="Shape key")

    uv_area_weight:       bpy.props.FloatProperty(
                            name="UV island area weight", default=1.0,
                            min=0.0, max=1.0
                          )

    bake_mode:            bpy.props.EnumProperty(items=tuple(UV_BAKE_MODE), name="UV bake mode", default=0)

    mirror_source:        bpy.props.IntProperty(name='Bake target used for mirror')

    uv_mode:              bpy.props.EnumProperty(items=tuple(UV_ISLAND_MODES), name="UV island mode", default=0)
    atlas:                bpy.props.PointerProperty(name="Atlas image", type=bpy.types.Image)
    # ↑ This is used for storing the automatic choice as well as the manual (frozen) one

    #TBD - use this? - yes we need UV map for when rescaling from source
    source_uv_map:        bpy.props.StringProperty(name="UV map", default=TARGET_UV_MAP)


    #Variants
    multi_variants:       bpy.props.BoolProperty(name="Multiple variants", default=False)
    variant_collection:   bpy.props.CollectionProperty(type = BakeVariant)
    selected_variant:     bpy.props.IntProperty(name = "Selected bake variant", default = -1)

    # Flag export
    export:                            bpy.props.BoolProperty(name="Export Bake Target", default=True)

    def get_object(self) -> bpy.types.Object:
        return get_named_entry(bpy.data.objects, self.object_name)

    def require_object(self) -> bpy.types.Object:
        return require_named_entry(bpy.data.objects, self.object_name)

    def get_atlas(self) -> bpy.types.Image:
        return get_named_entry(bpy.data.images, self.atlas)

    def require_atlas(self) -> bpy.types.Image:
        return require_named_entry(bpy.data.images, self.atlas)

    @property
    def shortname(self) -> str:
        if self.object_name:
            if self.shape_key_name:
                return self.shape_key_name
            else:
                return self.object_name
        return 'untitled'


    def get_mirror_type(self, ht: 'HomeomorphicProperties') -> tuple[BakeTargetMirrorEntry, MIRROR_TYPE]:
        find_id = ht.get_bake_target_index(self)
        for mirror in ht.bake_target_mirror_collection:
            if find_id == mirror.primary:
                return mirror, MIRROR_TYPE.PRIMARY
            elif find_id == mirror.secondary:
                return mirror, MIRROR_TYPE.SECONDARY

        return None, None

    #NOTE we should probably deprecate this in favor of iter_variants
    # this doesn't yield anything if there are no variants
    def iter_bake_scene_variants(self) -> typing.Generator[tuple[str, BakeVariant], None, None]:
        prefix = self.name # self.get_bake_scene_name()
        if self.multi_variants:
            for variant in self.variant_collection:
                yield f'{prefix}.{variant.name}', variant


    #TODO - use a helper function for creating names
    def iter_variants(self) -> typing.Generator[tuple[str, BakeVariant], None, None]:
        prefix = self.name # self.get_bake_scene_name()
        for variant in self.variant_collection:
            if self.multi_variants:
                yield f'{prefix}.{variant.name}', variant
            else:
                yield f'{prefix}', variant


    def iter_bake_scene_variant_names(self) -> typing.Generator[str, None, None]:
        prefix = self.name # self.get_bake_scene_name()
        if self.multi_variants:
            for variant in self.variant_collection:
                yield f'{prefix}.{variant.name}'
        else:
            yield prefix
