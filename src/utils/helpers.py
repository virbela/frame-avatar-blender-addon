import io
import bpy
import json
import enum
import uuid
import types
import bmesh
import pstats
import typing
import cProfile
import threading
import addon_utils
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from contextlib import contextmanager
from typing import TYPE_CHECKING, Tuple
from bpy.types import (
    Context,
    Scene,
    Menu,
    bpy_prop_collection,
    Object,
    AddonPreferences,
    Mesh,
    Action,
    ObjectBase,
)

from .logging import log
from .constants import BAKE_SCENE, WORK_SCENE
from .exceptions import InternalError, FrameException

T = typing.TypeVar("T")

if TYPE_CHECKING:
    from ..props import HomeomorphicProperties, BakeTarget, BakeVariant


def IMPLEMENTATION_PENDING(*p: typing.Any, **n: typing.Any) -> None:
    raise InternalError(f"This feature is not implemented! (arguments: {p} {n})")


PREFS_LOG = True


@contextmanager
def profile() -> typing.Generator[None, None, None]:
    s = io.StringIO()
    pr = cProfile.Profile()

    pr.enable()
    yield
    pr.disable()

    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs()
    ps.sort_stats("time")
    ps.print_stats()

    print(s.getvalue())


class MissingAction(enum.Enum):
    FAIL = object()
    RETURN_NONE = object()


class NamedEntryAction(enum.Enum):
    RENAME = enum.auto()
    RECREATE = enum.auto()
    GET_EXISTING = enum.auto()


@dataclass
class EnumEntry:
    identifier: str
    name: str
    description: str
    icon: str
    number: int


class EnumDescriptor:
    def __init__(self, *entries: typing.Tuple[str, str, str, str, int]) -> None:
        self.members = {ee.identifier: ee for ee in (EnumEntry(*e) for e in entries)}
        self.by_value = {ee.number: ee for ee in self.members.values()}

    def __iter__(
        self,
    ) -> typing.Generator[typing.Tuple[str, str, str, str, int], None, None]:
        for member in self.members.values():
            yield (
                member.identifier,
                member.name,
                member.description,
                member.icon,
                member.number,
            )


def require_work_scene() -> Scene:
    if scene := bpy.data.scenes.get(WORK_SCENE):
        return scene

    log.error(f"Work scene `{WORK_SCENE}` could not be found.")


def require_bake_scene() -> Scene:
    if scene := bpy.data.scenes.get(BAKE_SCENE):
        return scene

    return bpy.data.scenes.new(BAKE_SCENE)


def get_homeomorphic_tool_state(context: Context) -> "HomeomorphicProperties":
    scene = require_work_scene()
    return scene.homeomorphictools


def get_named_entry(collection: bpy_prop_collection[T], name: str) -> T:
    return collection.get(name)


def require_named_entry(collection: bpy_prop_collection[T], name: str) -> T:
    if not name:
        raise FrameException.NoNameGivenForCollectionLookup(collection)

    if candidate := collection.get(name):
        return candidate
    else:
        raise FrameException.NamedEntryNotFound(collection, name)


def create_named_entry(
    collection: bpy_prop_collection[T],
    name: str,
    *positional: typing.Any,
    action: NamedEntryAction = NamedEntryAction.GET_EXISTING,
) -> typing.Any:
    if name in collection:
        if action == NamedEntryAction.RECREATE:
            collection.remove(collection.get(name))
            return collection.new(name, *positional)
        elif action == NamedEntryAction.GET_EXISTING:
            return collection.get(name)
        elif action == NamedEntryAction.RENAME:
            return collection.new(name, *positional)
        else:
            raise FrameException.FailedToCreateNamedEntry(collection, name)

    return collection.new(name, *positional)


def set_scene(context: Context, scene: Scene) -> None:
    context.window.scene = scene


def set_selection(
    collection: list[ObjectBase],
    *selected: list[T],
    synchronize_active: bool = False,
    make_sure_active: bool = False,
) -> None:
    new_selection = set(selected)

    for item in collection:
        # NOTE There are two APIs to select things, we will favor the setter
        # since that seems the be most recent
        if setter := getattr(item, "select_set", None):
            setter(item in new_selection)
        else:
            item.select = item in new_selection

    # if there is an active element in this collection and it is not selected,
    # we deactivate it if synchronize_active is set
    if synchronize_active and collection.active not in new_selection:
        collection.active = None

    # select first if make_sure_active is set and there is no active object
    if make_sure_active and collection.active is None and selected:
        collection.active = selected[0]


def clear_selection(collection: list) -> None:
    set_selection(collection)


def set_active(collection: bpy_prop_collection, item: Object) -> None:
    collection.active = item


def clear_active(collection: bpy_prop_collection) -> None:
    collection.active = None


def set_rendering(
    collection: bpy_prop_collection[T],
    *selected: bpy_prop_collection[T],
    synchronize_active: bool = False,
    make_sure_active: bool = False,
) -> None:
    new_selection = set(selected)

    for item in collection:
        item.hide_render = item not in new_selection

    # if there is an active element in this collection and it is not selected,
    # we deactivate it if synchronize_active is set
    if synchronize_active and collection.active not in new_selection:
        collection.active = None

    # select first if make_sure_active is set and there is no active object
    if make_sure_active and collection.active is None and selected:
        collection.active = selected[0]


class AttributeReference:
    def __init__(self, target: T, attribute: str) -> None:
        self.target = target
        self.attribute = attribute


class AttrGet(AttributeReference):
    def __call__(self) -> typing.Any:
        return getattr(self.target, self.attribute)


class AttrSet(AttributeReference):
    def __call__(self, value: typing.Any) -> None:
        return setattr(self.target, self.attribute, value)


def get_nice_name(
    collection: typing.Iterable[T],
    prefix: str,
    max_prefix_length: int,
    random_hash_length: int = 8,
    max_tries: int = 1000,
) -> str:
    for v in range(max_tries):
        tail = f"-{v:03}" if v else ""
        candidate = f"{prefix[:max_prefix_length]}{tail}"
        if candidate not in collection:
            return candidate

    raise Exception(f"Failed to create name for {prefix}")


def is_reference_valid(target: typing.Any) -> bool:
    try:
        target.name
        return True
    except ReferenceError:
        return False


class UUIDManager:
    def __init__(self, key: str) -> None:
        self.key = key
        self.uuid_map: typing.Dict[str, Object] = dict()
        self.lock = threading.Lock()

    def validate(self) -> None:
        to_discard = [
            key for key, value in self.uuid_map.items() if not is_reference_valid(value)
        ]
        for key in to_discard:
            del self.uuid_map[key]

        for key, value in self.uuid_map.items():
            if self.uuid_map.get(key) is not value:
                log.warning("UUID connection was broken")

    def register(self, obj: Object, auto_fix=True) -> str:
        with self.lock:
            if existing_uuid := obj.get(self.key, ""):
                if self.uuid_map.get(existing_uuid) is not obj:
                    if auto_fix:
                        self.uuid_map[existing_uuid] = obj
                        log.debug("Updated incorrect UUID")
                    else:
                        raise Exception("UUID does not match")
                return existing_uuid
            else:
                while True:
                    candidate = str(uuid.uuid4())
                    if candidate not in self.uuid_map:
                        self.uuid_map[candidate] = obj
                        obj[self.key] = candidate
                        return candidate


def get_bake_target_variant_name(
    bake_target: "BakeTarget", variant: "BakeVariant"
) -> str:
    if bake_target.multi_variants:
        return f"{bake_target.shortname}.{variant.name}"
    return f"{bake_target.shortname}"


def purge_object(obj: Object) -> None:
    bpy.data.objects.remove(obj)
    for me in bpy.data.meshes:
        if me.users == 0:
            bpy.data.meshes.remove(me)

    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)


def is_dev() -> bool:
    # if we are installed as an addon, assume this is a production dist
    for mod in addon_utils.modules():
        if "frame_avatar_addon" == mod.__name__:
            return False
    return True


def get_prefs() -> typing.Union[AddonPreferences, types.SimpleNamespace]:
    global PREFS_LOG
    preferences: typing.Union[AddonPreferences, types.SimpleNamespace]
    try:
        preferences = bpy.context.preferences.addons[__package__].preferences
    except KeyError:
        # XXX DEV(simulate preferences)
        preferences = types.SimpleNamespace(
            log_target="",
            npy_export_dir="",
            glb_export_dir="",
            atlas_export_dir="",
            custom_frame_validation=True,
        )
        # -- check for .env.json to load dev frame dirs
        env_file = Path(__file__).parent.parent.parent.joinpath(".env.json").absolute()
        if env_file.exists():
            with open(env_file, "r") as file:
                data = json.load(file)
                glb_folder = data["frame_glb_folder"]
                if Path(glb_folder).exists():
                    preferences.glb_export_dir = glb_folder
                    if PREFS_LOG:
                        log.info(f"GLB Export dir set to {glb_folder}")
                atlas_folder = data["frame_atlas_folder"]
                if Path(atlas_folder).exists():
                    preferences.atlas_export_dir = atlas_folder
                    if PREFS_LOG:
                        log.info(f"Atlas Export dir set to {atlas_folder}")
                npy_folder = data["frame_npy_folder"]
                if Path(npy_folder).exists():
                    preferences.npy_export_dir = npy_folder
                    if PREFS_LOG:
                        log.info(f"Npy Export dir set to {npy_folder}")

    PREFS_LOG = False
    return preferences


def popup_message(message: str, title: str = "Error", icon: str = "ERROR") -> None:
    def oops(self: Menu, context: Context) -> None:
        self.layout.label(text=message)

    if bpy.app.background:
        log.info(message)
        return

    bpy.context.window_manager.popup_menu(oops, title=title, icon=icon)


def ensure_applied_rotation(object: Object) -> None:
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


def get_gltf_export_indices(obj: Object) -> list[int]:
    def __get_uvs(blender_mesh: Mesh, uv_i: int) -> np.ndarray[typing.Any, np.float32]:
        layer = blender_mesh.uv_layers[uv_i]
        uvs = np.empty(len(blender_mesh.loops) * 2, dtype=np.float32)
        layer.data.foreach_get("uv", uvs)
        uvs = uvs.reshape(len(blender_mesh.loops), 2)

        # Blender UV space -> glTF UV space
        # u,v -> u,1-v
        uvs[:, 1] *= -1
        uvs[:, 1] += 1

        return uvs

    # Get the active mesh
    me = obj.data
    tex_coord_max = len(me.uv_layers)

    dot_fields = [("vertex_index", np.uint32)]
    for uv_i in range(tex_coord_max):
        dot_fields += [("uv%dx" % uv_i, np.float32), ("uv%dy" % uv_i, np.float32)]

    dots = np.empty(len(me.loops), dtype=np.dtype(dot_fields))
    vidxs = np.empty(len(me.loops))
    me.loops.foreach_get("vertex_index", vidxs)
    dots["vertex_index"] = vidxs
    del vidxs

    for uv_i in range(tex_coord_max):
        uvs = __get_uvs(me, uv_i)
        dots["uv%dx" % uv_i] = uvs[:, 0]
        dots["uv%dy" % uv_i] = uvs[:, 1]
        del uvs

    # Calculate triangles and sort them into primitives.

    me.calc_loop_triangles()
    loop_indices = np.empty(len(me.loop_triangles) * 3, dtype=np.uint32)
    me.loop_triangles.foreach_get("loops", loop_indices)

    prim_indices = {}  # maps material index to TRIANGLES-style indices into dots

    # Bucket by material index.

    tri_material_idxs = np.empty(len(me.loop_triangles), dtype=np.uint32)
    me.loop_triangles.foreach_get("material_index", tri_material_idxs)
    loop_material_idxs = np.repeat(
        tri_material_idxs, 3
    )  # material index for every loop
    unique_material_idxs = np.unique(tri_material_idxs)
    del tri_material_idxs

    for material_idx in unique_material_idxs:
        prim_indices[material_idx] = loop_indices[loop_material_idxs == material_idx]

    prim_dots = dots[prim_indices[0]]
    prim_dots, _ = np.unique(prim_dots, return_inverse=True)
    result = [d[0] for d in prim_dots]
    return result


def get_animation_objects(ht: "HomeomorphicProperties") -> list[Object]:
    avatar_obj = ht.avatar_mesh
    animated_objects = []
    for bake_target in ht.bake_target_collection:
        if not avatar_obj:
            avatar_obj = bake_target.source_object

        if bake_target.multi_variants:
            # TODO(ranjian0) Figure out if baketargets with
            # multiple variants can be animated
            log.info(f"Skipping multivariant {bake_target.name}", print_console=False)
            continue

        obj = bake_target.variant_collection[0].workmesh
        if not obj:
            # TODO(ranjian0)
            # Possible variants not generated yet, or some other fail condition
            log.info(
                f"Skipping missing workmesh {bake_target.name}", print_console=False
            )
            continue

        has_armature = any(mod.type == "ARMATURE" for mod in obj.modifiers)
        if not has_armature:
            # Object has no armature!
            log.info(
                f"Skipping missing armature {bake_target.name}", print_console=False
            )
            continue

        animated_objects.append(obj)
    return animated_objects


def get_action_frame_range(action: Action) -> Tuple[int, int]:
    sx, sy = action.frame_range
    if (sy - sx) > 1:
        # range stop is exclusive, so add one if animation has more than one frame
        sy += 1
    return int(sx), int(sy)


def get_num_frames_all_actions() -> int:
    result = 0
    for action in bpy.data.actions:
        sx, sy = get_action_frame_range(action)
        result += sy - sx
    return result


def get_num_frames_single_action(action: Action) -> int:
    sx, sy = get_action_frame_range(action)
    return sy - sx


def get_asset_file(name: str, mode: str) -> bytes | str:
    asset_dir = Path(__file__).absolute().parent.parent / "assets"
    with open(asset_dir / name, mode) as assetfile:
        return assetfile.read()
