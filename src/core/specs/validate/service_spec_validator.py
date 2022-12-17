from typing import Tuple, Dict, List, Optional

import validators
from jsonschema import Draft3Validator

from core.specs.validate.validator import Validator, SchemaType


class ServiceSpecValidator(Validator):
    __specs: dict

    __schema_validator: Draft3Validator

    def __init__(self, meta_path: str, specs: dict):
        super().__init__(meta_path)
        self.__specs = specs
        self.__schema_validator = self.validator(SchemaType.service)

    def validate(self, service_key: str, service_spec: dict) -> Tuple[bool, List[Dict[str, str]], List[Dict[str, str]]]:
        errors = []
        warns = []
        if service_spec is None or not isinstance(service_spec, dict):
            errors.append({
                'service': service_key,
                'error': "Empty dict."
            })
            return len(errors) == 0, errors, warns

        for error in sorted(self.__schema_validator.iter_errors(service_spec), key=str):
            errors.append({
                'service': service_key,
                'error': error.message
            })
        self.__check_name_uniqueness(service_key, service_spec, errors)
        self.__check_connect_to_name(service_key, service_spec, errors)
        self.__check_connect_to_data_direction(service_key, service_spec, errors)
        self.__check_connect_to_offset_storage(service_key, service_spec, errors, warns)

        self.__check_dev_team_property(service_key, service_spec, errors)
        self.__check_layer_property(service_key, service_spec, errors)
        self.__check_status_property(service_key, service_spec, errors)
        self.__check_src_property(service_key, service_spec, errors)
        self.__check_desc_property(service_key, service_spec, errors, warns)
        self.__check_owner_property(service_key, service_spec, errors, warns)
        return len(errors) == 0, errors, warns

    @staticmethod
    def __check_desc_property(service_key: str, service_spec: dict, errors: List, warns: List):
        if "desc" in service_spec and \
                isinstance(service_spec["desc"], str) and \
                len(str(service_spec["desc"]).strip()) == 0:
            warns.append({
                'service': service_key,
                'warn': "Empty Description. Please, fill a property 'desc'"
            })

    @staticmethod
    def __check_owner_property(service_key: str, service_spec: dict, errors: List, warns: List):
        if "owner" in service_spec and \
                isinstance(service_spec["owner"], str) and \
                len(str(service_spec["owner"]).strip()) == 0:
            warns.append({
                'service': service_key,
                'warn': "no owners. Please, fill a property 'owner'"
            })

    @staticmethod
    def __check_src_property(service_key: str, service_spec: dict, errors: List):
        if "src" not in service_spec or not isinstance(service_spec["src"], str):
            return
        if len(service_spec["src"]) > 0 and not validators.url(service_spec["src"]):
            errors.append({
                'service': service_key,
                'error': "Invalid url '{}'".format(service_spec["src"])
            })

    def __check_name_uniqueness(self, service_key: str, service_spec: dict, errors: List):
        # name uniqueness check
        names = [service_key]
        if 'nodes' in service_spec and isinstance(service_spec['nodes'], list):
            for node in service_spec['nodes']:
                if isinstance(node, str):
                    names.append(node)

        found_cnt = 0
        for e in self.service_categories.all:
            for service_key in self.__specs[e]:
                found_spec = self.__specs[e][service_key]
                if found_spec == service_spec:
                    continue
                if service_key in names:
                    found_cnt = found_cnt + 1
                    if found_cnt > 0:
                        errors.append({
                            'service': service_key,
                            'error': "duplicate service name. All service names should be uniqueness."
                        })

                if 'nodes' in found_spec and isinstance(found_spec['nodes'], list):
                    for node in found_spec['nodes']:
                        if isinstance(node, str):
                            if node in names:
                                found_cnt = found_cnt + 1
                                if found_cnt > 0:
                                    msg = '''duplicate service node name '{}'. All service names should be 
                                    uniqueness."'''.format(node)
                                    errors.append({
                                        'service': service_key,
                                        'error': msg
                                    })

    def __check_connect_to_name(self, service_key: str, service_spec: dict, errors: List):
        if "connect_to" not in service_spec:
            return
        for connect_to in service_spec["connect_to"]:
            if 'name' not in connect_to:
                continue
            connect_to_service = self.__search_service(connect_to['name'])
            if connect_to_service is None:
                errors.append({
                    'service': service_key,
                    'error': "Could not find service '{}' from connect_to array".format(connect_to['name'])
                })

    def __check_connect_to_data_direction(self, service_key: str, service_spec: dict, errors: List):
        if "connect_to" not in service_spec:
            return
        for connect_to in service_spec["connect_to"]:
            if 'name' not in connect_to:
                continue
            connect_to_service = self.__search_service(connect_to['name'])
            if connect_to_service is None or 'type' not in connect_to_service:
                continue
            if connect_to_service['type'] == "kafka" and "data_direction" not in connect_to:
                errors.append({
                    'service': service_key,
                    'error': "Please, set 'data_direction' field for 'connect_to' == {}".format(connect_to['name'])
                })
                continue

    def __check_connect_to_offset_storage(self, service_key: str, service_spec: dict, errors: List, warns: List):
        if "connect_to" not in service_spec:
            return
        for connect_to in service_spec["connect_to"]:
            if 'name' not in connect_to:
                continue
            connect_to_service = self.__search_service(connect_to['name'])
            if connect_to_service is None or 'type' not in connect_to_service:
                continue
            if connect_to_service['type'] == "kafka" and \
                    "data_direction" not in connect_to:
                continue
            if connect_to_service['type'] == "kafka" and \
                    connect_to["data_direction"] == "rx" and \
                    "offset_storage" not in connect_to:
                errors.append({
                    'service': service_key,
                    'error': "Please, set 'offset_storage' field for 'connect_to' == {}".format(connect_to['name'])
                })

            if connect_to_service['type'] == "kafka" and \
                    connect_to["data_direction"] == "rx" and \
                    "offset_storage" in connect_to and \
                    (not isinstance(connect_to['offset_storage'], str) or len(connect_to['offset_storage']) == 0):
                warns.append({
                    'service': service_key,
                    'warn': "Please, set 'offset_storage' field for 'connect_to' == {}".format(connect_to['name'])
                })

            if connect_to_service['type'] == "kafka" and \
                    connect_to["data_direction"] == "tx" and \
                    "offset_storage" in connect_to:
                errors.append({
                    'service': service_key,
                    'error': "Please, remove 'offset_storage' field for 'connect_to' == {}. 'offset_storage' is used "
                             "only if `data_direction` == rx".format(connect_to['name'])
                })

    def __check_dev_team_property(self, service_key: str, service_spec: dict, errors: List):
        if "dev_team" not in service_spec:
            return
        if not isinstance(service_spec["dev_team"], list):
            errors.append({
                'service': service_key,
                'error': "dev-team property should be list"
            })
        for team in service_spec["dev_team"]:
            if 'name' not in team:
                errors.append({
                    'service': service_key,
                    'error': "Unknown dev-team"
                })
            elif self.__found_team(team['name']) is None:
                errors.append({
                    'service': service_key,
                    'error': "Unknown dev-team {}".format(team['name'])
                })

    def __check_layer_property(self, service_key: str, service_spec: dict, errors: List):
        if "layer" not in service_spec or not isinstance(service_spec["layer"], str):
            return
        if self.__has_layer(service_spec["layer"]) is False:
            errors.append({
                'service': service_key,
                'error': "Unknown layer '{}'".format(service_spec["layer"])
            })

    def __check_status_property(self, service_key: str, service_spec: dict, errors: List):
        if "status" not in service_spec or not isinstance(service_spec["status"], str):
            return
        if self.__has_status(service_spec["status"]) is False:
            errors.append({
                'service': service_key,
                'error': "Unknown status '{}'".format(service_spec["status"])
            })

    def __has_status(self, status_name: str) -> bool:
        for e in self.__specs["definitions"]["status"]:
            if status_name == self.__specs["definitions"]["status"][e]:
                return True
        return False

    def __has_layer(self, layer_name: str) -> bool:
        for e in self.__specs["definitions"]["layers"]:
            if layer_name == self.__specs["definitions"]["layers"][e]:
                return True
        return False

    def __found_team(self, team_name: str) -> Optional[Dict]:
        for e in self.__specs["definitions"]["teams"]:
            if team_name == self.__specs["definitions"]["teams"][e]['name']:
                return self.__specs["definitions"]["teams"][e]['name']

    def __search_service(self, service_key: str) -> Optional[Dict]:
        for e in self.service_categories.all:
            for key in self.__specs[e]:
                spec = self.__specs[e][key]
                if key == service_key:
                    return spec
                if 'nodes' in spec and isinstance(spec['nodes'], list):
                    for node in spec['nodes']:
                        if isinstance(node, str) and node == service_key:
                            return spec
        return None
