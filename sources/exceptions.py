class BakeException:
	class base(BaseException):
		pass

	class NoActiveMaterial(base):
		def __init__(self, object):
			self.object = object
			super().__init__(f'{object} has no active material which is required for the operation.')
