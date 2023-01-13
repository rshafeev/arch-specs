import logging

from content.page.system.branch.diagram.view import SystemNetworkBranchDiagramView
from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from core.specs.settings import Settings, ConfluenceSettings
from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.service import ConfluenceService
from data.template.templates_storage import HtmlTemplatesStorage


class DiagramPublisher:
    __branch: Branch

    __html_templates_storage: HtmlTemplatesStorage

    __confluence: ConfluenceService

    __page_view: SystemNetworkBranchDiagramView

    __settings: Settings

    __diagram_settings: dict


    def __init__(self,
                 confluence: ConfluenceService,
                 branch: Branch,
                 html_templates_storage: HtmlTemplatesStorage,
                 settings: Settings,
                 diagram_settings: dict):
        self.__confluence = confluence
        self.__html_templates_storage = html_templates_storage
        self.__branch = branch
        self.__settings = settings
        self.__diagram_settings = diagram_settings
        self.__page_view = SystemNetworkBranchDiagramView(html_templates_storage)

    @property
    def title(self):
        return self.__diagram_settings["title"]

    @property
    def wiki_space(self) -> str:
        if "space" in self.__diagram_settings:
            return self.__diagram_settings["space"]
        return self.__settings.confluence.space

    @property
    def diagram_fname(self) -> str:
        return f'{self.__settings.meta_path}/diagrams/{self.__diagram_settings["diagram"]}'

    async def __prepare_page(self,
                             page: ConfluencePage,
                             parent_page: ConfluencePage,
                             current_branch: Branch) -> ConfluencePage:

        page.space_key = self.wiki_space
        page.parent_id = parent_page.id
        page.body = await self.__page_view.render(current_branch)
        return page

    async def publish(self) -> ConfluencePage:
        parent_title = self.__diagram_settings["parent_page"]
        parent_page = await self.__confluence.pages.find(parent_title, self.wiki_space)
        page = await self.__confluence.pages.find(self.title, self.wiki_space)
        if page is None and not self.__branch.is_master and not self.__branch.is_release:
            raise Exception(f'''You try to create '{self.title}' page from the non-master/non-release branch '{self.__branch.name}'!
                Please, create handbook page from the master or release branch!''')

        if page is None:
            page = ConfluencePage()
            page.title = self.title
        page = await self.__prepare_page(page, parent_page, self.__branch)
        if page.id:
            await self.__confluence.pages.update(page)
            logging.info("Component Page '{}' was updated.".format(page.title))
        else:
            await self.__confluence.pages.create(page)
            logging.info("Component Page '{}' was created.".format(page.title))

        diagram_confluence_name = "{}_diagram".format(SystemNetworkBranchDiagramView.diagram_name)
        diagram_attachment = await self.__confluence.attachments.get(page.id, diagram_confluence_name)
        repo_diagram_hash_commit = await GitSpecsRepositoryHelper.file_hash(self.diagram_fname)
        logging.info(
            "Page '{}'. Current The draw.io component diagram hash: {}".format(page.title, repo_diagram_hash_commit))
        if diagram_attachment is None:
            await self.__confluence.attachments.create(page.id, self.diagram_fname, diagram_confluence_name)
            await self.__confluence.properties.set(page.id, PropertyKey.network_diagram_hash, repo_diagram_hash_commit)
            logging.info("Page '{}'. The draw.io component diagram was created.".format(page.title))
        else:
            confluenece_diagram_hash = await self.__confluence.properties.get(page.id, PropertyKey.network_diagram_hash)
            if confluenece_diagram_hash is None or confluenece_diagram_hash != repo_diagram_hash_commit:
                await self.__confluence.attachments.update(page.id, diagram_attachment['id'], self.diagram_fname,
                                                           diagram_confluence_name)
                await self.__confluence.properties.set(page.id, PropertyKey.network_diagram_hash,
                                                       repo_diagram_hash_commit)
                logging.info("Page '{}'. The draw.io component diagram was updated.".format(page.title))
            else:
                logging.info("Page '{}'. The draw.io component diagram is not changed [CACHE].".format(page.title))

        return page
