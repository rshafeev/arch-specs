import logging

from content.page.handbook.network.basic.publisher import NetworkBasicPublisher
from core.specs.specs import ServicesSpecs
from data.confluence.model.title import NetworkBasicPageTitle
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt


class BranchCleaner:
    __services_specs: ServicesSpecs

    __confluence: ConfluenceService

    @staticmethod
    def title(service_name: str):
        return "{}: communication".format(service_name)

    def __init__(self, services_specs: ServicesSpecs,
                confluence: ConfluenceService):
        self.__confluence = confluence
        self.__services_specs = services_specs

    async def remove_branch_pages(self, remove_branch: str):
        for service_name in self.__services_specs.all_services:
            await self.__remove_branch_pages(service_name, remove_branch)

    async def __remove_branch_pages(self, service_name: str, remove_branch: str):
        page = await self.__confluence.pages.find(self.title(service_name), self.__services_specs.settings.confluence.space)
        if page is None or page.id is None:
            return
        page.childs = await self.__confluence.pages.childs(page.id)
        for ch in page.childs:
            branch = NetworkBasicPublisher.make_branch_from_network_page_title(ch.title)
            if branch is None:
                continue
            if branch.name == remove_branch:
                logging.info("Needs to remove: {}".format(ch.title))
                await self.__confluence.pages.delete(ch.id)
