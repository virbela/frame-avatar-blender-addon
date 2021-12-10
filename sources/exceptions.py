class InternalError(BaseException):
	pass

class BakeException:
	class base(BaseException):
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
