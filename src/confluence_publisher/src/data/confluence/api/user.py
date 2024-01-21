from typing import Optional

from data.confluence.api.base import ApiBase
from data.confluence.api.session import SessionWrapper


class ApiUser(ApiBase):

    def __init__(self, config: dict, session: SessionWrapper):
        super().__init__(config, session)

    async def get_key(self, username: str) -> Optional[str]:
        payload = {'cql': "{{user.fullname~\"{}\"}}".format(username)}
        headers = {'Content-Type': 'application/json'}
        url = "{}/search".format(self.url)
        response = await self.session.get(url, params=payload, headers=headers)
        response_body = await self.session.response_body(response)
        if response_body is None or 'results' not in response_body or len(response_body["results"]) == 0:
            return None
        for e in response_body["results"]:
            if self.is_cloud:
                if e['user']['publicName'].upper() == username.upper():
                    return e['user']['accountId']
            else:
                if e['user']['displayName'].upper() == username.upper() or e['user']['username'].upper() == username.upper():
                    return e['user']['userKey']
        return None
