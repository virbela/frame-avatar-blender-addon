import bpy
import enum, time, traceback, textwrap
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


class log_level_descriptor:
	def __init__(self, log_instance: 'log_base', log_level: log_level, description: str):
		self.__doc__ = description
		self.log_instance = log_instance
		self.log_level = log_level

	def __call__(self, message):
		self.log_instance.process_message(pending_log_entry(time.localtime(), self.log_level, message))


class log_base:
	MAX_HISTORY = 1000
	def __init__(self):
		self.history = list()

		self.debug = 	log_level_descriptor(self, log_level.DEBUG,		"Debug log entries are intended for addon developer use only")
		self.info = 	log_level_descriptor(self, log_level.INFO, 		"Generic information to keep the user in the loop")
		self.warning = 	log_level_descriptor(self, log_level.WARNING, 	"Warnings are intended for things that is not really an error but that the user should still be made aware of")
		self.error = 	log_level_descriptor(self, log_level.ERROR,		"Errors the user should be made aware of")
		self.fatal = 	log_level_descriptor(self, log_level.FATAL,	 	"Fatal errors are errors that we can't recover from and we don't know how to tell the user to recover from them")

	def exception(self, message: str):
		tab = '\t'
		self.fatal(f'{message}\n{textwrap.indent(traceback.format_exc().strip(), tab)}\n')


class log_instance(log_base):
	'Log instance'

	def process_message(self, message: pending_log_entry):

		#TODO - messages that are repeating in close temporal proximity should be grouped to prevent spamming
		try:
			preferences = bpy.context.preferences.addons[__package__].preferences
		except KeyError:
			# XXX DEV(simulate preferences)
			import types
			preferences = types.SimpleNamespace()
			preferences.log_target = "devlog"

		#Get or create text target based on addon preference `log_target´
		text = bpy.data.texts.get(preferences.log_target) or bpy.data.texts.new(preferences.log_target)

		#TODO - here it would be nice to make sure that the text object is visible in the text pane but have not figured out how to do that yet

		t = time.strftime('%X', message.timestamp)
		line = f'{t} {message.log_level.name}: {message.message}'
		text.write(f'{line}\n')
		print(line)	#TODO - make this optional
		#TODO - make sure things scroll down

		self.history.append(message)

		if len(self.history) > self.MAX_HISTORY:
			self.history = self.history[-self.MAX_HISTORY:]


class dummy_log_instance(log_base):
	'Dummy log'

	def process_message(self, message: pending_log_entry):
		pass


log_writer = log_instance()
no_logging = dummy_log_instance()