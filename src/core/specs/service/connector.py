from enum import Enum
from typing import Optional, List
import core.specs.service


class ChannelType(Enum):
    topic = "topic"
    queue = "queue"
    celery_task = "celery_task"
    other = "other"




class ServiceSpecConnector:
    __connect_to: Optional[dict]
    source: 'ServiceSpec'
    dest: 'ServiceSpec'
    __channel_type: ChannelType

    @staticmethod
    def __many(channel_type: ChannelType) -> str:
        if channel_type == ChannelType.queue:
            return "queues"
        elif channel_type == ChannelType.topic:
            return "topics"
        elif channel_type == ChannelType.celery_task:
            return "celery_tasks"

    def __init__(self, raw: dict, source: 'ServiceSpec', dest: 'ServiceSpec'):
        self.__connect_to = raw
        self.source = source
        self.dest = dest
        self.__set_channel_type()
        self.__set_transport()
        self.__update_service_specs()

    def __set_transport(self):
        if 'transport' in self.__connect_to:
            return
        if self.dest.is_kafka_broker:
            self.__connect_to['transport'] = 'tcp'
        if 'protocol' in self.__connect_to and (
                self.__connect_to['protocol'] in ("ws", "wss", "http", "https", "grpc") or self.__connect_to[
            'protocol'].find("grpc") >= 0):
            self.__connect_to['transport'] = 'tcp'

    def __set_channel_type(self):
        if "celery_tasks" not in self.__connect_to and "topics" not in self.__connect_to:
            self.__channel_type = ChannelType.other
            return
        if "topics" in self.__connect_to:
            self.__channel_type = ChannelType.topic
        elif "celery_tasks" in self.__connect_to:
            self.__channel_type = ChannelType.celery_task
        else:
            self.__channel_type = ChannelType.other

    @property
    def has_channels(self) -> bool:
        return self.channels is not None

    @property
    def channels(self) -> Optional[dict]:
        if self.channel_type == ChannelType.other:
            return None
        key = self.__many(self.__channel_type)
        if key in self.__connect_to and self.__connect_to[key] != None:
            return self.__connect_to[key]
        return None

    @property
    def to_broker_connect(self) -> bool:
        return self.__channel_type != ChannelType.other

    @property
    def channel_type(self) -> ChannelType:
        return self.__channel_type

    @property
    def protocol(self) -> str:
        return self.__connect_to["protocol"]

    @property
    def has_protocol(self) -> bool:
        return "protocol" in self.__connect_to

    @property
    def offset_storage(self) -> Optional[str]:
        return self.__connect_to["offset_storage"]

    @property
    def transport(self) -> str:
        return self.__connect_to["transport"]

    @property
    def has_transport(self) -> bool:
        return "transport" in self.__connect_to

    @property
    def data_direction(self) -> str:
        if "data_direction" not in self.__connect_to:
            return ""
        return self.__connect_to["data_direction"]

    @property
    def description(self) -> str:
        if "desc" not in self.__connect_to or self.__connect_to["desc"] is None:
            return ""
        return self.__connect_to["desc"]

    def __update_service_specs(self):

        if self.channel_type == ChannelType.celery_task:
            self.dest.raw['used_as_celery'] = True
        if not self.dest.is_broker:
            return
        if self.channel_type not in [ChannelType.celery_task, ChannelType.topic]:
            return
        key = self.__many(self.__channel_type)
        source_spec = self.dest.raw
        dest_spec = self.dest.raw
        if key not in source_spec:
            source_spec[key] = {}
        if key not in dest_spec:
            dest_spec[key] = {}

        for channel_name in self.channels:
            channel = self.channels[channel_name]
            if channel is None:
                channel = {}
            if channel_name not in source_spec[key]:
                source_spec[key][channel_name] = channel
            if channel_name not in dest_spec[key]:
                dest_spec[key][channel_name] = channel
            if 'rx' not in source_spec[key][channel_name]:
                dest_spec[key][channel_name]['rx'] = {}
            if 'tx' not in source_spec[key][channel_name]:
                dest_spec[key][channel_name]['tx'] = {}
            dest_spec[key][channel_name][self.data_direction][self.source.service_name] = None
            pass


