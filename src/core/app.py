import argparse
import logging
from functools import wraps
from time import time

from core.config.loader import ConfigurationLoader
from core.git.specs_repo import GitSpecsRepositoryHelper


class AppCore:
    args = None

    __configuration: dict

    def __init__(self, args_parser: argparse.ArgumentParser):
        self.args = args_parser.parse_args()
        self.__configuration = ConfigurationLoader.load(self.args.config)
        self.set_basic_logging()
        GitSpecsRepositoryHelper.repo_path = self.args.specs_repo_path

    def set_basic_logging(self):
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s [%(module)s:%(funcName)s()]  %(message)s',
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger().setLevel(self.configuration['logging']['level'])

    @property
    def configuration(self) -> dict:
        return self.__configuration


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' %
              (f.__name__, args, kw, te - ts))
        return result

    return wrap
