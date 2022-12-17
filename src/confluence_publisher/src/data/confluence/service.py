from data import confluence
from data.confluence.api.attachment import ApiAttachment
from data.confluence.api.base import ApiBase
from data.confluence.api.page import ApiPage
from data.confluence.api.property import ApiProperty
from data.confluence.api.session import SessionWrapper
from data.confluence.api.user import ApiUser


class ConfluenceService(ApiBase):

    def __init__(self,
                 config: dict):
        confluence.api.base.configure(config['transaction_retries_max'], config['transaction_retries_delay_secs'])
        session = SessionWrapper(config)
        super().__init__(config, session)
        self.__users = ApiUser(config, session)
        self.__pages = ApiPage(config, session)
        self.__attachments = ApiAttachment(config, session)
        self.__properties = ApiProperty(config, session)

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
