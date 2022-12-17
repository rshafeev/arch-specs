import logging

from content.page.handbook.network.branch.view import NetworkBranchView
from content.page.handbook.network.network_pablisher_core import NetworkPagePublisherCore
from core.git.branch import Branch
from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.model.title import NetworkBranchPageTitle
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage


class NetworkBranchPublisher(NetworkPagePublisherCore):
    __branch: Branch

    __html_templates_storage: HtmlTemplatesStorage

    __page_view: NetworkBranchView

    def __init__(self,
                 confluence: ConfluenceService,
                 branch: Branch,
                 html_templates_storage: HtmlTemplatesStorage):
        super().__init__(confluence)
        self.__html_templates_storage = html_templates_storage
        self.__branch = branch
        self.__page_view = NetworkBranchView(html_templates_storage)

    @staticmethod
    def title(spec: ServiceSpecExt, branch: Branch):
        return NetworkBranchPageTitle.title(spec, branch)

    async def __prepare_page(self,
                             spec: ServiceSpecExt,
                             page: ConfluencePage,
                             network_basic_page: ConfluencePage,
                             current_branch: Branch) -> ConfluencePage:
        page.space_key = spec.settings.confluence.space
        page.parent_id = network_basic_page.id
        page.body = await self.__page_view.render(spec, current_branch)
        return page

    async def publish(self,
                      spec: ServiceSpecExt,
                      network_basic_page: ConfluencePage,
                      force_recreate_network_pages: int) -> ConfluencePage:
        page = await self._confluence.pages.find(self.title(spec, self.__branch),
                                                  spec.settings.confluence.space)
        if page is None and not self.__branch.is_master and not self.__branch.is_release:
            raise Exception('''You try to create '{}' page for the service '{}' from the non-master/non-release 
            branch '{}'! Please, create handbook page from the master or release branch!'''.format(
                self.title(spec, self.__branch), spec.service_name, self.__branch.name))

        if page is None:
            page = ConfluencePage()
            page.title = self.title(spec, self.__branch)
        page = await self.__prepare_page(spec, page, network_basic_page, self.__branch)
        if page.id:
            page = await self._update_page(page, force_recreate_network_pages)
        else:
            page = await self._create_page(page)
        return page
