import logging
from typing import Tuple, Dict, List

from core.specs.specs import ServicesSpecs
from data.confluence.cache.users_keys_cache_storage import UsersKeysCacheStorage
from data.confluence.service import ConfluenceService
from data.specs.service_spec_ext import ServiceSpecExt


class OwnersValidator:

    __services_specs: ServicesSpecs

    __user_keys_storage: UsersKeysCacheStorage

    def __init__(self, services_specs: ServicesSpecs, confluence: ConfluenceService, cache_path: str):
        self.__services_specs = services_specs
        self.__user_keys_storage = UsersKeysCacheStorage(confluence, cache_path)

    async def validate(self) -> Tuple[bool, List[Dict[str, str]]]:
        errors = []
        for service_name in self.__services_specs.all_services:
            service_spec = ServiceSpecExt.create(self.__services_specs.get_service_spec(service_name),
                                                 self.__user_keys_storage)
            owners = await service_spec.owner_keys()
            for owner_name in owners:
                if owners[owner_name] is None:
                    errors.append({
                        'service': service_name,
                        'error': "Invalid username: {}".format(owner_name)
                    })
        return len(errors) == 0, errors

    @staticmethod
    def print(errors: List[Dict[str, str]]):
        for e in errors:
            logging.error("[{}]: {}".format(e["service"], e["error"]))