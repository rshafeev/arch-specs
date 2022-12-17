import logging
from enum import Enum, auto
from typing import Optional

from data.confluence.api.base import ApiBase, transaction
from data.confluence.api.session import SessionWrapper


class PropertyKey(Enum):
    spec_hash = "spec_hash"
    page_hash = "page_hash"
    network_diagram_hash = "network_diagram_hash"
    content_appearance_draft = "content-appearance-draft"
    content_appearance_published = "content-appearance-published"


class ApiProperty(ApiBase):

    def __init__(self, config: dict, session: SessionWrapper):
        super().__init__(config, session)

    async def _get(self, page_id: str, key: PropertyKey, expand: str) -> Optional[dict]:
        payload = {'expand': expand}
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}/property/{}".format(self.url, page_id, key.value)
        response = await self.session.get(url, params=payload, headers=headers)
        response_body = await self.session.response_body(response, raise_exception=False)
        if 'statusCode' in response_body and response_body['statusCode'] == 404:
            return None
        return response_body

    async def get(self, page_id: str, key: PropertyKey) -> Optional[str]:
        response_body = await self._get(page_id, key, "content,version")
        if response_body is not None and 'value' in response_body:
            return response_body['value']
        return None

    async def set(self, page_id, key: PropertyKey, value: str) -> dict:
        p = await self.get(page_id, key)
        if p is not None:  # !hack!
            await self.delete(page_id, key)
        try:
            return await self.create(page_id, key, value)
        except:  # !hack!
            logging.warning("Could not set property {} for the page = {}".format(key.value, page_id))
            return {}

    async def version(self, page_id: str, key: PropertyKey) -> Optional[int]:
        response_body = await self._get(page_id, key, "content,version")
        print(response_body)
        if response_body is not None and 'version' in response_body:
            return response_body['version']['number']
        return None

    async def create(self, page_id, key: PropertyKey, value: str) -> dict:
        payload = {
            'key': key.value,
            'value': value
        }
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}/property".format(self.url, page_id, key.value)
        response = await self.session.post(url, json=payload, headers=headers)
        response_body = await self.session.response_body(response)
        return response_body

    async def delete(self, page_id, key: PropertyKey) -> dict:
        headers = {'Content-Type': 'application/json'}
        url = "{}/content/{}/property/{}".format(self.url, page_id, key.value)
        response = await self.session.delete(url, headers=headers)
        response_body = await self.session.response_body(response)
        return response_body
