import logging

from content.page.system.branch.diagram.view import SystemNetworkBranchDiagramView
from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from core.specs.settings import Settings
from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.model.title import SystemNetworkBranchDiagramPageTitle
from data.confluence.service import ConfluenceService
from data.template.templates_storage import HtmlTemplatesStorage


class SystemNetworkBranchDiagramPublisher:
    __branch: Branch

    __html_templates_storage: HtmlTemplatesStorage

    __confluence: ConfluenceService

    __page_view: SystemNetworkBranchDiagramView

    __specs_settings: Settings

    def __init__(self,
                 confluence: ConfluenceService,
                 branch: Branch,
                 html_templates_storage: HtmlTemplatesStorage,
                 specs_settings: Settings):
        self.__confluence = confluence
        self.__html_templates_storage = html_templates_storage
        self.__branch = branch
        self.__specs_settings = specs_settings
        self.__page_view = SystemNetworkBranchDiagramView(html_templates_storage)

    async def __prepare_page(self,
                             page: ConfluencePage,
                             network_branch_page: ConfluencePage,
                             current_branch: Branch) -> ConfluencePage:

        page.space_key = self.__specs_settings.confluence.space
        page.parent_id = network_branch_page.id
        page.body = await self.__page_view.render(current_branch)
        return page

    async def publish(self, parent_page: ConfluencePage, title: str) -> ConfluencePage:
        page = await self.__confluence.pages.find(title, self.__specs_settings.confluence.space)
        if page is None and not self.__branch.is_master and not self.__branch.is_release:
            raise Exception(f'''You try to create '{title}' page from the non-master/non-release branch '{self.__branch.name}'!
                Please, create handbook page from the master or release branch!''')

        if page is None:
            page = ConfluencePage()
            page.title = title
        page = await self.__prepare_page(page, parent_page, self.__branch)
        if page.id:
            await self.__confluence.pages.update(page)
            logging.info("Page '{}' was updated.".format(page.title))
        else:
            await self.__confluence.pages.create(page)
            logging.info("Page '{}' was created.".format(page.title))

        diagram_file_name = GitSpecsRepositoryHelper.system_diagram_fname()
        diagram_confluence_name = "{}_diagram".format(SystemNetworkBranchDiagramView.diagram_name)
        diagram_attachment = await self.__confluence.attachments.get(page.id, diagram_confluence_name)
        repo_diagram_hash_commit = await GitSpecsRepositoryHelper.file_hash(diagram_file_name)
        logging.info(
            "Page '{}'. Current The draw.io network diagram hash: {}".format(page.title, repo_diagram_hash_commit))
        if diagram_attachment is None:
            await self.__confluence.attachments.create(page.id, diagram_file_name, diagram_confluence_name)
            await self.__confluence.properties.set(page.id, PropertyKey.network_diagram_hash, repo_diagram_hash_commit)
            logging.info("Page '{}'. The draw.io network diagram was created.".format(page.title))
        else:
            confluenece_diagram_hash = await self.__confluence.properties.get(page.id, PropertyKey.network_diagram_hash)
            if confluenece_diagram_hash is None or confluenece_diagram_hash != repo_diagram_hash_commit:
                await self.__confluence.attachments.update(page.id, diagram_attachment['id'], diagram_file_name,
                                                           diagram_confluence_name)
                await self.__confluence.properties.set(page.id, PropertyKey.network_diagram_hash,
                                                       repo_diagram_hash_commit)
                logging.info("Page '{}'. The draw.io network diagram was updated.".format(page.title))
            else:
                logging.info("Page '{}'. The draw.io network diagram is not changed [CACHE].".format(page.title))

        return page
