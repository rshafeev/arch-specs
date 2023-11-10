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
        m_desc = "Confluence Pages Downloader"
        args_parser = argparse.ArgumentParser(
            fromfile_prefix_chars='@', description=m_desc, formatter_class=argparse.RawTextHelpFormatter)
        args_parser.add_argument(
            "-c", "--config", dest="config", help="config", default=path + "/../config/base.yaml",
            required=False)
        args_parser.add_argument(
            "-root_page_id", "--root_page_id", dest="root_page_id", help="root_page_id", required=True)
        args_parser.add_argument(
            "--recursive", "--recursive", dest="recursive", help="recursive", default=False, required=False,)
        args_parser.add_argument(
            "--out_path", "--out_path", dest="out_path", help="out_path", default="tmp/download", required=False,)
        return args_parser

    def __init__(self):
        super().__init__(self.prepare_args_parser())


    def safe_title(self, page_title: str):
        return page_title.replace("/", "_")
    async def _download_page(self, confluence, page_id, out_path) -> ConfluencePage:
        page = await confluence.pages.get_page(page_id, expand="body,body.storage,body.view,container")
        logging.info(f"Download page: {page.title}. Path: {out_path}")

        os.makedirs(f"{out_path}/", exist_ok=True)
        with open(f"{out_path}/{self.safe_title(page.title)}.html", "w+") as f:
            f.write(page.body_view)
        with open(f"{out_path}/{self.safe_title(page.title)}_raw.xml", "w+") as f:
            f.write(page.body)
        attachments = await confluence.attachments.get_all(page_id, 1, 100)
        if attachments is None:
            return page
        attachments_path = f"{out_path}/{self.safe_title(page.title)}-attachments"
        os.makedirs(attachments_path, exist_ok=True)
        for attach in attachments:
            attach_title = attach['title']
            try:
                attach_content = await confluence.attachments.download(page_id, attach_title)
                with open(f"{attachments_path}/{attach_title}.xml", "wb+") as f:
                    f.write(attach_content)
            except Exception as e:
                logging.error(e)
                await confluence.release()

        return page

    async def _download_pages(self, confluence: ConfluenceService, page_id: str, out_path: str, recursive: bool):
        page = await self._download_page(confluence, page_id, out_path)
        if recursive is False:
            return
        childs = await confluence.pages.childs(page_id)
        for child in childs:
            ch_out_path = f"{out_path}/{self.safe_title(page.title)}"
            await self._download_pages(confluence, child.id, ch_out_path, recursive)
    async def run(self):
        confluence = None
        try:
            confluence = ConfluenceService(self.configuration['confluence'])
            root_page_id = self.args.root_page_id
            out_path = self.args.out_path
            recursive = bool(self.args.recursive)
            await self._download_pages(confluence, root_page_id, out_path, recursive)
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
