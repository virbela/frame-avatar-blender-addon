from local_testing import test_suite
import logging

with test_suite('Addon tests', verbose=True) as (positive, negative):
	with positive('Basic import of addon'):
		import sources as addon

	with positive('Basic logging'):
		from sources.logging import log_writer
		import bpy

		#Testing with bpy.context mock
		with log_writer(bpy.context) as log:
			log.debug('Debug message')
			log.info('Info message')
			log.warning('Warning message')
			log.error('Error message')
			log.fatal('Fatal message')


	with positive('Register addon'):
		import sources as addon
		import bpy

		#Clear lists
		bpy._mock_stats.registered_classes.clear()
		bpy._mock_stats.unregistered_classes.clear()

		#Make calls
		addon.register()
		addon.unregister()
		if not bpy._mock_stats.registered_classes:
			raise Exception('No classes were registered')

		#Verify
		assert bpy._mock_stats.registered_classes == bpy._mock_stats.unregistered_classes, 'Registration and unregistration procedure mismatch'

	# with positive('Batch bake operator'):
	# 	import sources as addon
	# 	import bpy

	# 	#Setup mock state
	# 	bpy.context.scene.homeomorphictools = addon.HomeomorphicProperties()

	# 	bpy.context.scene.homeomorphictools.avatar_string = 'Avatar'
	# 	bpy.context.scene.homeomorphictools.uvset_string = 'UVMap'

	# 	bpy.context.scene.collection = bpy.types.Collection()

	# 	Avatar_MorphSet = bpy.data.collections.new('Avatar_MorphSet')
	# 	Avatar_MorphSet.objects['Eye_L']
	# 	Avatar_MorphSet.objects['Eye_R']

	# 	#Select avatar
	# 	avatar = bpy.context.active_object = bpy.data.objects['Avatar']
	# 	avatar.active_material = avatar.data.materials.new('Some material')

	# 	#Run operator
	# 	addon.BAKETARGET_OT_my_op().execute(bpy.context)


	#NOTE - this is only for quick testing of developing features
	with negative('Test bake exception'):
		import sources as addon
		from sources import baking
		import bpy

		#Setup mock state
		bpy.context.scene.homeomorphictools = addon.HomeomorphicProperties()

		bpy.context.scene.homeomorphictools.avatar_string = 'Avatar'
		bpy.context.scene.homeomorphictools.uvset_string = 'UVMap'

		bpy.context.scene.collection = bpy.types.Collection()

		Avatar_MorphSet = bpy.data.collections.new('Avatar_MorphSet')
		Avatar_MorphSet.objects['Eye_L']
		Avatar_MorphSet.objects['Eye_R']

		#Select avatar
		avatar = bpy.context.active_object = bpy.data.objects['Avatar']
		avatar.active_material = None

		baking.batch_bake('Avatar')

		#Run operator
		#addon.BATCHBAKE_OT_test_operator().execute(bpy.context)




	#print(addon)
