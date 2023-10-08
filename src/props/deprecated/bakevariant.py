from bpy.types import Context, Object, Image, PropertyGroup
from bpy.props import StringProperty, PointerProperty, EnumProperty

from ...utils.helpers import EnumDescriptor


UV_TARGET_CHANNEL = EnumDescriptor(
    (
        "UV_TARGET_NIL",
        "Unassigned",
        "UV island has not yet been assigned an atlas channel",
        "DOT",
        0,
    ),
    (
        "UV_TARGET_COLOR",
        "Color channel",
        "UV island will be placed in the color channel",
        "COLOR",
        1,
    ),
    (
        "UV_TARGET_R",
        "Red channel",
        "UV island will be placed in the red channel",
        "EVENT_R",
        2,
    ),
    (
        "UV_TARGET_G",
        "Green channel",
        "UV island will be placed in the green channel",
        "EVENT_G",
        3,
    ),
    (
        "UV_TARGET_B",
        "Blue channel",
        "UV island will be placed in the blue channel",
        "EVENT_B",
        4,
    ),
)


def update_atlas(self: "BakeVariant", context: Context):
    # when atlas is set, also set the uv_channel
    if self.intermediate_atlas:
        if "red" in self.intermediate_atlas.name:
            self.uv_target_channel = "UV_TARGET_R"
        elif "green" in self.intermediate_atlas.name:
            self.uv_target_channel = "UV_TARGET_G"
        elif "blue" in self.intermediate_atlas.name:
            self.uv_target_channel = "UV_TARGET_B"
        elif "color" in self.intermediate_atlas.name:
            self.uv_target_channel = "UV_TARGET_COLOR"
        else:
            self.uv_target_channel = "UV_TARGET_NIL"


def get_bakevariant_name(self: "BakeVariant"):
    return self.get("name", "Untitled variant")


def set_bakevariant_name(self: "BakeVariant", value: str):
    if not self.workmesh:
        self["name"] = value
        return

    # XXX THIS should only happen for multi variants
    # -- update workmesh name
    workmeshname = self.workmesh.name
    if "." in workmeshname:
        target, _ = workmeshname.split(".")
        self.workmesh.name = f"{target}.{value}"

    self["name"] = value


class BakeVariant(PropertyGroup):
    name: StringProperty(
        name="Variant name",
        default="Untitled variant",
        get=get_bakevariant_name,
        set=set_bakevariant_name,
    )

    image: PointerProperty(name="Image texture", type=Image)

    uv_map: StringProperty(name="UV Map")

    workmesh: PointerProperty(name="Work mesh", type=Object)

    uv_target_channel: EnumProperty(
        items=tuple(UV_TARGET_CHANNEL), name="UV target channel", default=0
    )

    intermediate_atlas: PointerProperty(
        name="Intermediate atlas", type=Image, update=update_atlas
    )
