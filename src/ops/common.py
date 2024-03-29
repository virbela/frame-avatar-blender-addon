from typing import Callable, Any
from bpy.types import CollectionProperty, Object, Context

from ..utils.properties import BakeVariant
from ..utils.constants import WORK_SCENE, BAKE_SCENE

class guarded_operator:
    def __init__(self, operator):
        self.operator = operator

    def __repr__(self):
        return f'<{self.__class__.__name__} of {self.operator}>'

    def __call__(self, *args, **kwargs):
        if self.operator.poll():
            return self.operator(*args, **kwargs)

class generic_list:
    'This is an abstract handler for list operations. The operations needs a collection and callables to get and set the current selection'

    @staticmethod
    def add(collection: CollectionProperty, get_selected: Any, set_selected: Any):
        new = collection.add()
        last_id = len(collection) - 1
        set_selected(last_id)
        return new

    @staticmethod
    def remove(collection: CollectionProperty, get_selected: Any, set_selected: Any):
        collection.remove(get_selected())
        last_id = len(collection) - 1
        if last_id == -1:
            set_selected(-1)
        else:
            set_selected(min(get_selected(), last_id))


def set_uv_map(obj: Object, uv_map: str):
    obj.data.uv_layers[uv_map].active = True

def copy_object(source_obj: Object, name: str) -> Object:
    new_object = source_obj.copy()
    new_object.data = source_obj.data.copy()	#Copy data as well
    new_object.name = name
    return new_object

def copy_collection(source: CollectionProperty, dest: CollectionProperty, transfer: Callable):
    while len(dest):
        dest.remove(0)

    for item in source:
        transfer(item, dest.add())

def transfer_variant(source: BakeVariant, dest: BakeVariant):
    dest.name = source.name
    dest.image = source.image
    dest.uv_map = source.uv_map

def poll_bake_scene(context: Context) -> bool:
    return context.scene.name == BAKE_SCENE

def poll_work_scene(context: Context) -> bool:
    return context.scene.name == WORK_SCENE

def poll_selected_objects(context: Context) -> bool:
    return context.selected_objects

def poll_baketargets(context: Context) -> bool:
    return  len(context.scene.homeomorphictools.bake_target_collection)

def poll_avatar_mesh(context: Context):
    return context.scene.homeomorphictools.avatar_mesh
