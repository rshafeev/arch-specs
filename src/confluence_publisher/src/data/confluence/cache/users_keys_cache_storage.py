import json
import logging

from data.confluence.service import ConfluenceService


class UsersKeysCacheStorage:
    __confluence: ConfluenceService

    __cache_user_keys: dict

    __cache_path: str

    def __init__(self, confluence: ConfluenceService, cache_path: str):
        self.__cache_path = cache_path
        self.__cache_user_keys = self.load_users_keys_cache()
        self.__confluence = confluence

    def load_users_keys_cache(self) -> dict:
        try:
            with open(self.__cache_path + '/specs_jira_users_keys.json', 'r') as json_file:
                return json.load(json_file)
        except:
            pass
        return {}

    def dump(self, users_keys_dict: dict):
        with open(self.__cache_path + "/specs_jira_users_keys.json", "w") as fp:
            json.dump(users_keys_dict, fp)

    async def get_user_key(self, owner_name: str):
        owner_name_l = owner_name.lower()
        if owner_name_l not in self.__cache_user_keys or self.__cache_user_keys[owner_name_l] is None:
            self.__cache_user_keys[owner_name_l] = await self.__confluence.users.get_key(owner_name_l)

        if owner_name_l not in self.__cache_user_keys:
            logging.info("Could not find user: {}".format(owner_name_l))
        return self.__cache_user_keys[owner_name_l]

    async def flush(self):
        self.dump(self.__cache_user_keys)
