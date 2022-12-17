import logging
import os
from typing import Optional

from core.specs.service.connector import ServiceSpecConnector, ChannelType
from core.specs.service.spec import ServiceSpec
from core.yaml import read_yaml
from core.git.branch import Branch

from core.specs.settings import Settings


class ServicesSpecs:
    row_services_specs: dict

    __topics_info: dict

    __services: dict

    __current_banch: Branch

    __unavailable_services: dict

    __settings: Settings

    def __init__(self, meta_path: str, topics_info_filename: str, current_banch: Branch):
        self.__current_banch = current_banch
        self.__settings = Settings(meta_path)
        self.row_services_specs = ServicesSpecs.upload_row_services_specs(meta_path, self.__settings)
        if os.path.isfile(topics_info_filename):
            self.__topics_info = read_yaml(topics_info_filename)
        else:
            self.__topics_info = {}
        self.__services = {}
        self.__unavailable_services = {}
        self.__extend_specs()

    @staticmethod
    def upload_row_services_specs(meta_path: str, settings: Settings) -> dict:
        out = {"definitions": {}}
        for category in settings.service_categories.all:
            out[category] = read_yaml(meta_path + "/specifications/{}.yaml".format(category))[category]
        out["definitions"] = read_yaml(meta_path + "/specifications/schema/definitions.yaml")["definitions"]
        return out

    def __is_service_avaliable(self, service: ServiceSpec) -> bool:
        if self.__current_banch.is_release and not service.is_release_service:
            return False
        if self.__current_banch.is_master and not service.is_master_service:
            return False
        return service.is_master_service

    def __extend_specs(self):
        for e in self.service_categories.all:
            for service_name in self.row_services_specs[e]:
                spec_raw = self.row_services_specs[e][service_name]
                if spec_raw is None:
                    continue
                spec_raw['category'] = e
                service_spec = ServiceSpec(service_name, self.__settings)
                service_spec.raw = spec_raw
                if self.__is_service_avaliable(service_spec):
                    self.__services[service_spec.service_name] = service_spec
                else:
                    self.__unavailable_services[service_spec.service_name] = service_spec
                    service_spec.raw['unavailable'] = True

        for service_name in self.available_services:
            source_spec = self.get_service_spec(service_name)
            if 'connect_to' not in source_spec.raw or \
                    source_spec.raw['connect_to'] is None:
                continue
            for c in source_spec.raw['connect_to']:
                dest_spec = self.get_service_spec(c['name'])
                connector = ServiceSpecConnector(c, source_spec, dest_spec)
                source_spec.connectors.append(connector)


    @property
    def settings(self):
        return self.__settings

    @property
    def service_categories(self):
        return self.__settings.service_categories

    @property
    def available_services(self):
        return self.__services

    @property
    def all_services(self):
        all_services = {}
        all_services.update(self.__unavailable_services)
        all_services.update(self.__services)
        return all_services

    @property
    def unavailable_services(self):
        return self.__unavailable_services

    def get_service_spec_raw(self, service_name: str) -> Optional[dict]:
        for e in self.settings.service_categories.all:
            if service_name in self.row_services_specs[e]:
                return self.row_services_specs[e][service_name]
            for service_name in self.row_services_specs[e]:
                if 'nodes' in self.row_services_specs[e][service_name] and \
                        service_name in self.row_services_specs[e][service_name]['nodes']:
                    return self.row_services_specs[e][service_name]
        return None

    def exists_service_spec(self, service_name: str) -> bool:
        return self.get_service_spec_raw(service_name) is not None

    def get_service_spec(self, service_name) -> Optional[ServiceSpec]:
        if service_name not in self.all_services:
            return None
        if service_name in self.__services:
            return self.__services[service_name]
        return self.__unavailable_services[service_name]

    def get_service_spec_by_node(self, service_node_name) -> Optional[ServiceSpec]:
        for service_name in self.all_services:
            service = self.get_service_spec(service_name)
            if service is None:
                continue
            if service_name == service_node_name:
                return service
            if 'nodes' in service.raw and \
                    service_node_name in service.raw['nodes']:
                return service
        return None
