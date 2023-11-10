import logging
from typing import Optional, List

import aiohttp

from data.confluence.api.base import ApiBase, transaction
from data.confluence.api.session import SessionWrapper
from data.confluence.model.page import ConfluencePage


class ApiPage(ApiBase):

    def __init__(self, config: dict, session: SessionWrapper):
        super().__init__(config, session)

    async def find(self, page_title: str, space_key: str) -> Optional[ConfluencePage]:
        payload = {'title': page_title, 'spaceKey': space_key, 'expand': "space,version,body.storage,metadata"}
        url = self.url + "/content"
        response = await self.session.get(url, params=payload)
        response_body = await self.session.response_body(response)
        if response_body is None:
            return None
        results = response_body['results']
        if len(results) == 0:
            return None
        page = ConfluencePage(results[0])
        page.space_key = space_key
        return page

    async def create(self, page: ConfluencePage) -> dict:
        headers = {'Content-Type': 'application/json'}
        response = await self.session.post(self.url + "/content", json=page.row_content, headers=headers)
        response_body = await self.session.response_body(response)
        page.id = response_body['id']
        await self.add_labels_to_page(page.id, page.labels)
        return response_body

    @transaction()
    async def update(self, page: ConfluencePage) -> dict:
        current_version = await self.version(page.id)
        page.version = current_version + 1
        page.status = "current"
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}".format(self.url, page.id)
        response = await self.session.put(url, json=page.row_content, headers=headers)
        response_body = await self.session.response_body(response)
        await self.add_labels_to_page(page.id, page.labels)
        return response_body

    async def delete(self, page_id: str) -> dict:
        for page in await self.childs(page_id):
            await self.delete(page.id)
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}".format(self.url, page_id)
        response = await self.session.delete(url, headers=headers)
        response_body = await self.session.response_body(response)
        return response_body

    async def get(self, page_id: str) -> dict:
        payload = {'expand': "space,version,body.storage,metadata"}
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}".format(self.url, page_id)
        response = await self.session.get(url, params=payload, headers=headers)
        response_body = await self.session.response_body(response)
        return response_body

    async def get_page(self, page_id: str, expand="body.storage") -> Optional[ConfluencePage]:
        payload = {'expand': f"space,version,metadata,{expand}"}
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}".format(self.url, page_id)
        response = await self.session.get(url, params=payload, headers=headers)
        response_body = await self.session.response_body(response)
        if response_body is None:
            return None
        page = ConfluencePage(response_body)
        return page

    async def add_labels_to_page(self, page_id: str, labels: List['str']) -> dict:
        if len(labels) == 0:
            return {}
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}/label".format(self.url, page_id)
        response = await self.session.post(url, json=labels, headers=headers)
        response_body = await self.session.response_body(response)
        return response_body

    async def version(self, page_id: str) -> int:
        payload = {'expand': "space,version,container"}
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}".format(self.url, page_id)
        response = await self.session.get(url, params=payload, headers=headers)
        response_body = await self.session.response_body(response)
        return response_body['version']['number']

    async def childs(self, page_id: str, start=0, limit=500) -> List[ConfluencePage]:
        payload = {'expand': "page", 'start': start, 'limit': limit}
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}/child".format(self.url, page_id)
        response = await self.session.get(url, params=payload, headers=headers)
        response_body = await self.session.response_body(response)
        childs = []
        if 'page' in response_body and 'results' in response_body['page']:
            for page_raw in response_body['page']['results']:
                page = ConfluencePage(page_raw)
                childs.append(page)
        return childs
