import pathlib

for file in pathlib.Path(".").glob("**/*.py"):
    print(f"Stripping {file}")
    try:
        with open(file, "r") as f:
            lines = [line.rstrip() for line in f.read().splitlines()]
        with open(file, "w") as f:
            [f.write(f"{line}\n") for line in lines]
    except UnicodeDecodeError as e:
        print(f"\t{file}: {e}")
