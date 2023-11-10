import logging

from data import confluence
from data.confluence.api.attachment import ApiAttachment
from data.confluence.api.base import ApiBase
from data.confluence.api.page import ApiPage
from data.confluence.api.property import ApiProperty
from data.confluence.api.session import SessionWrapper
from data.confluence.api.user import ApiUser


class ConfluenceService(ApiBase):

    _json_session: SessionWrapper
    _row_session: SessionWrapper

    def __init__(self,
                 config: dict):
        confluence.api.base.configure(config['transaction_retries_max'], config['transaction_retries_delay_secs'])
        json_session = SessionWrapper(config)
        row_session = SessionWrapper(config, check_response_code=False)

        super().__init__(config, json_session)
        self.__users = ApiUser(config, json_session)
        self.__pages = ApiPage(config, json_session)
        self.__attachments = ApiAttachment(config, json_session, row_session)
        self.__properties = ApiProperty(config, json_session)
        self._json_session = json_session
        self._row_session = row_session


    @property
    def users(self) -> ApiUser:
        return self.__users

    @property
    def pages(self) -> ApiPage:
        return self.__pages

    @property
    def attachments(self) -> ApiAttachment:
        return self.__attachments

    @property
    def properties(self) -> ApiProperty:
        return self.__properties

    async def release(self):
        try:
            await self._json_session.release()
            await self._row_session.release()
        except Exception as e:
            logging.error(e)
