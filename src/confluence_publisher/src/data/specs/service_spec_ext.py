import hashlib
import json
import logging
from typing import Dict

from core.specs.service.spec import ServiceSpec
from core.specs.settings import Settings
from data.confluence.cache.users_keys_cache_storage import UsersKeysCacheStorage


class ServiceSpecExt(ServiceSpec):
    __user_keys_storage: UsersKeysCacheStorage

    def __init__(self, user_keys_storage: UsersKeysCacheStorage, service_name: str, settings: Settings):
        super().__init__(service_name, settings)
        self.__user_keys_storage = user_keys_storage

    @classmethod
    def create(cls, spec: ServiceSpec, user_keys_storage: UsersKeysCacheStorage):
        s = ServiceSpecExt(user_keys_storage, spec.service_name, spec.settings)
        s.raw = spec.raw
        return s

    async def __update_service_owner_keys(self):
        raw = self.raw
        raw['owner_keys'] = {}
        try:
            if 'owner' not in raw or raw["owner"] is None:
                return
            owner_names_list = str(raw["owner"]).split(',')
            for owner_name in owner_names_list:
                owner_key = None
                owner_name = owner_name.strip()
                try:
                    owner_key = await self.__user_keys_storage.get_user_key(owner_name)
                except Exception as e:
                    logging.exception(e)
                if owner_key is None:
                    logging.error("Could not find userKey for {}".format(owner_name))
                    raw['owner_keys'][owner_name] = None
                    continue
                if 'owner_keys' not in raw:
                    raw['owner_keys'] = {}
                raw['owner_keys'][owner_name] = owner_key
        finally:
            await self.__user_keys_storage.flush()

    async def owner_keys(self) -> Dict[str, str]:
        raw = self.raw
        if 'owner_keys' not in raw or raw["owner_keys"] is None:
            await self.__update_service_owner_keys()
        return raw['owner_keys']

    @property
    def hash(self) -> str:
        return hashlib.md5(json.dumps(self.raw, ensure_ascii=False).encode('utf8')).hexdigest()
