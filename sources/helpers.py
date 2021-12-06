import bpy
import enum
from dataclasses import dataclass

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

	def __iter__(self):
		for member in self.members.values():
			yield (member.identifier, member.name, member.description, member.icon, member.number)


class base_property_group(bpy.types.PropertyGroup):
	def get_properties_by_names(self, names, if_missing=missing_action.FAIL):
		'Takes list of names separated by space and yields the values of those members.'

		if if_missing is missing_action.FAIL:
			return (getattr(self, member) for member in names.split())
		elif if_missing is missing_action.RETURN_NONE:
			return (getattr(self, member, None) for member in names.split())
		else:
			raise ValueError(f'if_missing has unknown value')

