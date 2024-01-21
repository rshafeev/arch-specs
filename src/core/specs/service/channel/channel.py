from core.specs.service.spec import ServiceSpec


class Channel:
    _source: ServiceSpec
    _desc: ServiceSpec
    _connect_to: dict
    _channel_dict: dict

    def __init__(self, connect_to: dict, source: 'ServiceSpec', dest: 'ServiceSpec', channel_dict: dict):
        self._connect_to = connect_to
        self.source = source
        self.dest = dest
        self.channel_dict = channel_dict