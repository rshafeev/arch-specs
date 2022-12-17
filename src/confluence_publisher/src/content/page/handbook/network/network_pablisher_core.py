import logging

from data.confluence.api.property import PropertyKey
from data.confluence.model.page import ConfluencePage
from data.confluence.service import ConfluenceService


class NetworkPagePublisherCore:
    _confluence: ConfluenceService

    def __init__(self,
                 confluence: ConfluenceService):
        self._confluence = confluence

    async def _create_page(self, page: ConfluencePage) -> ConfluencePage:
        await self._confluence.pages.create(page)
        await self._confluence.properties.set(page.id, PropertyKey.content_appearance_draft, "full-width")
        await self._confluence.properties.set(page.id, PropertyKey.content_appearance_published,
                                              "full-width")
        logging.info("Page '{}' was created.".format(page.title))
        return page

    async def _update_page(self, page: ConfluencePage, force_recreate_network_pages: int) -> ConfluencePage:
        updated_page_hash = page.content_hash
        current_page_hash = await self._confluence.properties.get(page.id, PropertyKey.page_hash)
        if current_page_hash != updated_page_hash or \
                force_recreate_network_pages == 1:
            await self._confluence.pages.update(page)
            await self._confluence.properties.set(page.id, PropertyKey.page_hash, updated_page_hash)
            logging.info("Page '{}' was updated.".format(page.title))
        else:
            logging.info("Page '{}'. Current page hash: {}".format(page.title, current_page_hash))
            logging.info("Page '{}'. Current page was not changed [CACHE]".format(page.title))

        if force_recreate_network_pages == 1:
            await self._confluence.properties.set(page.id, PropertyKey.content_appearance_draft, "full-width")
            await self._confluence.properties.set(page.id, PropertyKey.content_appearance_published,
                                                  "full-width")
        return page
