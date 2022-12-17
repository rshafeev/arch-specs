import yaml


def read_yaml(fname: str):
    with open(fname, 'r') as stream:
        return yaml.safe_load(stream)