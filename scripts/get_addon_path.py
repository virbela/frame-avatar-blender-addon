import bpy
import sys, argparse
from pathlib import Path

def get_args():
	try:
		argument_delimiter = sys.argv.index('--')
		pre_args = sys.argv[:argument_delimiter]
		args = sys.argv[argument_delimiter+1:]
	except ValueError:
		args = list()
		pre_args = sys.argv

	parser = argparse.ArgumentParser(prog=f'{" ".join(pre_args)} --')
	parser.add_argument("output", type=Path, help='File to write script dir to')
	return parser.parse_args(args)

args = get_args()
with args.output.open('w') as outfile:
	print(Path(bpy.utils.user_resource('SCRIPTS')) / 'addons', file=outfile)
