import logging
from typing import Set

from content.page.diagram.publisher import DiagramPublisher
from content.page.entire_handbook.publisher import EntireHandbookPagePublisher
from content.page.handbook.network.basic.publisher import NetworkBasicPublisher
from content.page.handbook.network.branch.diagram.publisher import NetworkBranchDiagramPublisher
from content.page.handbook.network.branch.links.publisher import NetworkBranchLinksPublisher
from content.page.handbook.network.branch.publisher import NetworkBranchPublisher
from content.page.handbook.network.current.diagram.publisher import NetworkCurrentDiagramPublisher
from content.page.handbook.network.current.links.publisher import NetworkCurrentLinksPublisher
from content.page.handbook.network.current.publisher import NetworkCurrentPublisher
from content.page.handbook.publisher import HandbookPagePublisher
from content.page.system.branch.diagram.publisher import SystemNetworkBranchDiagramPublisher
from core.git.branch import Branch
from core.specs.service.spec import ServiceType
from core.specs.specs import ServicesSpecs
from core.task.task_pool import TasksPool
from data.confluence.cache.users_keys_cache_storage import UsersKeysCacheStorage
from data.confluence.model.page import ConfluencePage
from data.confluence.model.title import ServiceHandbookPageTitle
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage


class PagesPublisher:
    __services_specs: ServicesSpecs

    __html_templates_storage: HtmlTemplatesStorage

    __max_releases_cnt: int

    __wiki_pages: list

    __user_keys_storage: UsersKeysCacheStorage

    __confluence: ConfluenceService

    __app_configuration: dict

    __max_parallel_tasks_cnt: int

    __branch: Branch

    __publish_only_diagrams: bool

    def __init__(self,
                 html_templates_storage: HtmlTemplatesStorage,
                 max_releases_cnt: int,
                 app_configuration: dict,
                 services_specs: ServicesSpecs,
                 confluence: ConfluenceService,
                 max_parallel_tasks_cnt: int,
                 branch: Branch,
                 cache_path: str,
                 publish_only_diagrams: bool):
        self.__html_templates_storage = html_templates_storage
        self.__max_releases_cnt = max_releases_cnt
        self.__confluence = confluence
        self.__services_specs = services_specs
        self.__app_configuration = app_configuration
        self.__max_parallel_tasks_cnt = max_parallel_tasks_cnt
        self.__branch = branch
        self.__user_keys_storage = UsersKeysCacheStorage(self.__confluence, cache_path)
        self.__publish_only_diagrams = publish_only_diagrams

    @property
    def branch(self) -> Branch:
        return self.__branch

    async def publish(self):
        await self.__clean_services()
        await self.__publish_pages()

    async def __publish_pages(self):
        tasks_pool = TasksPool(self.__max_parallel_tasks_cnt)
        is_entire_handbook_page = self.__services_specs.settings.confluence.is_entire_handbook_page
        if self.__services_specs.settings.confluence.diagrams:
            for diagram_settings in self.__services_specs.settings.confluence.diagrams:
                await tasks_pool.append(self.__publish_diagram_page(diagram_settings))
        if not self.__publish_only_diagrams:
            await tasks_pool.append(self.__publish_system_diagram_pages())
            await self.__publish_category_pages()
            for service_name in self.__services_specs.all_services:
                service_spec = ServiceSpecExt.create(self.__services_specs.get_service_spec(service_name),
                                                     self.__user_keys_storage)
                if service_spec.service_module in ['external']:
                    continue
                if self.__app_configuration["publish"]["service"] != 'all' and \
                        self.__app_configuration["publish"]["service"] != service_spec.service_name:
                    continue
                if is_entire_handbook_page:
                    await tasks_pool.append(self.__publish_service_entire_page(service_spec))
                else:
                    await tasks_pool.append(self.__publish_service_pages(service_spec))
        await tasks_pool.done()

    async def __publish_category_pages(self):
        settings = self.__services_specs.settings
        parent_page_title = settings.confluence.handbook_page_title
        parent_page = await self.__confluence.pages.find(parent_page_title, settings.confluence.space)
        if parent_page is None:
            raise Exception("Could not find Handbook Services Page")

        for category_name in settings.service_categories.product_services:
            category_page_title = f"{settings.confluence.module_prefix}{category_name}"
            page = await self.__confluence.pages.find(category_page_title,
                                                      settings.confluence.space)
            if page is not None:
                continue
            page = ConfluencePage()
            page.title = category_page_title
            page.space_key = self.__services_specs.settings.confluence.space
            page.body = ""
            page.parent_id = parent_page.id
            await self.__confluence.pages.create(page)

    async def __publish_system_diagram_pages(self):
        network_page_publisher = SystemNetworkBranchDiagramPublisher(self.__confluence,
                                                                     self.branch,
                                                                     self.__html_templates_storage,
                                                                     self.__services_specs.settings)
        wiki_space = self.__services_specs.settings.confluence.space
        handbook_page_title = self.__services_specs.settings.confluence.handbook_page_title
        handbook_page = await self.__confluence.pages.find(handbook_page_title, wiki_space)
        title = self.__services_specs.settings.confluence.system_diagram_page_title
        await network_page_publisher.publish(handbook_page, title)

    async def __clean_services(self):
        wiki_space = self.__services_specs.settings.confluence.space
        for service_name in self.__services_specs.settings.confluence.clean_services:
            page = await self.__confluence.pages.find(service_name, wiki_space)
            if page:
                await self.__confluence.pages.delete(page.id)

    async def __publish_diagram_page(self, diagram_settings: dict):
        page_publisher = DiagramPublisher(self.__confluence,
                                          self.branch,
                                          self.__html_templates_storage,
                                          self.__services_specs.settings,
                                          diagram_settings)
        await page_publisher.publish()

    async def __publish_service_entire_page(self, spec: ServiceSpecExt):
        force_recreate_handbook = self.__app_configuration['publish']['force_recreate_handbook']
        force_rewrite_handbook_properties = self.__app_configuration['publish']['force_rewrite_handbook_properties']
        force_recreate_network_pages = self.__app_configuration['publish']['force_recreate_network_pages']
        handbook_page_publisher = EntireHandbookPagePublisher(self.__confluence,
                                                              self.branch,
                                                              self.__html_templates_storage)
        handbook_page = await handbook_page_publisher.publish(spec,
                                                              force_recreate_handbook,
                                                              force_rewrite_handbook_properties)
        logging.info("[{}]: done".format(spec.service_name))

    async def __publish_service_pages(self, spec: ServiceSpecExt):
        force_recreate_handbook = self.__app_configuration['publish']['force_recreate_handbook']
        force_rewrite_handbook_properties = self.__app_configuration['publish']['force_rewrite_handbook_properties']
        force_recreate_network_pages = self.__app_configuration['publish']['force_recreate_network_pages']
        handbook_page_publisher = HandbookPagePublisher(self.__confluence,
                                                        self.branch,
                                                        self.__html_templates_storage)
        handbook_page = await handbook_page_publisher.publish(spec,
                                                              force_recreate_handbook,
                                                              force_rewrite_handbook_properties)
        if spec.unavailable:
            return

        network_basic_publisher = NetworkBasicPublisher(self.__confluence,
                                                        self.branch,
                                                        self.__html_templates_storage,
                                                        self.__max_releases_cnt)
        network_basic_page, release_branches, selected_branch = await network_basic_publisher.publish(spec,
                                                                                                      handbook_page,
                                                                                                      force_recreate_network_pages)

        await self.__publish_service_network_branch_pages(spec, network_basic_page, release_branches)
        await self.__publish_service_network_current_pages(spec, network_basic_page, selected_branch)
        logging.info("[{}]: done".format(spec.service_name))

    async def __publish_service_network_branch_pages(self,
                                                     spec: ServiceSpecExt,
                                                     network_basic_page: ConfluencePage,
                                                     release_branches: Set[Branch]):
        force_recreate_network_pages = self.__app_configuration['publish']['force_recreate_network_pages']
        if self.branch.is_master or self.branch in release_branches:
            network_branch_publisher = NetworkBranchPublisher(self.__confluence,
                                                              self.branch,
                                                              self.__html_templates_storage)
            network_branch_page = await network_branch_publisher.publish(spec,
                                                                         network_basic_page,
                                                                         force_recreate_network_pages)
            network_branch_links_publisher = NetworkBranchLinksPublisher(self.__confluence,
                                                                         self.branch,
                                                                         self.__html_templates_storage)
            network_branch_links_page = await network_branch_links_publisher.publish(spec,
                                                                                     network_branch_page,
                                                                                     force_recreate_network_pages)
            network_branch_diagram_publisher = NetworkBranchDiagramPublisher(self.__confluence,
                                                                             self.branch,
                                                                             self.__html_templates_storage)
            network_branch_diagram_page = await network_branch_diagram_publisher.publish(spec,
                                                                                         network_branch_page,
                                                                                         force_recreate_network_pages)

    async def __publish_service_network_current_pages(self,
                                                      spec: ServiceSpecExt,
                                                      network_basic_page: ConfluencePage,
                                                      selected_branch: Branch):
        force_recreate_network_pages = self.__app_configuration['publish']['force_recreate_network_pages']
        network_current_publisher = NetworkCurrentPublisher(self.__confluence,
                                                            self.branch,
                                                            self.__html_templates_storage)
        network_current_page = await network_current_publisher.publish(spec, network_basic_page,
                                                                       force_recreate_network_pages)

        network_current_links_publisher = NetworkCurrentLinksPublisher(self.__confluence,
                                                                       self.branch,
                                                                       self.__html_templates_storage)
        network_current_links_page = await network_current_links_publisher.publish(spec,
                                                                                   network_current_page,
                                                                                   selected_branch,
                                                                                   force_recreate_network_pages)
        network_current_diagram_publisher = NetworkCurrentDiagramPublisher(self.__confluence,
                                                                           self.branch,
                                                                           self.__html_templates_storage)
        network_current_diagram_page = await network_current_diagram_publisher.publish(spec,
                                                                                       network_current_page,
                                                                                       selected_branch,
                                                                                       force_recreate_network_pages)
