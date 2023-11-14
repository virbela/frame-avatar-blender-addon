import bpy
import typing 
from bpy.types import PropertyGroup, Object, Image
from bpy.props import (
    IntProperty,
    StringProperty,
    PointerProperty,
    FloatProperty,
    EnumProperty,
    BoolProperty,
    CollectionProperty,
)

from .bakevariant import BakeVariant
from ..utils.logging import log
from ..utils.constants import TARGET_UV_MAP
from ..utils.helpers import popup_message, get_named_entry, require_named_entry, EnumDescriptor



UV_ISLAND_MODES = EnumDescriptor(
    ("UV_IM_MONOCHROME", "Grayscale",     "This UV island will be channel packed to a grayscale segment of the atlas",
     "IMAGE_ZDEPTH",     0),

    ("UV_IM_COLOR",      "Color",         "This UV island will end up on the color segment of the atlas",
     "COLOR",            1),

    ("UV_IM_NIL",        "Nil UV island", "This UV island will have zero area (unshaded)",
     "DOT",              2),

    ("UV_IM_FROZEN",     "Frozen",        "This UV island will not be modified by the packer",
     "FREEZE",           3),
)

def get_baketarget_name(self: "BakeTarget"):
    return self.get("name", "Untitled bake target")


def set_baketarget_name(self: "BakeTarget", value: str):
    if not self.source_object:
        # Initial name set from the create bake targets operator
        self["name"] = value
        return

    # This is manual user name editing (remove leading "Avatar_")
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

    self["name"] = value
    log.info(f"Renaming baketarget to {value} ... ")


class BakeTarget(PropertyGroup):

    name: StringProperty(
        name = "Bake target name", 
        default="Untitled bake target", 
        get=get_baketarget_name, 
        set=set_baketarget_name
    )

    object_name: StringProperty(
        name = "Object name",
        description = "The object that is used for this bake target.\n"
                      "Once selected it is possible to select a specific shape key",
    )

    source_object: PointerProperty(
        name="Source object", 
        type=Object
    )

    shape_key_name: StringProperty(
        name="Shape key"
    )

    uv_area_weight: FloatProperty(
        name="UV island area weight", 
        default=1.0,
        min=0.0, 
        max=1.0
    )

    uv_mode: EnumProperty(
        items=tuple(UV_ISLAND_MODES), 
        name="UV island mode", 
        default=0
    )

    atlas: PointerProperty(
        name="Atlas image", 
        type=Image
    )

    source_uv_map: StringProperty(
        name="UV map", 
        default=TARGET_UV_MAP
    )

    multi_variants: BoolProperty(
        name="Multiple variants", 
        default=False
    )

    variant_collection: CollectionProperty(
        type=BakeVariant
    )

    selected_variant: IntProperty(
        name="Selected bake variant", 
        default=-1
    )

    # Flag export
    export: BoolProperty(name="Export Bake Target", default=True)

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
        return "untitled"

    def iter_bake_scene_variants(self) -> typing.Generator[tuple[str, BakeVariant], None, None]:
        prefix = self.name
        if self.multi_variants:
            for variant in self.variant_collection:
                yield f"{prefix}.{variant.name}", variant

    def iter_variants(self) -> typing.Generator[tuple[str, BakeVariant], None, None]:
        prefix = self.name
        for variant in self.variant_collection:
            if self.multi_variants:
                yield f"{prefix}.{variant.name}", variant
            else:
                yield f"{prefix}", variant

    def iter_bake_scene_variant_names(self) -> typing.Generator[str, None, None]:
        prefix = self.name
        if self.multi_variants:
            for variant in self.variant_collection:
                yield f"{prefix}.{variant.name}"
        else:
            yield prefix