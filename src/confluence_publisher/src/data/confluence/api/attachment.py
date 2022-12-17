from typing import Optional

from aiohttp import FormData

from data.confluence.api.base import ApiBase
from data.confluence.api.session import SessionWrapper


class ApiAttachment(ApiBase):

    def __init__(self, config: dict, session: SessionWrapper):
        super().__init__(config, session)

    async def create(self, page_id: str, local_file_name: str, confluence_file_name: str) -> dict:
        files = FormData()
        files.add_field("file", open(local_file_name, 'rb'), filename=confluence_file_name,
                        content_type='application/vnd.jgraph.mxfile.cached')
        url = "{}/content/{}/child/attachment".format(self.url, page_id)
        headers = {'X-Atlassian-Token': 'nocheck'}
        response = await self.session.post(url, data=files, headers=headers)
        response_body = await self.session.response_body(response)
        return response_body

    async def update(self, page_id: str, attachment_id: str, local_file_name: str, confluence_file_name: str) -> dict:
        files = FormData()
        files.add_field("file", open(local_file_name, 'rb'), filename=confluence_file_name,
                        content_type='application/vnd.jgraph.mxfile.cached')
        url = "{}/content/{}/child/attachment/{}/data".format(self.url, page_id, attachment_id)
        headers = {'X-Atlassian-Token': 'nocheck'}
        response = await self.session.post(url, data=files, headers=headers)
        response_body = await self.session.response_body(response)
        return response_body

    async def get(self, page_id: str, confluence_file_name: str) -> Optional[dict]:
        url = "{}/content/{}/child/attachment".format(self.url, page_id)
        payload = {'filename': confluence_file_name}
        headers = {'X-Atlassian-Token': 'nocheck'}
        response = await self.session.get(url, params=payload, headers=headers)
        response_body = await self.session.response_body(response)
        if 'results' not in response_body or len(response_body['results']) == 0:
            return None
        return response_body['results'][0]
