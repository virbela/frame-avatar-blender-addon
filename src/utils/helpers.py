import io
import bpy
import enum
import uuid
import types
import bmesh
import pstats
import typing
import cProfile
import threading
import addon_utils
from typing import TYPE_CHECKING
from dataclasses import dataclass
from contextlib import contextmanager
from bpy.types import bpy_struct, Context, Scene, bpy_prop_collection, Object, Preferences

from .logging import log_writer as log
from .constants import BAKE_SCENE, WORK_SCENE
from .exceptions import InternalError, FrameException

# controllers.py

if TYPE_CHECKING:
    from .properties import HomeomorphicProperties, BakeTarget, BakeVariant

pending_classes = list()

def IMPLEMENTATION_PENDING(*p, **n):
    raise InternalError(f'This feature is not implemented! (arguments: {p} {n})')


@contextmanager
def profile():
    s = io.StringIO()
    pr = cProfile.Profile()

    pr.enable()
    yield
    pr.disable()

    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs()
    ps.sort_stats('time')
    ps.print_stats()

    print(s.getvalue())


def register_class(cls: bpy_struct) -> bpy_struct:
    pending_classes.append(cls)
    return cls

class missing_action(enum.Enum):
    FAIL = object()
    RETURN_NONE = object()


class named_entry_action(enum.Enum):
    RENAME = enum.auto()
    RECREATE = enum.auto()
    GET_EXISTING = enum.auto()

@dataclass
class enum_entry:
    identifier: str
    name: str
    description: str
    icon: str
    number: int

class enum_descriptor:
    def __init__(self, *entries):
        self.members = {ee.identifier:ee for ee in (enum_entry(*e) for e in entries)}
        self.by_value = {ee.number: ee for ee in self.members.values()}

    def __iter__(self):
        for member in self.members.values():
            yield (member.identifier, member.name, member.description, member.icon, member.number)


class frame_property_group(bpy.types.PropertyGroup):
    #contribution note 6B
    def __init_subclass__(cls):
        pending_classes.append(cls)

    def get_properties_by_names(self, names: str, if_missing: missing_action = missing_action.FAIL) -> typing.Any:
        'Takes list of names separated by space and yields the values of those members.'

        if if_missing is missing_action.FAIL:
            return (getattr(self, member) for member in names.split())
        elif if_missing is missing_action.RETURN_NONE:
            return (getattr(self, member, None) for member in names.split())
        else:
            raise ValueError(f'if_missing has unknown value')


def require_work_scene(context: Context) -> Scene:
    if scene := bpy.data.scenes.get(WORK_SCENE):
        return scene

    log.error(f'Work scene `{WORK_SCENE}` could not be found.')


def require_bake_scene(context: Context) -> Scene:
    if scene := bpy.data.scenes.get(BAKE_SCENE):
        return scene

    return bpy.data.scenes.new(BAKE_SCENE)


def get_homeomorphic_tool_state(context: Context) -> 'HomeomorphicProperties':
    if work_scene := require_work_scene(context):
        return work_scene.homeomorphictools

    raise InternalError("Work scene not Found.")


def get_named_entry(collection: bpy_prop_collection, name: str) -> typing.Any:
    return collection.get(name)


def require_named_entry(collection: bpy_prop_collection, name: str):
    if not name:
        raise FrameException.NoNameGivenForCollectionLookup(collection)

    if candidate := collection.get(name):
        return candidate
    else:
        raise FrameException.NamedEntryNotFound(collection, name)


def create_named_entry(collection: bpy_prop_collection, name: str, *positional, action: named_entry_action = named_entry_action.GET_EXISTING) -> typing.Any:

    if name in collection:
        if action == named_entry_action.RECREATE:
            collection.remove(collection.get(name))
            return collection.new(name, *positional)
        elif action == named_entry_action.GET_EXISTING:
            return collection.get(name)
        elif action == named_entry_action.RENAME:
            return collection.new(name, *positional)
        else:
            raise FrameException.FailedToCreateNamedEntry(collection, name)

    return collection.new(name, *positional)


#ISSUE-12: Context handling
#	When modifying the context by switching scene or updating view layers we leave things in a different state than we found it.
#	Either we need to make sure we override the context properly (if this is possible with stuff like view layer configurations and such)
#	or we have to keep track of our changes that we want reverted and what changes we want to keep (like with paint assist we may actually want to change the state).
#	labels: needs-work, needs-research

def set_scene(context: Context, scene: Scene):
    context.window.scene = scene


def set_selection(collection: list, *selected, synchronize_active: bool = False, make_sure_active: bool = False):
    new_selection = set(selected)

    for item in collection:
        #NOTE There are two APIs to select things, we will favor the setter since that seems the be most recent
        if setter := getattr(item, 'select_set', None):
            setter(item in new_selection)
        else:
            item.select = item in new_selection

    # if there is an active element in this collection and it is not selected, we deactivate it if synchronize_active is set
    if synchronize_active and collection.active not in new_selection:
        collection.active = None

    # select first if make_sure_active is set and there is no active object
    if make_sure_active and collection.active is None and selected:
        collection.active = selected[0]


def clear_selection(collection: list):
    set_selection(collection)


def set_active(collection: bpy_prop_collection, item: Object):
    collection.active = item


def clear_active(collection: bpy_prop_collection):
    collection.active = None


def set_rendering(collection: bpy_prop_collection, *selected, synchronize_active: bool = False, make_sure_active: bool = False):
    'Replaces current rendering selection'
    new_selection = set(selected)

    for item in collection:
        item.hide_render = item not in new_selection

    # if there is an active element in this collection and it is not selected, we deactivate it if synchronize_active is set
    if synchronize_active and collection.active not in new_selection:
        collection.active = None

    # select first if make_sure_active is set and there is no active object
    if make_sure_active and collection.active is None and selected:
        collection.active = selected[0]


#NOTE - was going to use https://docs.python.org/3/library/operator.html#operator.attrgetter but there is no attrsetter so we'll just define both for consistency
class attribute_reference:
    def __init__(self, target, attribute):
        self.target = target
        self.attribute = attribute

class a_get(attribute_reference):
    def __call__(self):
        return getattr(self.target, self.attribute)

class a_set(attribute_reference):
    def __call__(self, value):
        return setattr(self.target, self.attribute, value)


def get_nice_name(collection: list, prefix: str, max_prefix_length: int, random_hash_length: int = 8, max_tries: int = 1000):

    for v in range(max_tries):
        tail = f'-{v:03}' if v else ''
        candidate = f'{prefix[:max_prefix_length]}{tail}'
        if candidate not in collection:
            return candidate

    raise Exception(f'Failed to create name for {prefix}')


def is_reference_valid(target: typing.Any) -> bool:
    try:
        target.name
        return True
    except ReferenceError:
        return False


class UUID_manager:
    def __init__(self, key):
        self.key = key
        self.uuid_map = dict()
        self.lock = threading.Lock()

    def validate(self):
        to_discard = [key for key, value in self.uuid_map.items() if not is_reference_valid(value)]
        for key in to_discard:
            del self.uuid_map[key]

        for key, value in self.uuid_map.items():
            if self.uuid_map.get(key) is not value:
                log.warning('UUID connection was broken')

    def register(self, obj, auto_fix=True):
        with self.lock:
            if existing_uuid := obj.get(self.key, ''):
                if self.uuid_map.get(existing_uuid) is not obj:
                    if auto_fix:
                        self.uuid_map[existing_uuid] = obj
                        log.debug('Updated incorrect UUID')
                    else:
                        raise Exception('UUID does not match')
                return existing_uuid
            else:
                while True:
                    candidate = str(uuid.uuid4())
                    if candidate not in self.uuid_map:
                        self.uuid_map[candidate] = obj
                        obj[self.key] = candidate
                        return candidate


def get_bake_target_variant_name(bake_target: 'BakeTarget', variant: 'BakeVariant'):
    if bake_target.multi_variants:
        return f'{bake_target.shortname}.{variant.name}'
    return f'{bake_target.shortname}'


def purge_object(obj: Object):
    bpy.data.objects.remove(obj)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def is_dev() -> bool:
    # if we are installed as an addon, assume this is a production dist
    for mod in addon_utils.modules():
        if 'frame_avatar_addon' == mod.__name__:
            return False
    return True


def get_prefs() -> typing.Union[Preferences, types.SimpleNamespace]:
    try:
        preferences = bpy.context.preferences.addons[__package__].preferences
    except KeyError:
        # XXX DEV(simulate preferences)
        preferences = types.SimpleNamespace()
        preferences.log_target = "devlog"
        preferences.glb_export_dir = ""
        preferences.atlas_export_dir = ""
        preferences.custom_frame_validation = True
    return preferences


def popup_message(message: str, title: str = "Error", icon: str = "ERROR"):
    def oops(self, context: Context):
        self.layout.label(text=message)

    if bpy.app.background:
        log.info(message)
        return

    bpy.context.window_manager.popup_menu(oops, title=title, icon=icon)


def ensure_applied_rotation(object: Object):
    "Ensure obj has rotation applied"
    rot = object.rotation_euler
    if (rot.x, rot.y, rot.z) == (0, 0, 0):
        # -- rotation already applied
        return

    bm = bmesh.new()
    bm.from_mesh(object.data)
    for v in bm.verts:
        v.co = object.matrix_world @ v.co
    bm.to_mesh(object.data)
    bm.free()
    object.rotation_euler = (0, 0, 0)
