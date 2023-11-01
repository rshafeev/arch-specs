import logging
from typing import Optional

from content.page.handbook.view import HandbookPageView
from core.git.branch import Branch
from core.specs.settings import ServiceCategoryNameWrapper
from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.model.title import ServiceHandbookManualPageTitle, ServiceHandbookPageTitle
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt
from data.template.templates_storage import HtmlTemplatesStorage


class HandbookPagePublisher:
    __branch: Branch

    __html_templates_storage: HtmlTemplatesStorage

    __page_view: HandbookPageView

    def __init__(self,
                 confluence: ConfluenceService,
                 branch: Branch,
                 html_templates_storage: HtmlTemplatesStorage):
        self.__confluence = confluence
        self.__html_templates_storage = html_templates_storage
        self.__branch = branch
        self.__page_view = HandbookPageView(html_templates_storage)

    async def __prepare_handbook_page(self, spec: ServiceSpecExt, page: Optional[ConfluencePage],
                                      force_recreate_handbook: int) -> ConfluencePage:
        parent_page_title = f"{spec.settings.confluence.module_prefix}{spec.category}"
        settings = spec.settings
        service_module_label = settings.confluence.module_label(spec.service_module)
        parent_page = await self.__confluence.pages.find(parent_page_title, spec.settings.confluence.space)
        if page is None:
            page = ConfluencePage()
            current_page_body_s = None
        else:
            current_page_body_s = page.body if force_recreate_handbook == 0 else None
        page.title = ServiceHandbookPageTitle.title(spec)
        page.space_key = spec.settings.confluence.space
        page.labels = [{"name": service_module_label, "prefix": "global"},
                       {"name": spec.service_name, "prefix": "global"},
                       {"name": 'service-{}-status'.format(spec.raw['status']), "prefix": "global"}]
        page.body = await self.__page_view.render(spec, current_page_body_s)
        page.parent_id = parent_page.id
        return page

    async def __create_handbook_manual_page(self, spec: ServiceSpecExt, parent_page: ConfluencePage):
        page = await self.__confluence.pages.find(ServiceHandbookManualPageTitle.title(spec), spec.settings.confluence.space)
        if page is not None:
            return
        page = ConfluencePage()
        page.title = ServiceHandbookManualPageTitle.title(spec)
        page.space_key = spec.settings.confluence.space
        page.body = ""
        page.parent_id = parent_page.id
        await self.__confluence.pages.create(page)

    async def publish(self,
                      spec: ServiceSpecExt,
                      force_recreate_handbook: int,
                      force_rewrite_handbook_properties: int) -> ConfluencePage:

        page = await self.__confluence.pages.find(ServiceHandbookPageTitle.title(spec), spec.settings.confluence.space)
        if page is None and not self.__branch.is_master:
            raise Exception('''You try to create handbook page for the service '{}' from the non-master branch '{}'!
                Please, create handbook page from the master branch!'''.format(
                spec.service_name, self.__branch.name))

        if self.__branch.is_master:
            if page is None:
                page = await self.__prepare_handbook_page(spec, page, force_recreate_handbook)
                await self.__confluence.pages.create(page)
                await self.__confluence.properties.set(page.id, PropertyKey.spec_hash, spec.hash)
                await self.__confluence.properties.set(page.id, PropertyKey.content_appearance_draft, "full-width")
                await self.__confluence.properties.set(page.id, PropertyKey.content_appearance_published, "full-width")
                logging.info("Page '{}' was created.".format(page.title))
            else:
                if force_recreate_handbook == 1:
                    await self.__confluence.properties.set(page.id, PropertyKey.content_appearance_draft, "full-width")
                    await self.__confluence.properties.set(page.id, PropertyKey.content_appearance_published,
                                                           "full-width")
                last_update_hash = await self.__confluence.properties.get(page.id, PropertyKey.spec_hash)
                current_hash = spec.hash
                if last_update_hash is None or \
                        last_update_hash != current_hash or \
                        force_recreate_handbook == 1 or \
                        force_rewrite_handbook_properties == 1:
                    page = await self.__prepare_handbook_page(spec, page, force_recreate_handbook=1)
                    await self.__confluence.pages.update(page)
                    logging.info("Page '{}' was updated.".format(page.title))
                    await self.__confluence.properties.set(page.id, PropertyKey.spec_hash, current_hash)
                else:
                    logging.info("Page '{}'. Current service spec hash: {}".format(page.title, last_update_hash))
                    logging.info("Page '{}'. Current service spec was not changed [CACHE].".format(page.title))
            await self.__create_handbook_manual_page(spec, page)

        return page
