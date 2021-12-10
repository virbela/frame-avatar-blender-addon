from ..helpers import IMPLEMENTATION_PENDING
import bpy

#TODO - move to helpers
#Note - was going to use https://docs.python.org/3/library/operator.html#operator.attrgetter but there is no attrsetter so we'll just define both for consistency
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


#TODO - implement proper version of commented code blocks in this module

#MINOR-TODO - We could still improve list handling but for the moment it is good enough to strike a balance between maintainability and development

class generic_list:
	'This is an abstract handler for list operations. The operations needs a collection and callables to get and set the current selection'

	@staticmethod
	def add(collection, get_selected, set_selected):
		new = collection.add()
		last_id = len(collection) - 1
		set_selected(last_id)

	@staticmethod
	def remove(collection, get_selected, set_selected):
		collection.remove(get_selected())
		last_id = len(collection) - 1
		if last_id == -1:
			set_selected(-1)
		else:
			set_selected(min(get_selected(), last_id))


def auto_assign_atlas(operator, context, ht):
	'Goes through all bake targets and assigns them to the correct atlas and UV set based on the uv_mode'

	for bake_target in ht.bake_target_collection:
		print('BAKE', bake_target.name, bake_target.get_mirror_type(ht))



update_bake_scene = IMPLEMENTATION_PENDING
pack_uv_islands = IMPLEMENTATION_PENDING
bake_all_bake_targets = IMPLEMENTATION_PENDING
bake_selected_bake_targets = IMPLEMENTATION_PENDING
create_bake_targets_from_shapekeys = IMPLEMENTATION_PENDING

def create_bake_targets_from_shapekeys(operator, context, ht):
	#BUG - User may create multiple bake targets

	if source := bpy.data.objects.get(ht.source_object):
		shape_keys = source.data.shape_keys.key_blocks

		def create_mirror(primary, secondary):
			new = ht.bake_target_mirror_collection.add()
			new.primary = primary.identifier
			new.secondary = secondary.identifier
			return new

		#TODO - Here we should run our rules for the naming scheme

		#Create all targets
		targets = dict()
		for sk in shape_keys:
			key = sk.name
			targets[key] = dict(
				name = f'bake_{ht.source_object}_{key}',
				object_name = ht.source_object,
				shape_key_name = key,
				uv_mode = 'UV_IM_MONOCHROME',
			)


		#NOTE - there is a bug where we can only set uv_mode (or any other enum) once from the same context.
		#		To avoid this bug we first create dicts that represents the new bake targets and then we instanciate them below
		for target in targets.values():
			new = ht.bake_target_collection.add()
			for key, value in target.items():
				setattr(new, key, value)


		#Configure targets and mirrors
		for key in targets:
			if key.endswith('_L'):
				base = key[:-2]
				Lk = f'{base}_L'
				Rk = f'{base}_R'
				R = targets.get(Rk)

				if R:
					create_mirror(Lk, Rk)
				else:
					log.error(f"Could not create mirror for {key} since there was no such object `{Rk}´")

			elif key.endswith('_R'):
				pass

			elif key.endswith('__None'):
				targets[key]['uv_mode'] = 'UV_IM_NIL'



#create bake targets from shape keys
	#TODO - define the proper frame_operator

	# def execute(self, context):

	# 	if HT := get_homeomorphic_tool_state(context):	#contribution note 2

	# 		if source := bpy.data.objects.get(HT.source_object):
	# 			shape_keys = source.data.shape_keys.key_blocks
	# 			create_bake_targets_from_shapekeys(context, HT, shape_keys)

	# 		else:
	# 			raise BakeException.NoObjectChosen(HT.source_object)

	# 		return {'FINISHED'}

	# 	else:
	# 		return {'CANCELLED'}





class bake_mirrors:
	def set_primary(operator, context, ht):
		if mirror := ht.get_selected_mirror():
			if bake_target := ht.get_selected_bake_target():
				mirror.primary = bake_target.identifier

	def set_secondary(operator, context, ht):
		if mirror := ht.get_selected_mirror():
			if bake_target := ht.get_selected_bake_target():
				mirror.secondary = bake_target.identifier

	def add(operator, context, ht):
		generic_list.add(ht.bake_target_mirror_collection, a_get(ht, 'selected_bake_target_mirror'), a_set(ht, 'selected_bake_target_mirror'))

	def remove(operator, context, ht):
		generic_list.remove(ht.bake_target_mirror_collection, a_get(ht, 'selected_bake_target_mirror'), a_set(ht, 'selected_bake_target_mirror'))

class bake_targets:
	#BUG - currently we don't check if a target is in a mirror and therefore a mirror will point to the wrong thing if removing a reference

	def add(operator, context, ht):
		generic_list.add(ht.bake_target_collection, a_get(ht, 'selected_bake_target'), a_set(ht, 'selected_bake_target'))

	def remove(operator, context, ht):
		generic_list.remove(ht.bake_target_collection, a_get(ht, 'selected_bake_target'), a_set(ht, 'selected_bake_target'))

class bake_variants(generic_list):

	def add(operator, context, ht):
		if bake_target := ht.get_selected_bake_target():
			generic_list.add(bake_target.variant_collection, a_get(bake_target, 'selected_variant'), a_set(bake_target, 'selected_variant'))

	def remove(operator, context, ht):
		if bake_target := ht.get_selected_bake_target():
			generic_list.remove(bake_target.variant_collection, a_get(bake_target, 'selected_variant'), a_set(bake_target, 'selected_variant'))
