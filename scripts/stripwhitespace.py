import pathlib

for file in pathlib.Path(".").glob("**/*.py"):
    print(f"Stripping {file}")
    try:
        with open(file, "r") as f:
            lines = [l.rstrip() for l in f.read().splitlines()]
        with open(file, "w") as f:
            [f.write(f"{l}\n") for l in lines]
    except UnicodeDecodeError as e:
        print(f"\t{file}: {e}")
