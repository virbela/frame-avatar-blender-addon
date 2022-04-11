import bpy
import enum
import addon_utils
from dataclasses import dataclass
from .logging import log_writer as log
from .constants import *
from .exceptions import *
import threading, uuid

pending_classes = list()

def IMPLEMENTATION_PENDING(*p, **n):
	raise InternalError(f'This feature is not implemented! (arguments: {p} {n})')


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