import argparse
import asyncio
import logging
import os

from core.app import AppCore
from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from core.specs.validate.specs_validator import SpecsValidator
from specs_generator.generator import SpecsGenerator


class App(AppCore):

    @staticmethod
    def prepare_args_parser():
        path = os.path.dirname(__file__)
        m_desc = "json specs generator"
        args_parser = argparse.ArgumentParser(
            fromfile_prefix_chars='@', description=m_desc, formatter_class=argparse.RawTextHelpFormatter)
        args_parser.add_argument(
            "-m", "--meta_path", dest="meta_path", help="meta_path", required=True)
        args_parser.add_argument(
            "-specs_repo_path", "--specs_repo_path", dest="specs_repo_path", help="specs_repo_path",
            default="../../arch_specs_autogen", required=False)
        args_parser.add_argument(
            "-c", "--config", dest="config", help="config", default=path + "/config/base.yaml",
            required=False)
        args_parser.add_argument('--validate', action='store_true')

        return args_parser

    def __init__(self):
        super().__init__(self.prepare_args_parser())

    async def run(self) -> int:
        if self.args.validate:
            specs_validator = SpecsValidator(self.args.meta_path)
            valid, errors, warns = specs_validator.validate()
            specs_validator.print(errors, warns)
            if valid is False:
                exit(1)

        current_branch = Branch(self.configuration["git"]["branch"])
        generator = SpecsGenerator(self.args.meta_path, self.configuration,
                                   GitSpecsRepositoryHelper.topics_info_fname(), current_branch)
        generator.save("{}/specs".format(self.args.specs_repo_path))
        return 0


async def main():
    app = App()
    return await app.run()


if __name__ == '__main__':
    asyncio.run(main())
