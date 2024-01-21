from enum import Enum
from typing import Optional, List
import core.specs.service
from core.specs.service.channel.rmq_channel import RabbitmqChannel
from core.specs.service.connector import ServiceSpecConnector, ChannelType


class RmqServiceSpecConnector(ServiceSpecConnector):

    def __init__(self, raw: dict, source: 'ServiceSpec', dest: 'ServiceSpec'):
        super().__init__(raw, source, dest)
        self._update_service_specs()

    def _update_service_specs(self):
        key = self._many(self._channel_type)
        source_spec = self.source.raw
        dest_spec = self.dest.raw
        if key not in source_spec:
            source_spec[key] = {}
        if key not in dest_spec:
            dest_spec[key] = {}

        for channel_name in self.channels:
            channel = self.channels[channel_name]
            if channel is None:
                channel = {}
            if channel_name not in dest_spec[key]:
                dest_spec[key][channel_name] = channel
                if self.channel_type is ChannelType.queue:
                    raise Exception(f'Could not find queue "{channel_name}" in broker "{self.dest.service_name}"')
            if 'rx' not in dest_spec[key][channel_name]:
                dest_spec[key][channel_name]['rx'] = {}
            if 'tx' not in dest_spec[key][channel_name]:
                dest_spec[key][channel_name]['tx'] = {}
            dest_spec[key][channel_name][self.data_direction][self.source.service_name] = None

            if self.channel_type is ChannelType.exchange:
                for queue_name in dest_spec['queues']:
                    queue = dest_spec['queues'][queue_name]
                    if 'binding' not in queue or queue['binding'] is None:
                        continue
                    for binding_to in queue['binding']:
                        if binding_to['exchange'] not in channel['exchange']:
                            continue
                        if ('routing_key' not in binding_to or
                                channel['routing_key'] == "" or
                                channel['routing_key'] == binding_to['routing_key']):
                            if 'rx' not in dest_spec['queues'][queue_name]:
                                dest_spec['queues'][queue_name]['rx'] = {}
                            if 'tx' not in dest_spec['queues'][queue_name]:
                                dest_spec['queues'][queue_name]['tx'] = {}
                            dest_spec['queues'][queue_name][self.data_direction][self.source.service_name] = None


    def channel_obj(self, channel_name) -> RabbitmqChannel:
        channel_dict = self.channels[channel_name]
        return RabbitmqChannel(self._connect_to, self.source, self.dest, channel_dict)
