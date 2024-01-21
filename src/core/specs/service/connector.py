from enum import Enum
from typing import Optional, List
import core.specs.service


class ChannelType(Enum):
    topic = "topic"
    queue = "queue"
    exchange = "exchange"
    celery_task = "celery_task"
    other = "other"


class ServiceSpecConnector:
    _connect_to: Optional[dict]
    source: 'ServiceSpec'
    dest: 'ServiceSpec'
    _channel_type: ChannelType

    @staticmethod
    def _many(channel_type: ChannelType) -> str:
        if channel_type == ChannelType.queue:
            return "queues"
        if channel_type == ChannelType.exchange:
            return "exchanges"
        elif channel_type == ChannelType.topic:
            return "topics"
        elif channel_type == ChannelType.celery_task:
            return "celery_tasks"

    def __init__(self, connect_to: dict, source: 'ServiceSpec', dest: 'ServiceSpec'):
        self._connect_to = connect_to
        self.source = source
        self.dest = dest
        self._set_channel_type()
        self._set_transport()
        self._update_service_specs()

    def _set_transport(self):
        if 'transport' in self._connect_to:
            return
        if self.dest.is_kafka_broker:
            self._connect_to['transport'] = 'tcp'
        if self.dest.is_mq_broker:
            self._connect_to['transport'] = 'tcp'
        if self.dest.is_rabbitmq_broker:
            self._connect_to['transport'] = 'tcp'
        if 'protocol' in self._connect_to and (
                self._connect_to['protocol'] in ("ws", "wss", "http", "https", "grpc", "s3") or self._connect_to[
            'protocol'].find("grpc") >= 0):
            self._connect_to['transport'] = 'tcp'

    def _set_channel_type(self):
        if ("celery_tasks" not in self._connect_to and
                "topics" not in self._connect_to and
                "queues" not in self._connect_to and
                "exchanges" not in self._connect_to):
            self._channel_type = ChannelType.other

            return
        if "topics" in self._connect_to:
            self._channel_type = ChannelType.topic
        elif "celery_tasks" in self._connect_to:
            self._channel_type = ChannelType.celery_task
        elif "queues" in self._connect_to:
            self._channel_type = ChannelType.queue
        elif "exchanges" in self._connect_to:
            self._channel_type = ChannelType.exchange
        else:
            self._channel_type = ChannelType.other

    @property
    def has_channels(self) -> bool:
        return self.channels is not None

    @property
    def channels(self) -> Optional[dict]:
        if self.channel_type == ChannelType.other:
            return None
        key = self._many(self._channel_type)
        if self._channel_type is ChannelType.exchange:
            exchanges_dict = {}
            for exchange in self._connect_to[key]:
                exchange['exchange'] = exchange['name']
                if 'routing_key' in exchange and exchange['routing_key'] is not None and exchange['routing_key'] != "":
                    channel_name = f"{exchange['name']}/{exchange['routing_key']}"
                else:
                    channel_name = f"{exchange['name']}"
                exchanges_dict[channel_name] = exchange
            return exchanges_dict

        if key in self._connect_to and self._connect_to[key] != None:
            for channel_name in self._connect_to[key]:
                if self._connect_to[key][channel_name] is None:
                    self._connect_to[key][channel_name] = {}
                self._connect_to[key][channel_name][self.channel_type.value] = channel_name
            return self._connect_to[key]
        return None




    @property
    def to_broker_connect(self) -> bool:
        return self._channel_type != ChannelType.other

    @property
    def channel_type(self) -> ChannelType:
        return self._channel_type

    @property
    def protocol(self) -> str:
        return self._connect_to["protocol"]

    @property
    def has_protocol(self) -> bool:
        return "protocol" in self._connect_to

    @property
    def offset_storage(self) -> Optional[str]:
        return self._connect_to["offset_storage"]

    @property
    def transport(self) -> str:
        return self._connect_to["transport"]

    @property
    def has_transport(self) -> bool:
        return "transport" in self._connect_to

    @property
    def data_direction(self) -> str:
        if "data_direction" not in self._connect_to:
            return ""
        return self._connect_to["data_direction"]

    @property
    def description(self) -> str:
        if "desc" not in self._connect_to or self._connect_to["desc"] is None:
            return ""
        return self._connect_to["desc"]

    def _update_service_specs(self):
        if self.channel_type == ChannelType.celery_task:
            self.dest.raw['used_as_celery'] = True
        if not self.dest.is_broker:
            return
        if self.channel_type not in [ChannelType.celery_task, ChannelType.topic, ChannelType.queue]:
            return
        key = self._many(self._channel_type)
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

