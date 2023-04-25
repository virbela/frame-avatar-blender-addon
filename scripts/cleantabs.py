import pathlib

src = pathlib.Path(__file__).parent.parent / "src"

test = src / "utils" / "properties.py"

with open(test, 'r') as file:
    newlines = []
    for line in file.readlines():
        newlines.append(line.replace('\t', '    '))

with open(test, 'w') as file:
    file.writelines(newlines)
