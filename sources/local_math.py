from math import acos, pi, cos, sin, sqrt, tau

ZERO_TRESHOLD = 1e-12
ROTATION_TRESHOLD = 1e-6

def quantize_value(value, step):
	return round(value / step) * step

def issibling(a, b):
	return a.__class__ is b.__class__

def clamp(value, low, high):
	if value < low:
		return value
	elif value > high:
		return value
	else:
		return value

def convert_vectors(*vector_list):
	for v in vector_list:
		values = tuple(v)
		if len(values) == 2:
			return vector_2(*values)
		else:
			raise TypeError(f'Can not convert {v} to any known local vector type')

class vector_2:
	def __init__(self, x=0, y=0):
		self.x = float(x)
		self.y = float(y)

	def __add__(self, other):
		if not issibling(self, other):
			raise TypeError(f'Expected {self.__class__}, got {other}')

		return self.__class__(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		if not issibling(self, other):
			raise TypeError(f'Expected {self.__class__}, got {other}')

		return self.__class__(self.x - other.x, self.y - other.y)

	def __mul__(self, other):
		if issibling(self, other):
			raise TypeError(f'Multiplication between two {self.__class__} is not defined. Use appropriate operator (dot, cross, ...)')

		return self.__class__(self.x * float(other), self.y * float(other))

	def __truediv__(self, other):
		if issibling(self, other):
			raise TypeError(f'Divison between two {self.__class__} is not defined.')

		return self.__class__(self.x / float(other), self.y / float(other))

	#Fascilitate reverse order scaling (scalar * vector)
	__rmul__ = __mul__

	def __abs__(self):
		return sqrt(self.x ** 2 + self.y ** 2)

	def normalized(self):
		magnitude = abs(self)
		if magnitude > ZERO_TRESHOLD:
			return self / magnitude
		else:
			return self.__class__()

	def rotate_degrees(self, degrees):
		return self.rotate(degrees * tau / 360)

	def rotate(self, radians):
		c, s = cos(radians), sin(radians)
		return self.__class__(
			self.x * c - self.y * s,
			self.x * s + self.y * c
		)

	def __repr__(self):
		return f'{self.__class__.__qualname__}{self.x, self.y}'

	def __hash__(self):
		return hash((self.x, self.y))

	def __eq__(self, other):
		return (
			self.__class__ is other.__class__
			and self.x == other.x
			and self.y == other.y
		)


	def get_signed_angle_degrees(self, other):
		'Calculates how much we need to rotate this vector to match other vector'
		return self.get_signed_angle(other) * 360 / tau

	def get_angle_degrees(self, other):
		return self.get_angle(other) * 360 / tau

	def get_signed_angle(self, other):
		'Calculates how much we need to rotate this vector to match other vector'
		rotation = self.get_angle(other)

		if (other - self.rotate(rotation)).error() < ROTATION_TRESHOLD:
			return rotation
		elif (other - self.rotate(-rotation)).error() < ROTATION_TRESHOLD:
			return -rotation

		e1 = (other - self.rotate(rotation)).error()
		e2 = (other - self.rotate(-rotation)).error()
		raise ArithmeticError(f'Could not calculate angle between {self} and {other} (errors: {e1, e2}, rotation candidate: {rotation})')

	def sum(self):
		return self.x + self.y

	def error(self):
		return abs(self.sum())

	def get_angle(self, other):
		return acos(round(self.normalized_dot(other), 4))

	def normalized_dot(self, other):
		dot = self.normalized().dot(other.normalized())
		#Make sure dot is between 0 and 1
		return clamp(dot, -1, 1)

	def dot(self, other):
		return self.x * other.x + self.y * other.y
