from content.page.handbook.network.current.links.view import NetworkCurrentLinksView
from content.page.handbook.network.network_pablisher_core import NetworkPagePublisherCore
from core.git.branch import Branch
from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.model.title import NetworkCurrentLinksPageTitle
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage


class NetworkCurrentLinksPublisher(NetworkPagePublisherCore):
    __branch: Branch

    __html_templates_storage: HtmlTemplatesStorage

    __page_view: NetworkCurrentLinksView

    def __init__(self,
                 confluence: ConfluenceService,
                 branch: Branch,
                 html_templates_storage: HtmlTemplatesStorage):
        super().__init__(confluence)
        self.__html_templates_storage = html_templates_storage
        self.__branch = branch
        self.__page_view = NetworkCurrentLinksView(html_templates_storage)

    @staticmethod
    def title(spec: ServiceSpecExt):
        return NetworkCurrentLinksPageTitle.title(spec)

    async def __prepare_page(self,
                             spec: ServiceSpecExt,
                             page: ConfluencePage,
                             network_current_page: ConfluencePage,
                             selected_branch: Branch) -> ConfluencePage:
        page.space_key = spec.settings.confluence.space
        page.parent_id = network_current_page.id
        page.body = await self.__page_view.render(spec, selected_branch)
        return page

    async def publish(self,
                      spec: ServiceSpecExt,
                      network_current_page: ConfluencePage,
                      selected_branch: Branch,
                      force_recreate_network_pages: int) -> ConfluencePage:
        page = await self._confluence.pages.find(self.title(spec), spec.settings.confluence.space)
        if page is None:
            page = ConfluencePage()
            page.title = self.title(spec)
        page = await self.__prepare_page(spec, page, network_current_page, selected_branch)
        if page.id:
            page = await self._update_page(page, force_recreate_network_pages)
        else:
            page = await self._create_page(page)
        return page
