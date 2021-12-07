import bpy
import enum, time
from dataclasses import dataclass

#TODO - currently we don't care about log level but we should later have a place for accessing logs and filtering logs

class log_level(enum.IntEnum):
	DEBUG = 1
	INFO = 2
	WARNING = 3
	ERROR = 4
	FATAL = 5



@dataclass
class pending_log_entry:
	timestamp: time.struct_time
	log_level: log_level
	message: str

class log_level_handler:
	def __init__(self, bound_log_context, log_level):
		self.bound_log_context = bound_log_context
		self.log_level = log_level

	def __call__(self, message):
		log, context = self.bound_log_context.log, self.bound_log_context.context
		log.process_message(context, pending_log_entry(time.localtime(), self.log_level, message))

class log_level_descriptor:
	def __init__(self, log_level, description):
		self.__doc__ = description
		self.log_level = log_level

	def __get__(self, instance, owner):
		if instance is None:
			return self
		else:
			return log_level_handler(instance, self.log_level)

class bound_log_context:
	'Log context bound to blender context'

	debug = log_level_descriptor(	log_level.DEBUG, 		"Debug log entries are intended for addon developer use only")
	info = log_level_descriptor(	log_level.INFO, 		"Generic information to keep the user in the loop")
	warning = log_level_descriptor(	log_level.WARNING, 		"Warnings are intended for things that is not really an error but that the user should still be made aware of")
	error = log_level_descriptor(	log_level.ERROR,		"Errors the user should be made aware of")
	fatal = log_level_descriptor(	log_level.FATAL,	 	"Fatal errors are errors that we can't recover from and we don't know how to tell the user to recover from them")

	def __init__(self, log, context):
		self.log = log
		self.context = context


class pending_log_context:
	'Pending log context referencing a blender context'
	def __init__(self, log, context):
		self.log = log
		self.context = context

	def __enter__(self):
		return bound_log_context(self.log, self.context)

	def __exit__(self, et, ev, tb):
		pass

class log_instance:
	MAX_HISTORY = 1000

	'Log instance'
	def __init__(self):
		self.history = list()

	def __call__(self, context):
		'Return a pending log context for using with pythons with statement (context manager)'
		return pending_log_context(self, context)

	def process_message(self, context, message):

		#TODO - messages that are repeating in close temporal proximity should be grouped to prevent spamming

		preferences = context.preferences.addons[__package__].preferences
		#Get or create text target based on addon preference `log_target´
		text = bpy.data.texts.get(preferences.log_target) or bpy.data.texts.new(preferences.log_target)

		#TODO - here it would be nice to make sure that the text object is visible in the text pane but have not figured out how to do that yet

		t = time.strftime('%X', message.timestamp)
		text.write(f'{t} {message.log_level.name}: {message.message}\n')

		#TODO - make sure things scroll down

		self.history.append(message)

		if len(self.history) > self.MAX_HISTORY:
			self.history = self.history[-self.MAX_HISTORY:]



log_writer = log_instance()

