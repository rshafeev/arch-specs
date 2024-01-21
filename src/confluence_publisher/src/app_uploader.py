import argparse
import asyncio
import logging
import os

from branch_cleaner import BranchCleaner
from core.app import AppCore
from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from core.specs.specs import ServicesSpecs
from data.confluence.model.page import ConfluencePage
from data.confluence.service import ConfluenceService
from data.specs.owners_validator import OwnersValidator
from data.template.templates_storage import HtmlTemplatesStorage
from publisher import PagesPublisher


class App(AppCore):

    @staticmethod
    def prepare_args_parser():
        path = os.path.dirname(__file__)
        m_desc = "Confluence Pages Uploader"
        args_parser = argparse.ArgumentParser(
            fromfile_prefix_chars='@', description=m_desc, formatter_class=argparse.RawTextHelpFormatter)
        args_parser.add_argument(
            "-c", "--config", dest="config", help="config", default=path + "/../config/base.yaml",
            required=False)
        args_parser.add_argument(
            "-page_id", "--page_id", dest="page_id", help="page_id", required=True)
        args_parser.add_argument(
            "--recursive", "--recursive", dest="recursive", help="recursive", default=False, required=False,)
        args_parser.add_argument(
            "--input_xml_file", "--input_xml_file", dest="input_xml_file", help="input_xml_file", default="", required=False,)
        return args_parser

    def __init__(self):
        super().__init__(self.prepare_args_parser())


    def safe_title(self, page_title: str):
        return page_title.replace("/", "_")
    async def _upload_page(self, confluence, page_id, input_xml_file) -> ConfluencePage:
        with open(input_xml_file, 'r') as file:
            xml_data = file.read().rstrip()
        page = await confluence.pages.get_page(page_id)
        page.body = xml_data
        page = await confluence.pages.update(page)
        return page

    async def run(self):
        confluence = None
        try:
            confluence = ConfluenceService(self.configuration['confluence'])
            page_id = self.args.page_id
            input_xml_file = self.args.input_xml_file
            await self._upload_page(confluence, page_id, input_xml_file)
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
