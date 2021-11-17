from local_math import *
from local_testing import test_suite
TRESHOLD = 1e-12

with test_suite('Vector math tests', verbose=True) as (positive, negative):

	with positive('Vector equality'):
		assert vector_2(0.5, 0.5) == vector_2(0.5, 0.5)
		assert vector_2(0.5, 0.5) != vector_2(1.5, 0.5)

	with positive('Vector translation'):
		assert vector_2(0.5, 0.5) + vector_2(1.0, 2.0) == vector_2(1.5, 2.5)
		assert vector_2(1.5, 2.5) - vector_2(1.0, 2.0) == vector_2(0.5, 0.5)

	with positive('Vector scaling'):
		assert vector_2(0.5, 2) * 3 == vector_2(1.5, 6.0)
		assert 3 * vector_2(0.5, 2) == vector_2(1.5, 6.0)
		assert vector_2(1.5, 6.0) / 3 == vector_2(0.5, 2.0)

	with negative('Undefined products and such'):
		vector_2(1, 2) * vector_2(3, 4)
		vector_2(1, 2) / vector_2(3, 4)

	with positive('Common operations'):
		assert abs(vector_2(3, 4)) == 5
		assert vector_2(30, 40).normalized() == vector_2(0.6, 0.8)
		assert vector_2(0, 0).normalized() == vector_2()

		assert convert_vectors((1, 2), [1, 2]) == vector_2(1, 2), vector_2(1, 2)

	with positive('Advanced operations'):

		original = vector_2(100, 0)
		rotated = original.rotate_degrees(60)
		assert (50 - TRESHOLD) < rotated.x < (50 + TRESHOLD)

		#Negative because we are asking how much to rotate the rotated one to match the original
		assert (-60 - TRESHOLD) < rotated.get_signed_angle_degrees(original) < (-60 + TRESHOLD)


	with negative('Impossible operations'):
		vector_2(10, 20).get_signed_angle_degrees(vector_2(0, 0))


