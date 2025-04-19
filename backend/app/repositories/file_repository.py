import os


def create_file(dir, name, file):
    path = dir + "/" + name
    os.mkdir(dir)
    with open(path, "wb") as f:
        f.write(file)
    return path
