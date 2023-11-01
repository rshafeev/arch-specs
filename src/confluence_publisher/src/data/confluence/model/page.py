import hashlib
import json
from typing import Optional, List

PAGE_PROPERTIES_MACRO_ID = "69a99ad2-87af-4049-9b88-2b98ac10afe6"


class ConfluencePage:
    __row_content: dict

    labels: List[str]

    __childs: Optional[List['ConfluencePage']]

    def __init__(self, row_content=None):
        self.labels = []
        self.__childs = None
        if row_content is None:
            self.__row_content = {
                'type': "page"
            }
        else:
            self.__row_content = row_content

    @property
    def row_content(self) -> dict:
        return self.__row_content

    @row_content.setter
    def row_content(self, row_content: dict):
        self.__row_content = row_content

    @property
    def id(self) -> Optional[str]:
        if 'id' not in self.__row_content or len('id') == 0:
            return None
        return self.__row_content['id']

    @id.setter
    def id(self, value: str):
        self.__row_content['id'] = value

    @property
    def status(self) -> Optional[str]:
        if 'status' not in self.__row_content:
            return None
        return self.__row_content['status']

    @status.setter
    def status(self, value: str):
        self.__row_content['status'] = value

    @property
    def version(self) -> Optional[int]:
        if 'version' not in self.__row_content:
            return None
        return self.__row_content['version']['number']

    @version.setter
    def version(self, value: int):
        self.__row_content['version'] = {'number': value}

    @property
    def space_key(self) -> Optional[str]:
        if 'space' not in self.__row_content:
            return None
        return self.__row_content['space']['key']

    @space_key.setter
    def space_key(self, value: str):
        self.__row_content['space'] = {'key': value}

    @property
    def title(self) -> Optional[str]:
        if 'title' not in self.__row_content:
            return None
        return self.__row_content['title']

    @title.setter
    def title(self, value: str):
        self.__row_content['title'] = value

    @property
    def body(self) -> Optional[str]:
        if 'body' not in self.__row_content:
            return None
        return self.__row_content['body']['storage']['value']

    @body.setter
    def body(self, value: str):
        self.__row_content['body'] = {
            'storage': {
                'value': value,
                'representation': "storage"
            }
        }

    @property
    def parent_id(self) -> Optional[str]:
        if 'ancestors' in self.__row_content and len(self.__row_content['ancestors']) > 0:
            return self.__row_content['ancestors'][0]['id']
        return None

    @parent_id.setter
    def parent_id(self, value: str):
        self.__row_content['ancestors'] = [{'id': value}]

    @property
    def hash(self) -> Optional[str]:
        if 'hash' not in self.__row_content:
            return None
        return self.__row_content['hash']['storage']['value']

    @property
    def content_hash(self) -> str:
        if self.__row_content is None or \
                'body' not in self.__row_content or \
                'storage' not in self.__row_content['body'] or \
                'value' not in self.__row_content['body']['storage']:
            return ""
        hash = hashlib.md5(str(self.__row_content['body']['storage']['value']).encode()).hexdigest()
        return hash

    @hash.setter
    def hash(self, value: str):
        self.__row_content['hash'] = {
            'storage': {
                'value': value,
                'representation': "storage"
            }
        }

    @property
    def childs(self) -> Optional[List['ConfluencePage']]:
        return self.__childs

    @childs.setter
    def childs(self, val: List['ConfluencePage']):
        self.__childs = val
