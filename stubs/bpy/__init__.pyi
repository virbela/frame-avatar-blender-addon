import sys
import typing
import bpy.types

from bpy import types
from bpy import ops
from bpy import msgbus
from bpy import utils
from bpy import path
from bpy import app
from bpy import props

GenericType = typing.TypeVar("GenericType")
context: 'bpy.types.Context' = None

data: 'bpy.types.BlendData' = None
''' Access to Blender's internal data
'''
