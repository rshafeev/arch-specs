import logging
from ctypes import Array
from enum import Enum, auto
from typing import Optional, List

from core.specs.service.channel.rmq_channel import RabbitmqChannel
from core.specs.service.connector import ServiceSpecConnector
from core.specs.settings import Settings


class ServiceType(Enum):
    kafka = "kafka"
    activemq = "activemq"
    rabbitmq = "rabbitmq"
    unknown = ""


class ServiceStatus(Enum):
    ready = auto()
    develop = auto()
    decommission = auto()
    deprecated = auto()
    unknown = auto()

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.name, cls))

    @classmethod
    def list_s(cls) -> str:
        names = cls.list()
        names.remove(ServiceStatus.unknown.name)
        return " ".join(str(x) for x in names)


class ServiceSpec:

    service_name: str

    __raw_spec: Optional[dict]

    __settings: Settings

    __connectors: List[ServiceSpecConnector]

    def __init__(self, service_name: str, settings: Settings):
        self.service_name = service_name
        self.__raw_spec = None
        self.__settings = settings
        self.__connectors = []

    @property
    def wiki_name(self) -> str:
        return f"{self.settings.confluence.service_prefix}{self.service_name}"

    @property
    def is_pro(self) -> bool:
        return self.status == ServiceStatus.ready

    @property
    def is_release_service(self):
        return self.status == ServiceStatus.ready

    @property
    def is_master_service(self):
        return self.status in [ServiceStatus.ready, ServiceStatus.develop, ServiceStatus.deprecated]

    @property
    def unavailable(self) -> bool:
        return 'unavailable' in self.__raw_spec and self.__raw_spec['unavailable'] is True

    @property
    def support_encryption(self) -> List[str]:
        if 'encryption' not in self.__raw_spec:
            return []
        return self.__raw_spec['encryption']

    @property
    def service_module(self) -> str:
        if 'module' not in self.__raw_spec:
            print('error')
        return self.__raw_spec['module']

    @property
    def category(self) -> str:
        return self.__raw_spec['category']

    @property
    def is_product(self) -> bool:
        return self.category in self.__settings.service_categories.product_services

    @property
    def is_kafka_broker(self) -> bool:
        return self.type in [ServiceType.kafka.value]

    @property
    def is_mq_broker(self) -> bool:
        return self.type in [ServiceType.activemq.value]

    @property
    def is_rabbitmq_broker(self) -> bool:
        return self.type in [ServiceType.rabbitmq.value]


    @property
    def is_celery_broker(self) -> bool:
        return 'used_as_celery' in self.__raw_spec and self.__raw_spec['used_as_celery'] is True

    @property
    def is_broker(self) -> bool:
        return (self.is_kafka_broker is True or
                self.is_celery_broker is True  or
                self.is_mq_broker is True or
                self.is_rabbitmq_broker is True)

    @property
    def settings(self) -> Settings:
        return self.__settings

    @property
    def type(self) -> str:
        try:
            if 'type' not in self.__raw_spec:
                return ""
            return self.__raw_spec['type']
        except:
            return ""

    @property
    def status(self) -> ServiceStatus:
        try:
            return ServiceStatus[self.__raw_spec['status']]
        except:
            return ServiceStatus.unknown

    @property
    def dev_teams(self) -> Optional[list]:
        if "dev_team" not in self.__raw_spec:
            return None
        return self.__raw_spec["dev_team"]

    @property
    def full_name(self) -> str:
        if "full_name" not in self.__raw_spec:
            return self.service_name
        return self.__raw_spec["full_name"]

    @property
    def raw(self) -> Optional[dict]:
        if self.__raw_spec is None:
            raise Exception(
                "Could not find raw data for the service '{}'. Please, check meta data!".format(self.service_name))
        return self.__raw_spec

    @property
    def has_internal_storages(self) -> bool:
        return 'internal_storage' in self.__raw_spec and self.__raw_spec['internal_storage'] is not None

    @property
    def internal_storages(self) -> dict:
        return self.__raw_spec['internal_storage']

    @property
    def apidocs(self) -> dict:
        if 'interfaces' not in self.raw:
            return {}
        return self.raw['interfaces']




    @raw.setter
    def raw(self, value: dict):
        self.__raw_spec = value

    @property
    def connectors(self) -> List[ServiceSpecConnector]:
        return self.__connectors

    @property
    def has_connectors(self) -> bool:
        return len(self.connectors) > 0

    def topic(self, topic_name) -> Optional[dict]:
        if self.is_broker is False:
            return None
        raw = self.__raw_spec
        if 'topics' not in raw:
            return None
        if topic_name in raw['topics']:
            return raw['topics'][topic_name]
        return None

    def celery_task(self, task_name) -> Optional[dict]:
        if self.is_broker is False:
            return None
        raw = self.__raw_spec
        if 'celery_tasks' not in raw:
            return None
        if task_name in raw['celery_tasks']:
            return raw['celery_tasks'][task_name]
        return None

    def queue(self, queue_name) -> Optional[dict]:
        if self.is_broker is False:
            return None
        raw = self.__raw_spec
        if 'queues' not in raw:
            return None
        if queue_name in raw['queues']:
            return raw['queues'][queue_name]
        return None

    def get_binding_rabbitmq_queues(self, channel: dict) -> List[dict]:
        if not self.is_rabbitmq_broker:
            return []
        binding_queues = []
        for queue_name in self.queues:
            queue = self.queue(queue_name)
            queue['name'] = queue_name
            if 'binding' not in queue:
                continue
            for binding in queue['binding']:
                if binding['exchange'] != channel['exchange']:
                    continue
                if RabbitmqChannel.is_routing_key_binding(channel, binding):
                    binding_queues.append(queue)
        return binding_queues

    @property
    def topics(self) -> Optional[dict]:
        if self.is_broker is False:
            return None
        raw = self.__raw_spec
        if 'topics' not in raw:
            return None
        return raw['topics']

    @property
    def queues(self) -> Optional[dict]:
        if self.is_broker is False:
            return None
        raw = self.__raw_spec
        if 'queues' not in raw:
            return None
        return raw['queues']

    @property
    def exchanges(self) -> Optional[dict]:
        if self.is_broker is False:
            return None
        raw = self.__raw_spec
        if 'exchanges' not in raw:
            return None
        return raw['exchanges']

    @property
    def celery_tasks(self) -> Optional[dict]:
        if self.is_broker is False:
            return None
        raw = self.__raw_spec
        if 'celery_tasks' not in raw:
            return None
        return raw['celery_tasks']

    def get_connector(self, connect_to_service_name: str, data_direction: str) -> Optional[ServiceSpecConnector]:
        for connector in self.connectors:
            if connector.dest.service_name == connect_to_service_name and connector.data_direction == data_direction:
                return connector

    # def get_topics_list(self, connect_to_service_name: str, data_direction: str) -> Optional[dict]:
    #     c = self.get_connect_to(connect_to_service_name, data_direction)
    #     if c is None or 'topics' not in c or c['topics'] is None:
    #         return None
    #     return c['topics']
