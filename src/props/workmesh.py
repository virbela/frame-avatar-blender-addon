from bpy.types import PropertyGroup
from bpy.props import StringProperty, EnumProperty

from .baketarget import UV_ISLAND_MODES
from .bakevariant import UV_TARGET_CHANNEL
from ..utils.constants import TARGET_UV_MAP

class WorkmeshProperty(PropertyGroup):
    parent_shapekey: StringProperty(
        name="Parent Shapekey",
        description="The shapekey used as the base for this workmesh",
    )
    
    source_uv_map: StringProperty(
        name="Source UV Map",
        default=TARGET_UV_MAP,
    )
    
    uv_mode: EnumProperty(
        items=tuple(UV_ISLAND_MODES), 
        name="UV island mode", 
        default=0
    )
    
    uv_channel: EnumProperty(
        items=tuple(UV_TARGET_CHANNEL), 
        name="UV target channel", 
        default=0
    )
