import bpy
import enum
from dataclasses import dataclass
from .logging import log_writer
from .constants import *
from .exceptions import *

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


def get_work_scene(context):
	if scene := bpy.data.scenes.get(WORK_SCENE):
		return scene
	else:
		with log_writer(context) as log:
			log.error(f'Work scene `{WORK_SCENE}´ could not be found.')



def get_homeomorphic_tool_state(context):
	if work_scene := get_work_scene(context):
		return work_scene.homeomorphictools


