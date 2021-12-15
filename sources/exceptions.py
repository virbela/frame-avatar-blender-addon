class InternalError(Exception):
	pass

#DECISION - should we go away from pythons camel case exception naming scheme to make it easier to read? If everything is prefixed by the module name it shouldn't be a surprise to anyone.

class FrameException:
	class FailedToCreateNamedEntry(Exception):
		def __init__(self, collection, name):
			super().__init__(f'Failed to create a named entry named `{name}´ in collection {collection}.')

	class NamedEntryNotFound(Exception):
		def __init__(self, collection, name):
			super().__init__(f'No entry named `{name}´ was found in collection {collection}.')

	class NoNameGivenForCollectionLookup(Exception):
		def __init__(self, collection):
			super().__init__(f'No name was given for look up in collection {collection}.')


class BakeException:
	class base(Exception):
		pass

	class NoActiveMaterial(base):
		def __init__(self, object):
			self.object = object
			super().__init__(f'{object} has no active material which is required for the operation.')

	class NoObjectChosen(base):
		def __init__(self, name):
			self.name = name
			super().__init__(f'The operation requries an object to be chosen and no such object `{name}´ exists.')

	class NoSuchScene(base):
		def __init__(self, name):
			self.name = name
			super().__init__(f'The operation requires a scene named `{name}´ which was not found.')
