import bpy
import textwrap
from ..helpers import get_bake_scene
from ..logging import log_writer as log 

def clear_bake_targets(operator, context, ht):
	ht.selected_bake_target = -1
	while len(ht.bake_target_collection):
		ht.bake_target_collection.remove(0)


def clear_bake_scene(operator, context, ht):
	scene = get_bake_scene(context)
	for item in scene.objects:
		bpy.data.meshes.remove(item.data, do_unlink=True)


class devtools:
	def get_node_links(operator, context, ht):
		link_ref = lambda node, socket: f'{node.name}.{socket.name.replace(" ", "-")}'
		int_tuple = lambda t: tuple(int(e) for e in t)

		if not context.selected_nodes:
			return

		#There might not be an active node so we will use first node in selection instead
		#node_tree = context.active_node.id_data
		node_tree = context.selected_nodes[0].id_data

		result = list()
		result.append('#Node definitions')
		for node in context.selected_nodes:
			result.append(f'{node.bl_idname}\t{node.name}')
		result.append('')

		result.append('#Node locations')
		for node in context.selected_nodes:
			result.append(f'{node.name}.location = {int_tuple(node.location)}')
		result.append('')

		result.append('#Node links')
		for link in node_tree.links:
			result.append(f'{link_ref(link.from_node, link.from_socket)} --> {link_ref(link.to_node, link.to_socket)}')


		body = textwrap.indent('\n'.join(result), '\t')
		log.info(f'Node data:\n\n{body}')