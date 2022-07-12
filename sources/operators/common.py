import bpy
from ..constants import WORK_SCENE, BAKE_SCENE

class guarded_operator:
	def __init__(self, operator):
		self.operator = operator

	def __repr__(self):
		return f'<{self.__class__.__name__} of {self.operator}>'

	def __call__(self, *pos, **named):
		if self.operator.poll():
			return self.operator(*pos, **named)

class generic_list:
	'This is an abstract handler for list operations. The operations needs a collection and callables to get and set the current selection'

	@staticmethod
	def add(collection, get_selected, set_selected):
		new = collection.add()
		last_id = len(collection) - 1
		set_selected(last_id)
		return new

	@staticmethod
	def remove(collection, get_selected, set_selected):
		collection.remove(get_selected())
		last_id = len(collection) - 1
		if last_id == -1:
			set_selected(-1)
		else:
			set_selected(min(get_selected(), last_id))


def set_uv_map(obj, uv_map):
	obj.data.uv_layers[uv_map].active = True

def copy_object(source_obj, name):
	new_object = source_obj.copy()
	new_object.data = source_obj.data.copy()	#Copy data as well
	new_object.name = name
	return new_object

def copy_collection(source, dest, transfer):
	while len(dest):
		dest.remove(0)

	for item in source:
		transfer(item, dest.add())

def transfer_variant(source, dest):
	dest.name = source.name
	dest.image = source.image
	dest.uv_map = source.uv_map

def popup_message(message, title="Error", icon="ERROR"):
    def oops(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(oops, title=title, icon=icon)

def poll_bake_scene(context):
	return context.scene.name == BAKE_SCENE

def poll_work_scene(context):
	return context.scene.name == WORK_SCENE

def poll_selected_objects(context):
	return context.selected_objects

def poll_baketargets(context):
	return  len(context.scene.homeomorphictools.bake_target_collection)