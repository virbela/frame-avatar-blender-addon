import textwrap, re, inspect
from inspect import linecache
from dataclasses import dataclass

def parse_signature(sig):
	return inspect.signature(eval(f'lambda {sig}: None'))

@dataclass
class tp_rule:
	name: str
	pattern: re.Pattern
	function: object

def iter_type(t):
	seen = set()
	for b in t.mro():
		for key, value in t.__dict__.items():
			if key in seen:
				continue

			yield key, value
			seen.add(key)

class re_transpiler:
	'This transpiler is stateless and can therefore be operated with classmethods. One could improve this but it is not needed at this point'
	def __init_subclass__(cls):
		cls.transpilation_rules = list()
		for key, member in iter_type(cls):
			if anno := getattr(member, '__annotations__', None):
				if pattern := anno.get('return'):
					cls._register_transpilation_rule(key, pattern, member)

	@classmethod
	def _register_transpilation_rule(cls, name, raw_pattern, function):
		pattern = re.compile(raw_pattern, re.M)
		cls.transpilation_rules.append(tp_rule(name, pattern, function))

	@classmethod
	def transpile(cls, context, source, position=0):

		result = ''
		last_position = position

		while cls.transpilation_rules:

			closest_match = None
			closest_rule = None

			for rule in cls.transpilation_rules:
				if match := rule.pattern.search(source, position):
					left, right = match.span()

					if closest_match:
						closest_left, closest_right = closest_match.span()
						if left < closest_left:
							closest_match, closest_rule = match, rule
					else:
						closest_match, closest_rule = match, rule

			if closest_match:
				match, rule = closest_match, closest_rule
				left, right = match.span()

				replacement = rule.function(cls, context, *match.groups(), **match.groupdict())

				if replacement is False:
					#No replacement
					result += source[position:right]
				else:
					result += source[position:left] + replacement

				position = right

				if left == right:
					#This is a special case if matching on something that has no length, like an empty line.
					#In this case we have to advance position by one or we will get stuck in an infinite loop
					#In the current use this will not happen but never hurts to be thorough for future use
					position += 1

			else:
				return result + source[position:]

		return source	#No rules - nothing done



class node_code_transpiler(re_transpiler):

	_identifier = r'[A-Za-z_][A-Za-z0-9_]*'

	#TO-DOC - document this properly and somewhere else
	#Short story: after mandatory arguments `transpiler´ and `context´,
	#  we have positional capture groups as positional arguments
	#  and we have named capture groups (P<name>?...) as named arguments
	#  the pattern is described using the return annotation and it is probably
	#  a good idea to use a raw string for this such as below
	#
	#  If return value is False, no replacement is made
	#  otherwise it is assumed to be a string with the replacement (could be empty too)
	#
	#  The purpose of context is to provide a place to shove stuff specific for the transpilation run, this could be any type
	#  we will use a dict in this particular case for the moment
	def define_arguments(transpiler, context, argument_list) -> r'^arguments:\s+(.*)$\n':
		context['signature'] = parse_signature(f'_tree, {argument_list}')
		return ''

	#Finds line:		a.b --> c.d
	#Replaces with: 	_tree.links.new(c.inputs['d'], a.outputs['b'])
	#Note that we will replace dashes with spaces so if you want node slot "Base Color" you do "Base-Color"
	def define_connection(transpiler, context, indention, source_object, source_slot, dest_object, dest_slot) -> r'^(\s*)(\S+)\.(\S+)\s*-->\s*(\S+)\.(\S+)$':
		source_slot = source_slot.replace('-', ' ')
		dest_slot = dest_slot.replace('-', ' ')
		return f'{indention}_tree.links.new({dest_object}.inputs[{dest_slot!r}], {source_object}.outputs[{source_slot!r}])'

	#This defines a node
	#Note that this function will only work on root level indention
	#  due to this not being a fully fledged code generator
	#The syntax here is: type name storage_name
	#  storage_name is optional and defaults to the value of name
	#  This is useful to be able to be concise in local variables in the definition expression, yet retaining verbose naming for objects in blender
	def define_node(transpiler, context, indention, node_type, name, storage_name) -> rf'^(\s*)({_identifier})\s+({_identifier})(?:\s+({_identifier}))?\s*$':
		if not storage_name:
			storage_name = name

		return (
			f'{indention}{name} = _tree.nodes.new({node_type!r})\n'
			f'{indention}{name}.name = {storage_name!r}\n'
		)


class thunk_return:
	def __init__(self, value):
		self.value = value

	def __call__(self):
		return self.value


def load_node_setup_function(name, raw_code):
	'This version creates materials from scratch'

	pre = textwrap.dedent('''
		from .helpers import set_selection as _set_selection, set_active as _set_active

		def set_selection(*node_list):
			_set_selection(_tree.nodes, *node_list)

		def set_active(node):
			_set_active(_tree.nodes, node)

		#DECISION - should this be mandatory?
		_tree.nodes.clear()

	''').strip()

	code = textwrap.dedent(raw_code).strip()

	tp_context = dict()
	result = node_code_transpiler.transpile(tp_context, code)

	body = textwrap.indent(f'{pre}\n{result}', '\t')
	resulting_code = f'def {name}{tp_context["signature"]}:\n{body}'

	l_scope, g_scope = dict(), dict(
		__package__ = __package__,
		__name__ = f'{__name__}.generated',
	)

	try:
		compiled_code = compile(resulting_code, f'{__name__}.generated.{name}', 'exec')
		exec(compiled_code, g_scope, l_scope)
	except:
		log.fatal('--- Problematic code segment for shader node generation ---')
		log.fatal(resulting_code)
		log.fatal('--- End of output ---')
		raise

	# make sure source is available in traceback formatting
	#NOTE - this only works outside of blender because blender does something weird. Will not spend time on figuring that out now.
	linecache.cache[compiled_code.co_filename] = (thunk_return(resulting_code),)

	result_function = l_scope[name]
	result_function.__source__ = resulting_code	#DECISION - maybe not do this in distributed version, it can be useful for debugging though
	return result_function