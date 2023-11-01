import asyncio
import json
import logging
import uuid
from typing import Optional, List

import aiohttp
from aiohttp import ClientResponse


class ClientSessionExt(aiohttp.ClientSession):
    __timeout_secs: int

    __retries_max: int

    __retries_codes: List[int]

    __retries_delay_secs: int

    @property
    def timeout_secs(self) -> int:
        return self.__timeout_secs

    @property
    def retries_max(self) -> int:
        return self.__retries_max

    @property
    def retries_codes(self) -> List[int]:
        return self.__retries_codes

    @property
    def retries_delay_secs(self) -> int:
        return self.__retries_delay_secs

    @timeout_secs.setter
    def timeout_secs(self, value: int):
        self.__timeout_secs = value

    @retries_max.setter
    def retries_max(self, value: int):
        self.__retries_max = value

    @retries_codes.setter
    def retries_codes(self, value: List[int]):
        self.__retries_codes = value

    @retries_delay_secs.setter
    def retries_delay_secs(self, value: int):
        self.__retries_delay_secs = value

    async def _request(self, method, url, **kwargs):
        request_id = str(uuid.uuid4())
        logging.info('[%s] <%s %r>', request_id, method, url)
        if "headers" in kwargs and kwargs["headers"] is not None:
            headers_s = json.dumps(kwargs["headers"], ensure_ascii=False).encode('utf8')
            logging.info('[%s] headers: %s', request_id, headers_s)

        if "params" in kwargs and kwargs["params"] is not None:
            params_s = json.dumps(kwargs["params"], ensure_ascii=False).encode('utf8')
            logging.info('[%s] params: %s', request_id, params_s)
        retries = 0
        try:
            while retries < self.retries_max:
                retries = retries + 1
                if retries > 1:
                    logging.warning("[%s] retry %d starting...", request_id, retries)
                try:
                    response = await super()._request(method, url, timeout=self.timeout_secs, **kwargs)
                    response._request_id = request_id
                    body = await self.response_body(response, False)
                    if response.status in self.retries_codes or \
                            (body is not None and 'statusCode' in body and
                             body['statusCode'] in self.retries_codes):
                        await asyncio.sleep(self.retries_delay_secs)
                        continue
                    return response
                except Exception as e:
                    logging.exception(e)
                await asyncio.sleep(self.retries_delay_secs)
            logging.error("[%s] retries exceeded: %d >= %d", request_id, retries, self.retries_max)
            raise Exception("[{}] could not execute the request with success status code".format(request_id))
        except Exception as e:
            if "json" in kwargs and kwargs["json"] is not None:
                json_s = json.dumps(kwargs["json"], ensure_ascii=False).encode('utf8')
                logging.error('[%s] body: %s', request_id, json_s)
            raise e

    @staticmethod
    def __handle_response_error(response: ClientResponse, response_body_s: str, response_body: dict,
                                raise_exception: bool):
        request_id = response._request_id
        if 'statusCode' in response_body:
            logging.warning('[%s] response: %s', request_id, response_body_s)
            reason = ""
            if 'message' in response_body:
                reason = response_body['message']
            if raise_exception:
                raise Exception("[{}] code: {}. {}".format(request_id, response_body['statusCode'], reason))

    async def response_body(self, response: ClientResponse, raise_exception=True) -> Optional[dict]:
        request_id = response._request_id
        logging.info('[%s] response status code: %d', request_id, response.status)
        response_body_s = await response.text(encoding="utf8")
        if response_body_s is None or response_body_s == "":
            logging.warning('[%s] empty response', request_id)
            return None
        try:
            out = json.loads(response_body_s)
        except:
            logging.error('[%s] could not parse response: %s', request_id, response_body_s)
            return None
        self.__handle_response_error(response, response_body_s, out, raise_exception)
        return out


class SessionWrapper:
    __session: Optional[ClientSessionExt]

    __auth_user: str

    __auth_password: str

    __auth_token: str

    __config: dict

    def __init__(self,
                 config: dict):
        self.__auth_user = config['auth_user']
        self.__auth_password = config['auth_password']
        self.__auth_token = config['auth_token']
        self.__config = config
        self.__session = None

    @property
    def current(self) -> ClientSessionExt:
        if self.__session is None:
            if self.__auth_token is None or len(self.__auth_token) == 0:
                auth = aiohttp.BasicAuth(login=self.__auth_user,
                                         password=self.__auth_password,
                                         encoding='utf-8')
                self.__session = ClientSessionExt(auth=auth)
            else:
                headers = {'Authorization': 'Bearer {}'.format(self.__auth_token)}
                self.__session = ClientSessionExt(headers=headers)
        self.__session.retries_max = self.__config['retries_max']
        self.__session.timeout_secs = self.__config['timeout_secs']
        self.__session.retries_codes = self.__config['retries_codes']
        self.__session.retries_delay_secs = self.__config['retries_delay_secs']

        return self.__session

    async def release(self):
        if self.__session is not None:
            await self.__session.close()
