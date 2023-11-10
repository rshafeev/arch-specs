import argparse
import asyncio
import logging
import os

from branch_cleaner import BranchCleaner
from core.app import AppCore
from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from core.specs.specs import ServicesSpecs
from data.confluence.service import ConfluenceService
from data.specs.owners_validator import OwnersValidator
from data.template.templates_storage import HtmlTemplatesStorage
from publisher import PagesPublisher


class App(AppCore):

    @staticmethod
    def prepare_args_parser():
        path = os.path.dirname(__file__)
        m_desc = "Confluence Pages Publisher"
        args_parser = argparse.ArgumentParser(
            fromfile_prefix_chars='@', description=m_desc, formatter_class=argparse.RawTextHelpFormatter)
        args_parser.add_argument(
            "-c", "--config", dest="config", help="config", default=path + "/../config/base.yaml",
            required=False)
        args_parser.add_argument(
            "-m", "--meta_path", dest="meta_path", help="meta_path", required=True)
        args_parser.add_argument(
            "--cache_path", "--cache_path", dest="cache_path", help="cache_path", default="/tmp", required=False,)
        args_parser.add_argument(
            "--html_templates_path", "--html_templates_path", dest="html_templates_path",
            help="html_templates_path", default=path + "/../res/template-onprem", required=False)
        args_parser.add_argument(
            "-s", "--specs_repo_path", dest="specs_repo_path", help="specs_repo_path", required=True)
        args_parser.add_argument('--validate_only', action='store_true')
        args_parser.add_argument('--publish_only_diagrams', action='store_true')

        args_parser.add_argument(
            "--removed_branch", "--removed_branch", dest="removed_branch",
            help="removed_branch", default="", required=False)
        return args_parser

    def __init__(self):
        super().__init__(self.prepare_args_parser())
        GitSpecsRepositoryHelper.repo_path = self.args.specs_repo_path


    @property
    def max_parallel_tasks_cnt(self):
        return self.configuration['app']['max_parallel_tasks_cnt']

    @property
    def max_releases_cnt(self):
        return self.configuration['publish']['max_releases_cnt']

    async def run(self):
        confluence = None
        try:
            current_branch = Branch(self.configuration["git"]["branch"])
            cache_path = self.args.cache_path
            confluence = ConfluenceService(self.configuration['confluence'])

            services_specs = ServicesSpecs(self.args.meta_path, GitSpecsRepositoryHelper.topics_info_fname(),
                                               current_branch)

            validator = OwnersValidator(services_specs, confluence, cache_path)
            valid, errors = await validator.validate()
            if valid is False:
                logging.error("Owner`s names Validation - FAILED")
                return 1
            if self.args.validate_only:
                logging.info("Owner`s names Validation - OK")
                return 0

            if self.args.removed_branch != "":
                logging.info("Clean branch mode. Starting...")
                cleaner = BranchCleaner(services_specs, confluence)
                await cleaner.remove_branch_pages(self.args.removed_branch)
                logging.info("Clean branch mode - OK")
                return 0

            if not current_branch.is_master and not current_branch.is_release:
                raise Exception("You try to execute confluence_publisher utility for the non-master/non-release "
                                "branch '{}'!".format(current_branch.name) +
                                "Please, checkout git repository to the master or release branch and try again!")
            html_templates_storage = HtmlTemplatesStorage(self.args.html_templates_path)
            confluence_pages = PagesPublisher(html_templates_storage,
                                              self.max_releases_cnt,
                                              self.configuration,
                                              services_specs,
                                              confluence,
                                              self.max_parallel_tasks_cnt,
                                              current_branch,
                                              cache_path,
                                              self.args.publish_only_diagrams)
            await confluence_pages.publish()
        finally:
            if confluence is not None:
                await confluence.release()


async def main():
    try:
        app = App()
        await app.run()
    except Exception as e:
        logging.error(e, exc_info=True)
        exit(1)


if __name__ == '__main__':
    asyncio.run(main())
