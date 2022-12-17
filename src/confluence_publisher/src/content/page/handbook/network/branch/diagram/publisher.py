import logging

from content.page.handbook.network.branch.diagram.view import NetworkBranchDiagramView
from content.page.handbook.network.network_pablisher_core import NetworkPagePublisherCore
from core.git.branch import Branch
from core.git.specs_repo import GitSpecsRepositoryHelper
from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.model.title import NetworkBranchDiagramPageTitle
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage


class NetworkBranchDiagramPublisher(NetworkPagePublisherCore):
    __branch: Branch

    __html_templates_storage: HtmlTemplatesStorage

    __page_view: NetworkBranchDiagramView

    def __init__(self,
                 confluence: ConfluenceService,
                 branch: Branch,
                 html_templates_storage: HtmlTemplatesStorage):
        super().__init__(confluence)
        self.__html_templates_storage = html_templates_storage
        self.__branch = branch
        self.__page_view = NetworkBranchDiagramView(html_templates_storage)

    @staticmethod
    def title(spec: ServiceSpecExt, branch: Branch):
        return NetworkBranchDiagramPageTitle.title(spec, branch)

    async def __prepare_page(self,
                             spec: ServiceSpecExt,
                             page: ConfluencePage,
                             network_branch_page: ConfluencePage,
                             current_branch: Branch) -> ConfluencePage:

        page.space_key = spec.settings.confluence.space
        page.parent_id = network_branch_page.id
        page.body = await self.__page_view.render(spec, current_branch)
        return page

    async def publish(self,
                      spec: ServiceSpecExt,
                      network_branch_page: ConfluencePage, force_recreate_network_pages: int) -> ConfluencePage:
        page = await self._confluence.pages.find(self.title(spec, self.__branch), spec.settings.confluence.space)
        if page is None and not self.__branch.is_master and not self.__branch.is_release:
            raise Exception('''You try to create '{}' page for the service '{}' from the non-master/non-release 
            branch '{}'! Please, create handbook page from the master or release branch!'''.format(
                self.title(spec, self.__branch), spec.service_name, self.__branch.name))

        if page is None:
            page = ConfluencePage()
            page.title = self.title(spec, self.__branch)
        page = await self.__prepare_page(spec, page, network_branch_page, self.__branch)
        if page.id:
            page = await self._update_page(page, force_recreate_network_pages)
        else:
            page = await self._create_page(page)

        diagram_file_name = GitSpecsRepositoryHelper.diagram_fname(spec.service_name)
        diagram_confluence_name = "{}_network_diagram".format(spec.service_name)
        diagram_attachment = await self._confluence.attachments.get(page.id, diagram_confluence_name)
        repo_diagram_hash_commit = await GitSpecsRepositoryHelper.file_hash(
            GitSpecsRepositoryHelper.diagram_fname(spec.service_name))
        logging.info(
            "Page '{}'. Current The draw.io network diagram hash: {}".format(page.title, repo_diagram_hash_commit))
        if diagram_attachment is None:
            await self._confluence.attachments.create(page.id, diagram_file_name, diagram_confluence_name)
            await self._confluence.properties.set(page.id, PropertyKey.network_diagram_hash, repo_diagram_hash_commit)

            logging.info("Page '{}'. The draw.io network diagram was created.".format(page.title))
        else:
            confluenece_diagram_hash = await self._confluence.properties.get(page.id, PropertyKey.network_diagram_hash)
            if confluenece_diagram_hash is None or confluenece_diagram_hash != repo_diagram_hash_commit:
                await self._confluence.pages.delete(page.id)
                logging.info("Page '{}' was deleted.".format(page.title))
                await self._confluence.pages.create(page)
                logging.info("Page '{}' was created.".format(page.title))
                await self._confluence.attachments.create(page.id, diagram_file_name, diagram_confluence_name)
                await self._confluence.properties.set(page.id, PropertyKey.network_diagram_hash,
                                                       repo_diagram_hash_commit)
                logging.info("Page '{}'. The draw.io network diagram was updated.".format(page.title))
            else:
                logging.info("Page '{}'. The draw.io network diagram is not changed [CACHE].".format(page.title))

        return page
