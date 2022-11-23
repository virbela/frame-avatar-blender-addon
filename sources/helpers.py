import io 
import bpy
import enum
import uuid
import bmesh
import pstats
import cProfile 
import threading
import addon_utils
import numpy as np
from dataclasses import dataclass
from contextlib import contextmanager
from .logging import log_writer as log
from .constants import BAKE_SCENE, WORK_SCENE
from .exceptions import InternalError, FrameException

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


def register_class(cls):
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

	def get_properties_by_names(self, names, if_missing=missing_action.FAIL):
		'Takes list of names separated by space and yields the values of those members.'

		if if_missing is missing_action.FAIL:
			return (getattr(self, member) for member in names.split())
		elif if_missing is missing_action.RETURN_NONE:
			return (getattr(self, member, None) for member in names.split())
		else:
			raise ValueError(f'if_missing has unknown value')


def require_work_scene(context):
	if scene := bpy.data.scenes.get(WORK_SCENE):
		return scene

	log.error(f'Work scene `{WORK_SCENE}` could not be found.')


def require_bake_scene(context):
	if scene := bpy.data.scenes.get(BAKE_SCENE):
		return scene

	return bpy.data.scenes.new(BAKE_SCENE)


def get_homeomorphic_tool_state(context):
	if work_scene := require_work_scene(context):
		return work_scene.homeomorphictools

	raise InternalError("Work scene not Found.")


def get_named_entry(collection, name):
	return collection.get(name)


def require_named_entry(collection, name):
	if not name:
		raise FrameException.NoNameGivenForCollectionLookup(collection)

	if candidate := collection.get(name):
		return candidate
	else:
		raise FrameException.NamedEntryNotFound(collection, name)


def create_named_entry(collection, name, *positional, action=named_entry_action.GET_EXISTING):

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

def set_scene(context, scene):
	context.window.scene = scene


def set_selection(collection, *selected, synchronize_active=False, make_sure_active=False):
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


def clear_selection(collection):
	set_selection(collection)


def set_active(collection, item):
	collection.active = item


def clear_active(collection):
	collection.active = None


def set_rendering(collection, *selected, synchronize_active=False, make_sure_active=False):
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


def get_nice_name(collection, prefix, max_prefix_length, random_hash_length=8, max_tries=1000):

	for v in range(max_tries):
		tail = f'-{v:03}' if v else ''
		candidate = f'{prefix[:max_prefix_length]}{tail}'
		if candidate not in collection:
			return candidate

	raise Exception('severe fail')	#TODO - proper exception


def is_reference_valid(target):
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


def get_bake_target_variant_name(bake_target, variant):
	if bake_target.multi_variants:
		return f'{bake_target.shortname}.{variant.name}'
	return f'{bake_target.shortname}'


def purge_object(obj):
	bpy.data.objects.remove(obj)
	for block in bpy.data.meshes:
		if block.users == 0:
			bpy.data.meshes.remove(block)
	
	for block in bpy.data.materials:
		if block.users == 0:
			bpy.data.materials.remove(block)


def is_dev():
	# if we are installed as an addon, assume this is a production dist
	for mod in addon_utils.modules():
		if 'frame_avatar_addon' == mod.__name__:
			return False
	return True


def get_prefs():
	try:
		preferences = bpy.context.preferences.addons[__package__].preferences
		return preferences
	except KeyError:
		# XXX DEV(simulate preferences)
		import types
		preferences = types.SimpleNamespace()
		preferences.log_target = "devlog"
		preferences.glb_export_dir = ""
		preferences.atlas_export_dir = ""
		return preferences


def popup_message(message, title="Error", icon="ERROR"):
    def oops(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(oops, title=title, icon=icon)


def ensure_applied_rotation(object):
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


def get_animation_objects(ht):
    avatar_obj = ht.avatar_object
    animated_objects = []
    for bake_target in ht.bake_target_collection:
        if not avatar_obj:
            avatar_obj = bake_target.source_object 

        if bake_target.multi_variants:
            # TODO(ranjian0) Figure out if baketargets with multiple variants can be animated
            log.info(f"Skipping multivariant {bake_target.name}")
            continue

        obj = bake_target.variant_collection[0].workmesh
        if not obj:
            # TODO(ranjian0) 
            # Possible variants not generated yet, or some other fail condition
            log.info(f"Skipping missing workmesh {bake_target.name}")
            continue

        has_armature = any(mod.type == 'ARMATURE' for mod in obj.modifiers)
        if not has_armature:
            # Object has no armature!
            log.info(f"Skipping missing armature {bake_target.name}")
            continue

        animated_objects.append(obj)
    return animated_objects


def get_gltf_export_indices(obj):
    def __get_uvs(blender_mesh, uv_i):
        layer = blender_mesh.uv_layers[uv_i]
        uvs = np.empty(len(blender_mesh.loops) * 2, dtype=np.float32)
        layer.data.foreach_get('uv', uvs)
        uvs = uvs.reshape(len(blender_mesh.loops), 2)

        # Blender UV space -> glTF UV space
        # u,v -> u,1-v
        uvs[:, 1] *= -1
        uvs[:, 1] += 1

        return uvs


    # Get the active mesh
    me = obj.data
    tex_coord_max = len(me.uv_layers)

    dot_fields = [('vertex_index', np.uint32)]
    for uv_i in range(tex_coord_max):
        dot_fields += [('uv%dx' % uv_i, np.float32), ('uv%dy' % uv_i, np.float32)]


    dots = np.empty(len(me.loops), dtype=np.dtype(dot_fields))
    vidxs = np.empty(len(me.loops))
    me.loops.foreach_get('vertex_index', vidxs)
    dots['vertex_index'] = vidxs
    del vidxs

    for uv_i in range(tex_coord_max):
        uvs = __get_uvs(me, uv_i)
        dots['uv%dx' % uv_i] = uvs[:, 0]
        dots['uv%dy' % uv_i] = uvs[:, 1]
        del uvs


    # Calculate triangles and sort them into primitives.

    me.calc_loop_triangles()
    loop_indices = np.empty(len(me.loop_triangles) * 3, dtype=np.uint32)
    me.loop_triangles.foreach_get('loops', loop_indices)

    prim_indices = {}  # maps material index to TRIANGLES-style indices into dots

    # Bucket by material index.

    tri_material_idxs = np.empty(len(me.loop_triangles), dtype=np.uint32)
    me.loop_triangles.foreach_get('material_index', tri_material_idxs)
    loop_material_idxs = np.repeat(tri_material_idxs, 3)  # material index for every loop
    unique_material_idxs = np.unique(tri_material_idxs)
    del tri_material_idxs

    for material_idx in unique_material_idxs:
        prim_indices[material_idx] = loop_indices[loop_material_idxs == material_idx]


    prim_dots = dots[prim_indices[0]]
    prim_dots, indices = np.unique(prim_dots, return_inverse=True)
    result = [d[0] for d in prim_dots]
    return result
