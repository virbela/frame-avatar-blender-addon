import bpy, enum
from .constants import COLORS


def print_to_editor(string, outputname):
	text_input = str(string)

	textdata = bpy.data.texts

	if textdata.get(outputname) == None:
		#textdata.new(f'.{outputname}') # hidden in text editor
		textdata.new(outputname) # not hidden

	textdata[outputname].from_string(string) # overwrite existing

def hide_everything_from_render():
	for obj in bpy.data.objects:
		obj.hide_render = True


# def register_class(cls):
# 	pending_classes.append(cls)
# 	return cls

def deselect_all_nodes(node_list):
	for node in node_list:
		node.select = False



def get_named_image(name, size=None, size_mandatory=False, auto_create=True, background_color=COLORS.BLACK):
	img = bpy.data.images.get(name)

	#Support enums
	if isinstance(background_color, enum.Enum):
		background_color = background_color.value

	if img is None:
		img = bpy.data.images.new(name, *size)
		img.generated_color = background_color

	elif size_mandatory and tuple(img.size) != tuple(size):
		#Set proper size and color
		img.generated_width, img.generated_height = size
		img.generated_color = background_color
		img.source = 'GENERATED'

	return img


