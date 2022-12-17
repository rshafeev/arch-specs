import logging
from typing import Optional, Set, List, Tuple

from content.page.handbook.network.basic.view import NetworkBasicPageView
from content.page.handbook.network.network_pablisher_core import NetworkPagePublisherCore
from core.git.branch import Branch
from core.struct_helper import array_to_set
from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.model.title import NetworkBasicPageTitle
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage


class NetworkBasicPublisher(NetworkPagePublisherCore):
    __branch: Branch

    __html_templates_storage: HtmlTemplatesStorage

    __max_releases_cnt: int

    __page_view: NetworkBasicPageView

    def __init__(self,
                 confluence: ConfluenceService,
                 branch: Branch,
                 html_templates_storage: HtmlTemplatesStorage,
                 max_releases_cnt: int):
        super().__init__(confluence)
        self.__html_templates_storage = html_templates_storage
        self.__branch = branch
        self.__max_releases_cnt = max_releases_cnt
        self.__page_view = NetworkBasicPageView(html_templates_storage)

    @classmethod
    def make_branch_from_network_page_title(cls,
                                            title: str) -> Optional[Branch]:
        ind_start = title.find('[')
        ind_end = title.find(']')
        if ind_end < 0 or ind_end < 0 or ind_end < ind_start:
            return None
        branch_name = title[ind_start + 1:ind_end]
        if branch_name == 'current':
            return None
        return Branch(branch_name)

    @staticmethod
    def title(spec: ServiceSpecExt):
        return NetworkBasicPageTitle.title(spec)

    async def __remove_deprecated_branch_pages(self, release_pages: List[dict], release_branches: Set[Branch]):
        for e in release_pages:
            should_delete = True
            if e['branch'] in release_branches:
                should_delete = False
            if should_delete is True:
                await self._confluence.pages.delete(e['page'].id)

    async def __prepare_page(self, spec: ServiceSpecExt, page: ConfluencePage,
                             handbook_page: ConfluencePage) -> Tuple[ConfluencePage, Set[Branch], Branch]:
        available_release_branches = set()
        release_pages = []
        has_master_branch = False
        if page.id is None:
            has_master_branch = True
        else:
            page.childs = await self._confluence.pages.childs(page.id)
            for ch in page.childs:
                branch = self.make_branch_from_network_page_title(ch.title)
                if branch is None:
                    continue
                if branch.is_release:
                    release_pages.append({
                        "page": ch,
                        "branch": branch
                    })
                    available_release_branches.add(branch)
                elif branch.is_master:
                    has_master_branch = True
        if self.__branch.is_master:
            has_master_branch = True
        elif self.__branch.is_release and spec.is_pro:
            available_release_branches.add(self.__branch)
        release_branches_arr = Branch.latest_release_branches(available_release_branches, self.__max_releases_cnt)
        page.space_key = spec.settings.confluence.space
        page.parent_id = handbook_page.id
        page.body = await self.__page_view.render(spec, release_branches_arr, has_master_branch)
        release_branches = array_to_set(release_branches_arr)
        await self.__remove_deprecated_branch_pages(release_pages, release_branches)
        selected_branch = Branch.selected(release_branches_arr, has_master_branch)
        return page, release_branches, selected_branch

    async def publish(self, spec: ServiceSpecExt, handbook_page: ConfluencePage, force_recreate_network_pages: int) -> Tuple[
        ConfluencePage, Set[Branch], Branch]:
        page = await self._confluence.pages.find(self.title(spec), spec.settings.confluence.space)
        if page is None and not self.__branch.is_master:
            raise Exception('''You try to create '{}' page for the service '{}' from the non-master branch '{}'!
                Please, create handbook page from the master branch!'''.format(
                self.title(spec), spec.service_name, self.__branch.name))
        if page is None:
            page = ConfluencePage()
            page.title = self.title(spec)
        page, release_branches, selected_branch = await self.__prepare_page(spec, page, handbook_page)
        if page.id:
            page = await self._update_page(page, force_recreate_network_pages)
        else:
            page = await self._create_page(page)
        return page, release_branches, selected_branch
