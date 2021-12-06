from local_testing import mock_object as _mock_object

#Note that a lot of mocking happens as singletons even though those objects should not be singletons.

def iter_annotations(type):
	annotations = dict()
	for base in reversed(type.mro()):
		if item_anno := getattr(base, '__annotations__', None):
			annotations.update(item_anno)

	yield from annotations.items()

class _mock_stats:
	registered_classes = list()
	unregistered_classes = list()

class _mock:
	class property_instance:
		def __init__(self, name, property_type):
			self.name = name
			self.property_type = property_type

		def __set__(self, instance, value):
			instance.__dict__[self.name] = self.property_type._filter(value)

		def __get__(self, instance, owner):
			if isinstance is None:
				return self
			else:

				MISS = object()
				instance_value = instance.__dict__.get(self.name, MISS)
				if instance_value is not MISS:
					return instance_value

				else:
					try:
						return self.property_type._filter(self.property_type.named['default'])
					except:
						raise AttributeError(f'{instance} has no attribute `{self.name}´') from None

class _named_mock_object(_mock_object):
	@property
	def name(self):
		return self.positional[0]

class _mock_collection:

	def __init__(self, create_on_get = False):
		self._items = dict()
		self._create_on_get = create_on_get

	def __getitem__(self, name):
		if existing := self._items.get(name):
			return existing

		item_type = getattr(types, self._item_type)
		new = item_type(name)
		self._items[name] = new
		return new

	def __iter__(self):
		yield from self._items.values()

	def get(self, name):
		if existing := self._items.get(name):
			return existing

		if self._create_on_get:
			item_type = getattr(types, self._item_type)
			return item_type(name)


#We refer to types by name here since we will have circular dependencies of our definitions - this is the quick and kinda dirty solution
class _mock_object_collection(_mock_collection):
	_item_type = 'Object'

class _mock_collection_collection(_mock_collection):
	_item_type = 'Collection'

	def new(self, name):
		new = types.Collection(name)
		self._items[name] = new
		return new

class _mock_layer_object_collection(_mock_collection):
	_item_type = 'Object'

class _mock_node_input_collection(_mock_collection):
	_item_type = 'Node'

class _mock_node_link_collection(_mock_collection):
	_item_type = 'NodeLink'

	def new(self, src, dst):
		return types.NodeLink(src, dst)

class _mock_node_collection(_mock_collection):
	_item_type = 'NodeTree'

	def new(self, name):
		new = types.NodeTree(name)
		self._items[name] = new
		return new

class _mock_mesh_collection(_mock_collection):
	_item_type = 'Mesh'

	def new(self, name, width, height):
		new = types.Mesh(name, width, height)
		self._items[name] = new
		return new

class _mock_shape_key_collection(_mock_collection):
	_item_type = 'ShapeKey'

	key_blocks = dict()


class _mock_image_collection(_mock_collection):
	_item_type = 'Image'

	def new(self, name, width, height):
		new = types.Image(name, width, height)
		self._items[name] = new
		return new

class _mock_text_collection(_mock_collection):
	_item_type = 'Text'

	def new(self, name):
		new = types.Text(name)
		self._items[name] = new
		return new


class _mock_addon_collection(_mock_collection):
	_item_type = 'AddonPreferences'

class _mock_preferences_collection(_mock_collection):
	_item_type = 'PropertyGroup'

	log_target = 'frame.log'

class _mock_material_collection(_mock_collection):
	_item_type = 'Material'

	def new(self, name):
		new = types.Material(name)
		self._items[name] = new
		return new

class data:

	objects = _mock_object_collection()
	images = _mock_image_collection()
	meshes = _mock_mesh_collection()
	materials = _mock_material_collection()
	collections = _mock_collection_collection()
	texts = _mock_text_collection()

class context:
	active_object = None
	class preferences:
		addons = _mock_addon_collection()

	class view_layer:
		objects = _mock_layer_object_collection()

	class scene:
		class cycles:
			pass

		class render:
			@staticmethod
			def bake():
				pass


class ops:
	class object:
		@staticmethod
		def bake(type=None, save_mode=None):
			pass

class types:
	class PropertyGroup(_mock_object):
		def __init_subclass__(cls):
			for key, value in iter_annotations(cls):
				setattr(cls, key, _mock.property_instance(key, value))

	class AddonPreferences(PropertyGroup):
		preferences = _mock_preferences_collection()

	class Text(_mock_object):
		def write(self, text):
			pass

	class Mesh(_mock_object):
		materials = _mock_material_collection()
		shape_keys = _mock_shape_key_collection()

	class UIList(_mock_object):
		pass

	class Node(_mock_object):
		pass

	class NodeLink(_mock_object):
		pass

	class NodeTree(_mock_object):
		inputs = _mock_node_input_collection()
		outputs = _mock_node_input_collection()

	class Panel(_mock_object):
		pass

	class Operator(_mock_object):
		pass

	class Scene(_named_mock_object):
		pass

	class Object(_named_mock_object):
		class data:
			materials = _mock_material_collection()
			shape_keys = _mock_shape_key_collection()
			name = 'SomeObject'

		def hide_set(self, state):
			pass

		def select_set(self, state):
			pass

	class Collection(_named_mock_object):
		objects = _mock_object_collection()
		class children:
			@staticmethod
			def link(mesh_collection):
				pass

	class Image(_named_mock_object):
		def save(self):
			pass

	class Material(_named_mock_object):
		class node_tree:
			nodes = _mock_node_collection(True)
			links = _mock_node_link_collection()

class utils:
	register_class = _mock_stats.registered_classes.append
	unregister_class = _mock_stats.unregistered_classes.append

class props:
	class _mock_property(_mock_object):
		pass

	class PointerProperty(_mock_property):
		_filter = lambda x: x

	class StringProperty(_mock_property):
		_filter = str

	class BoolProperty(_mock_property):
		_filter = bool

	class IntProperty(_mock_property):
		_filter = int

	class FloatProperty(_mock_property):
		_filter = float


	class EnumProperty(_mock_property):
		_filter = lambda x: x

	class CollectionProperty(_mock_property):
		_filter = lambda x: x
