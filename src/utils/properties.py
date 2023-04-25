import bpy
import typing
from bpy.types import Context, Object, Image
from .helpers import (
    popup_message,
    enum_descriptor,
    get_named_entry,
    require_named_entry,
)

from .logging import log_writer as log
from .constants import MIRROR_TYPE, TARGET_UV_MAP

#Important notes
#    Regarding descriptions of properties, please see contribution note 1

#ISSUE-9: Not all properties have descriptions
#    Add descriptions for them
#    labels: needs-work

UV_ISLAND_MODES = enum_descriptor(

    #Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
    #(identifier,             name,                 description,
    #    icon,                 number),

    #NOTE - Suspecting the number is not needed, also since we use our own object to represent these values we could have the long column last and get a more
    #compact and nice table.

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

    #Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
    #(identifier,             name,                 description,
    #    icon,                 number),

    #NOTE - Suspecting the number is not needed, also since we use our own object to represent these values we could have the long column last and get a more
    #compact and nice table.

    ('UV_BM_REGULAR',        'Regular',            'This is a regular, non mirrored, bake target',
        'OBJECT_DATA',       0),

    ('UV_BM_MIRRORED',       'Mirrored',           'This bake target will be mirrored upon another target along the U axis',
        'MOD_MIRROR',        1),
)


UV_TARGET_CHANNEL = enum_descriptor(

    #Tuple layout - see https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
    #(identifier,             name,                 description,
    #    icon,                 number),

    #NOTE - Suspecting the number is not needed, also since we use our own object to represent these values we could have the long column last and get a more
    #compact and nice table.

    ('UV_TARGET_NIL',        'Unassigned',           'UV island has not yet been assigned an atlas channel',
        'DOT',               0),

    ('UV_TARGET_COLOR',      'Color channel',        'UV island will be placed in the color channel',
        'COLOR',             1),

    ('UV_TARGET_R',          'Red channel',          'UV island will be placed in the red channel',
        'EVENT_R',           2),

    ('UV_TARGET_G',          'Green channel',        'UV island will be placed in the green channel',
        'EVENT_G',           3),

    ('UV_TARGET_B',          'Blue channel',         'UV island will be placed in the blue channel',
        'EVENT_B',           4),
)


BAKING_MODE = enum_descriptor(
    ('COMBINED',       'Combined',          'Full bake',
        '',            0),

    ('DIFFUSE',        'Color',             'Color only bake',
        '',            1),

)


EFFECT_TYPE = enum_descriptor(
    ('POSITION',       'Position Effect',            'Effect to transform shape positions',
        '',            0),

    ('COLOR',          'Color Effect',               'Effect to override shape color',
        '',            1),

)


AVATAR_TYPE = enum_descriptor(
    ('FLOATER',        'Floater',              'Export floater avatar',
        '',            0),

    ('FULLBODY',       'Full body',            'Export full body avatar',
        '',            1),

)


ANIMATION_TYPE = enum_descriptor(
    ('VERTEX',         'Vertex',                'Export vertex animations (npy blobs)',
        '',            0),

    ('BONE',           'Bone',                  'Export bone animation.',
        '',            1),

)


def update_atlas(self: 'BakeVariant', context: Context):
    # when atlas is set, also set the uv_channel
    if self.intermediate_atlas:
        if 'red' in self.intermediate_atlas.name:
            self.uv_target_channel = 'UV_TARGET_R'
        elif 'green' in self.intermediate_atlas.name:
            self.uv_target_channel = 'UV_TARGET_G'
        elif 'blue' in self.intermediate_atlas.name:
            self.uv_target_channel = 'UV_TARGET_B'
        elif 'color' in self.intermediate_atlas.name:
            self.uv_target_channel = 'UV_TARGET_COLOR'
        else:
            self.uv_target_channel = 'UV_TARGET_NIL'


def get_bakevariant_name(self: 'BakeVariant'):
    return self.get("name", 'Untitled variant')


def set_bakevariant_name(self: 'BakeVariant', value: str):
    if not self.workmesh:
        self['name'] = value
        return

    # XXX THIS should only happen for multi variants
    # -- update workmesh name
    workmeshname = self.workmesh.name
    if '.' in workmeshname:
        target, _ = workmeshname.split('.')
        self.workmesh.name = f"{target}.{value}"

    self['name'] = value


class BakeVariant(bpy.types.PropertyGroup):
    name:                bpy.props.StringProperty(name="Variant name", default='Untitled variant', get=get_bakevariant_name, set=set_bakevariant_name)
    image:               bpy.props.PointerProperty(name="Image texture", type=bpy.types.Image)
    uv_map:              bpy.props.StringProperty(name="UV Map")

    workmesh:            bpy.props.PointerProperty(name='Work mesh', type=bpy.types.Object)

    #NOTE - we are not caring about target channel right now - we instead use intermediate_atlas
    uv_target_channel:   bpy.props.EnumProperty(items=tuple(UV_TARGET_CHANNEL), name="UV target channel", default=0)
    intermediate_atlas:  bpy.props.PointerProperty(name='Intermediate atlas', type=bpy.types.Image, update=update_atlas)


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

#FUTURE - we may want to use work meshes as the container for each bake target in the future so that we can easier deal with selections but now we want to just get the current structure working all the way
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

    def get_object(self) -> Object:
        return get_named_entry(bpy.data.objects, self.object_name)

    def require_object(self) -> Object:
        return require_named_entry(bpy.data.objects, self.object_name)

    def get_atlas(self) -> Image:
        return get_named_entry(bpy.data.images, self.atlas)

    def require_atlas(self) -> Image:
        return require_named_entry(bpy.data.images, self.atlas)

    @property
    def shortname(self) -> str:
        if self.object_name:
            if self.shape_key_name:
                return self.shape_key_name
            else:
                return self.object_name
        return 'untitled'


    def get_mirror_type(self, ht: 'HomeomorphicProperties') -> tuple['BakeTargetMirrorEntry', MIRROR_TYPE]:
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


class BakeTargetReference(bpy.types.PropertyGroup):
    target:             bpy.props.IntProperty(name='Bake target identifier', default=-1)


class BakeGroup(bpy.types.PropertyGroup):
    name:               bpy.props.StringProperty(name="Group name", default='Untitled group')
    members:            bpy.props.CollectionProperty(type = BakeTargetReference)
    selected_member:    bpy.props.IntProperty(name = "Selected bake target", default = -1)


class BakeTargetMirrorEntry(bpy.types.PropertyGroup):
    primary:            bpy.props.IntProperty(name='Primary bake target identifier', default=-1)
    secondary:          bpy.props.IntProperty(name='Secondary bake target identifier', default=-1)


def update_atlas_size(self, context: Context):
    atlas_images = [im for im in bpy.data.images if 'atlas_intermediate' in im.name]
    if atlas_images:
        ats = self.atlas_size
        for at in atlas_images:
            at.generated_color = (1.0, 1.0, 1.0, 1.0)
            if tuple(at.size) != (ats, ats):
                log.info(f"Resizing '{at.name}' from {tuple(at.size)} to {(ats, ats)}")
                if at.has_data:
                    at.scale(ats, ats)
                    at.update()


class PositionEffect(bpy.types.PropertyGroup):
    parent_shapekey:        bpy.props.StringProperty(
                                name="Parent Shapekey",
                                description="Shape key used as the relative key for this effect"
                            )
    effect_shapekey:        bpy.props.StringProperty(
                                name="Effect Shapekey",
                                description="Shape key with the final effect"
                            )


class ColorEffect(bpy.types.PropertyGroup):
    shape:                  bpy.props.StringProperty(name="Target Shapekey")
    color:                  bpy.props.FloatVectorProperty(name="Color", subtype='COLOR',
                                size = 4,
                                min = 0.0,
                                max = 1.0,
                                default = (1.0, 1.0, 1.0, 1.0)
                            )
    vert_group:             bpy.props.StringProperty(name="Vertex Group")


class EffectProperty(bpy.types.PropertyGroup):
    name:                   bpy.props.StringProperty(name="Effect Name", default='Untitled Effect')
    type:                   bpy.props.EnumProperty(items=tuple(EFFECT_TYPE), name="Effect Type")
    target:                 bpy.props.IntProperty(name='Effect identifier', default=-1)

    positions:              bpy.props.CollectionProperty(type = PositionEffect)
    colors:                 bpy.props.CollectionProperty(type = ColorEffect)


class ExportAnimationProperty(bpy.types.PropertyGroup):
    name:                   bpy.props.StringProperty(name="", default="")
    checked:                bpy.props.BoolProperty(name="", default=True)


class HomeomorphicProperties(bpy.types.PropertyGroup):

    ### Bake targets ###
    avatar_rig:                         bpy.props.PointerProperty(name='Avatar Rig', type=bpy.types.Object)
    avatar_mesh:                        bpy.props.PointerProperty(name='Avatar Mesh', type=bpy.types.Object)

    #Note that we use -1 to indicate that nothing is selected for integer selections
    effect_collection:                  bpy.props.CollectionProperty(type = EffectProperty)
    selected_effect:                    bpy.props.IntProperty(name = "Selected effect", default = -1)

    bake_target_collection:             bpy.props.CollectionProperty(type = BakeTarget)
    selected_bake_target:               bpy.props.IntProperty(name = "Selected bake target", default = -1)

    bake_target_mirror_collection:      bpy.props.CollectionProperty(type = BakeTargetMirrorEntry)
    selected_bake_target_mirror:        bpy.props.IntProperty(name = "Selected mirror entry", default = -1)

    bake_group_collection:              bpy.props.CollectionProperty(type = BakeGroup)
    selected_bake_group:                bpy.props.IntProperty(name = "Selected bake group", default = -1)

    source_object:                      bpy.props.StringProperty(name="Object name")

    ### Atlas,textures, paint assist ###
    atlas_size:                         bpy.props.IntProperty(name="Atlas size", default = 4096, update=update_atlas_size)
    color_percentage:                   bpy.props.FloatProperty(name="Atlas color region percentage", default = 25.0)
    painting_size:                      bpy.props.IntProperty(name="Hand paint texture size", default = 1024)
    select_by_atlas_image:              bpy.props.PointerProperty(name='Match atlas', type=bpy.types.Image)

    ### Export options
    avatar_type:                        bpy.props.EnumProperty(items=tuple(AVATAR_TYPE), name="Avatar Type", default=1)
    animation_type:                     bpy.props.EnumProperty(items=tuple(ANIMATION_TYPE), name="Animation Type", default=1)
    denoise:                            bpy.props.BoolProperty(name="Denoise Atlas", default=False)
    export_atlas:                       bpy.props.BoolProperty(name="Export Atlas", default=True)
    export_glb:                         bpy.props.BoolProperty(name="Export GLB", default=True)
    export_animation:                   bpy.props.BoolProperty(name="Export Animation", default=True)
    export_animation_actions:           bpy.props.CollectionProperty(type=ExportAnimationProperty)

    ### Baking options
    baking_target_uvmap:                bpy.props.StringProperty(name="Bake UV map", default=TARGET_UV_MAP)
    baking_options:                     bpy.props.EnumProperty(items=tuple(BAKING_MODE), name="Bake Mode", default=1)

    ### Helpers Copy UV
    target_object_uv:                   bpy.props.PointerProperty(name="Target", type=bpy.types.Object, description="Object to copy UV layers to")
    source_object_uv:                   bpy.props.PointerProperty(name="Source", type=bpy.types.Object, description="Object to copy UV layers from")

    ### Debug bone animation
    debug_animation_show:               bpy.props.BoolProperty(name="Show Debug Vis", default=False)
    debug_animation_name:               bpy.props.StringProperty(name="Action", default="")

    ### Mirror Vertices Options
    mirror_distance:                    bpy.props.FloatProperty(name="Mirror Distance", default=0.001, precision=4, description="Maximum distance to search for mirror a vertex")
    mirror_verts_source:                bpy.props.PointerProperty(name="Mirror Source", type=bpy.types.Object, description="Object to copy vertex positions from.")
    mirror_verts_target:                bpy.props.PointerProperty(name="Mirror Target", type=bpy.types.Object, description="Object to copy vertex positions to.")

    def get_selected_effect(self) -> EffectProperty:
        if self.selected_effect:
            return self.effect_collection[self.selected_effect]

    def get_selected_bake_target(self) -> BakeTarget:
        if self.selected_bake_target != -1:
            return self.bake_target_collection[self.selected_bake_target]

    def get_selected_bake_group(self) -> BakeGroup:
        if self.selected_bake_group != -1:
            return self.bake_group_collection[self.selected_bake_group]

    def require_selected_bake_target(self) -> BakeTarget:
        if candidate := self.get_selected_bake_target():
            return candidate
        else:
            raise Exception()    #TODO - proper exception

    def get_selected_mirror(self) -> BakeTargetMirrorEntry:
        if self.selected_bake_target_mirror != -1:
            return self.bake_target_mirror_collection[self.selected_bake_target_mirror]

    def require_selected_mirror(self) -> BakeTargetMirrorEntry:
        if candidate := self.get_selected_mirror():
            return candidate
        else:
            raise Exception()    #TODO - proper exception

    def get_bake_target_index(self, target: BakeTarget) -> int:
        for index, bt in enumerate(self.bake_target_collection):
            if bt == target:    # note: We can't use identity comparison due to internal deferring in blender
                return index
        return -1


class UIStateProperty(bpy.types.PropertyGroup):
    workflow_introduction_visible:      bpy.props.BoolProperty(default=True)
    workflow_bake_targets_visible:      bpy.props.BoolProperty(default=True)
    workflow_work_meshes_visible:       bpy.props.BoolProperty(default=False)
    workflow_texture_atlas_visible:     bpy.props.BoolProperty(default=False)
    workflow_work_materials_visible:    bpy.props.BoolProperty(default=False)
    workflow_baking_visible:            bpy.props.BoolProperty(default=False)
    workflow_helpers_visible:           bpy.props.BoolProperty(default=False)


classes = (
    BakeTargetReference,
    BakeGroup,

    BakeTargetMirrorEntry,
    BakeVariant,
    BakeTarget,

    ColorEffect,
    PositionEffect,
    EffectProperty,

    UIStateProperty,
    ExportAnimationProperty,
    HomeomorphicProperties,
)

register, unregister = bpy.utils.register_classes_factory(classes)


def register_props():
    register()

    bpy.types.Scene.ui_state = bpy.props.PointerProperty(type=UIStateProperty)
    bpy.types.Scene.homeomorphictools = bpy.props.PointerProperty(type=HomeomorphicProperties)



def unregister_props():
    del bpy.types.Scene.ui_state
    del bpy.types.Scene.homeomorphictools

    unregister()