from typing import Optional

from core.specs.service.channel.channel import Channel
from core.specs.service.connector import ChannelType


class RabbitmqChannel(Channel):

    def __init__(self, connect_to: dict, source: 'ServiceSpec', dest: 'ServiceSpec', channel_dict: dict):
        super().__init__(connect_to, source, dest, channel_dict)


    @property
    def is_produce(self) -> bool:
        return self._connect_to['data_direction'] == 'tx'

    @property
    def is_consume(self) -> bool:
        return self._connect_to['data_direction'] == 'rx'


    @staticmethod
    def is_routing_key_binding(keyProducer: dict, keyConsumer: dict) -> bool:
        if 'routing_key' not in keyProducer or keyProducer['routing_key'] == "":
            return True
        if 'routing_key' not in keyConsumer or keyConsumer['routing_key'] == "":
            return True

        if ('routing_key' in keyProducer and
                'routing_key' in keyConsumer and
                keyProducer['routing_key'] == keyConsumer['routing_key']):
            return True

        return False

    def is_binding(self, right_channel: 'RabbitmqChannel') -> bool:
        if self.is_produce and right_channel.is_produce:
            return False
        if self.is_consume and right_channel.is_consume:
            return False
        if self.dest.service_name != right_channel.dest.service_name:
            return False

        if self.is_produce and right_channel.is_consume:
            queue_name = right_channel.channel_dict['queue']
            queue = right_channel.dest.queues[queue_name]
            if 'binding' not in queue or queue['binding'] is None:
                return False
            for binding_to in queue['binding']:
                if binding_to['exchange'] != self.channel_dict['exchange']:
                    continue
                if self.is_routing_key_binding(self.channel_dict, binding_to):
                    return True
            return False
        return False

    @property
    def has_link_destination(self) -> bool:
        if self._connect_to['data_direction'] == 'rx':
            if self.channel_dict['queue'] not in self.dest.queues:
                return False
            queue = self.dest.queues[self.channel_dict['queue']]
            if 'tx' not in queue:
                return False
            return len(queue['tx']) > 0

        if self._connect_to['data_direction'] == 'tx':
            for queue_name in self.dest.queues:
                queue = self.dest.queues[queue_name]
                if 'binding' not in queue or queue['binding'] is None:
                    continue
                for binding_to in queue['binding']:
                    if binding_to['exchange'] != self.channel_dict['exchange']:
                        continue
                    if self.is_routing_key_binding(self.channel_dict, binding_to):
                        return True
        return False


