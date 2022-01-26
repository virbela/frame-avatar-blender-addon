import bpy
import enum
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


#DEPRECHATED - should be require_work_scene
# The context here is only for logging purposes
def get_work_scene(context):
	if scene := bpy.data.scenes.get(WORK_SCENE):
		return scene
	else:
		log.error(f'Work scene `{WORK_SCENE}´ could not be found.')


#DEPRECHATED - should be require_bake_scene and comments should be updated
# The context here is only for logging purposes and is not currently used here but
# we want to keep the API consistent in case we later do want some logging here
def get_bake_scene(context):
	if scene := bpy.data.scenes.get(BAKE_SCENE):
		return scene
	else:
		return bpy.data.scenes.new(BAKE_SCENE)


def get_homeomorphic_tool_state(context):
	if work_scene := get_work_scene(context):
		return work_scene.homeomorphictools

	#TODO raise exception if fail



def get_named_entry(collection, name):
	return collection.get(name)

def require_named_entry(collection, name):
	if not name:
		raise FrameException.NoNameGivenForCollectionLookup(collection)

	if candidate := collection.get(name):
		return candidate
	else:
		raise FrameException.NamedEntryNotFound(collection, name)

#TODO - we should use an enum mode instead of a bunch of booleans which is confusing
#TODO - ignore_existing is not very well named
def create_named_entry(collection, name, *positional, allow_rename=False, recreate=False, ignore_existing=False):

	if name in collection:
		if recreate:
			collection.remove(collection.get(name))
			return collection.new(name, *positional)
		elif ignore_existing:
			return collection.get(name)
		elif allow_rename:
			return collection.new(name, *positional)
		else:
			raise FrameException.FailedToCreateNamedEntry(collection, name)

	else:
		return collection.new(name, *positional)



def set_scene(context, scene):
	context.window.scene = scene

def set_selection(collection, *selected):
	'Replaces current selection'
	new_selection = set(selected)
	for item in collection:
		#NOTE There are two APIs to select things, we will favor the setter since that seems the be most recent
		if setter := getattr(item, 'select_set', None):
			setter(item in new_selection)
		else:
			item.select = item in new_selection

# this is just to make code more readable
def clear_selection(collection):
	set_selection(collection)

def set_active(collection, item):
	collection.active = item

def clear_active(collection):
	collection.active = None

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

