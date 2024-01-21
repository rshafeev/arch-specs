import json
import xml.etree.ElementTree as ET
from typing import List

from core.specs.service.channel.rmq_channel import RabbitmqChannel
from core.specs.service.connector import ServiceSpecConnector, ChannelType
from core.specs.service.spec import ServiceSpec
from diagrams_generator.diagrams.geometry import Position, Geometry
from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import Style, StyleSelector
from diagrams_generator.diagrams.text_pixel_size import TextPixelSize
from diagrams_generator.diagrams.xml.object import XmlObject, XmlElementType


class XmlRabbitmqTopic(XmlObject):
    __spec: ServiceSpec

    __connector: ServiceSpecConnector

    __topic_name: str

    __style: Style

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 spec: ServiceSpec,
                 broker_service: ServiceSpec,
                 connector: ServiceSpecConnector,
                 channel_name: str,
                 parent: XmlObject):
        super().__init__(config, styles, parent)
        self.__spec = spec
        self.__broker_service = broker_service
        self.__connector = connector
        self.__channel_name = channel_name
        if self.topic_enable:
            self.__style = self.styles.topic_style(spec, connector, channel_name)
        else:
            self.__style = self.styles.topic_disable_style(spec, connector, channel_name)
        self.__create_xml_objects()

    @property
    def rmq_channel(self) -> RabbitmqChannel:
        return self.__connector.channel_obj(self.__channel_name)

    @property
    def has_link_destination(self) -> bool:
        if self.__connector.dest.is_broker is False:
            return False
        props = self.styles.props['service-topic']
        if self.__spec.service_name in props['disable_arrow_links_service_name']:
            return False
        if self.__broker_service.is_rabbitmq_broker:
            return self.rmq_channel.has_link_destination
        else:
            if self.__connector.channel_type == ChannelType.topic:
                channel = self.__broker_service.topic(self.__channel_name)
            elif self.__connector.channel_type == ChannelType.celery_task:
                channel = self.__broker_service.celery_task(self.__channel_name)
            else:
                return False

            direction = "rx" if self.__connector.data_direction == "tx" else "tx"
            if direction is None:
                pass
            if direction not in channel or len(channel[direction]) == 0:
                return False
            return True

    @property
    def topic_enable(self) -> bool:
        props = self.styles.props['service-topic']
        if self.__connector.dest.is_broker and not self.has_link_destination and \
                self.__spec.service_name not in props['disable_arrow_links_service_name']:
            return False
        return True

    @property
    def id(self):
        return "s#{}#topic#{}#{}#{}".format(self.__spec.service_name,
                                                  self.__connector.dest.service_name,
                                                  self.__connector.data_direction,
                                                  self.__channel_name)

    @property
    def name(self) -> str:
        return self.__channel_name

    @property
    def service_name(self) -> str:
        return self.__spec.service_name

    @property
    def broker_name(self) -> str:
        return self.__connector.dest.service_name

    @property
    def direction(self) -> str:
        return self.__connector.data_direction

    def tag(self, postfix: XmlElementType):
        return "broker#{}#topic#{}#{}".format(self.__connector.dest.service_name,
                                             self.__channel_name,
                                             postfix.name)

    def set_producer_name(self, producer_name: str):
        self.xml(XmlElementType.topic).attrib['producer'] = producer_name

    @property
    def link_actions(self):
        toggle_tags = list()
        hide_tags = list()
        if self.__connector.data_direction == 'rx':
            queue_name = self.rmq_channel.channel_dict['queue']
            if queue_name in self.rmq_channel.dest.queues:
                queue = self.rmq_channel.dest.queues[queue_name]
                for bind_to in queue['binding']:
                    rechange = bind_to['exchange']
                    if 'routing_key' in bind_to and bind_to['routing_key'] != "":
                        rechange = f"{rechange}/{bind_to['routing_key']}"
                    toggle_tags.append(ID_MAP.tag(f"broker#{self.__connector.dest.service_name}#topic#{rechange}#{self.service_name}#l"))
                    hide_tags.append(ID_MAP.tag(f"broker#{self.__connector.dest.service_name}#topic#{rechange}#l"))
        else:
            rexchange = self.__channel_name
            toggle_tags.append(ID_MAP.tag(f"broker#{self.__connector.dest.service_name}#topic#{rexchange}#l#{self.__connector.source.service_name}"))
            hide_tags.append(ID_MAP.tag(f"broker#{self.__connector.dest.service_name}#topic#{rexchange}#l#rx"))
        link_actions = [
            {
                "toggle": {
                    "tags": toggle_tags
                }
            },
            {
                "hide": {
                    "tags": hide_tags
                }
            }
        ]
        return link_actions

    @property
    def has_link(self) -> bool:
        topic = self.xml(XmlElementType.topic)
        return 'link' in topic.attrib

    def disable_link(self):
        topic = self.xml(XmlElementType.topic)
        if 'link' in topic.attrib:
            self.xml(XmlElementType.topic).attrib.pop('link')

    def set_style(self, style: Style):
        self.__style = style
        self.xml(XmlElementType.topic).find('mxCell').attrib['style'] = str(self.__style)

    def __create_xml_objects(self):
        tag = "topic"
        if self.__connector.dest.is_celery_broker:
            tag = "celery_task"
        props = self.styles.props['service-topic']
        topic = self.__connector.channels[self.__channel_name]
        topic_object_id = self.id
        topic_xml = ET.Element('UserObject')
        topic_xml.attrib['id'] = ID_MAP.id(topic_object_id)
        topic_xml.attrib['tags'] = ID_MAP.tag(tag)
        topic_xml.attrib['label'] = self.__channel_name
        topic_xml.attrib['Broker'] = self.__connector.dest.service_name

        if self.__connector.channel_type is ChannelType.exchange:
            channel = self.__connector.channels[self.__channel_name]
            topic_xml.attrib['Exchange'] = str(channel['name'])
            if 'routing_key' in channel:
                topic_xml.attrib['RoutingKey'] = str(channel['routing_key'])
        if self.has_link_destination:
            topic_xml.attrib['link'] = "data:action/json,{}".format(json.dumps({"actions": self.link_actions}))
        if topic is not None and 'desc' in topic and topic['desc'] is not None:
            topic_xml.attrib['Description'] = str(topic['desc'])

        topic_mx_cell_xml = ET.Element('mxCell')
        topic_mx_cell_xml.attrib['style'] = str(self.__style)
        topic_mx_cell_xml.attrib['vertex'] = "1"
        topic_mx_cell_xml.attrib['parent'] = ID_MAP.id(self.parent.id)

        topic_mx_geometry_xml = ET.Element('mxGeometry')
        topic_mx_geometry_xml.attrib['x'] = str(0)
        topic_mx_geometry_xml.attrib['y'] = str(0)
        topic_mx_geometry_xml.attrib['width'] = str(self.min_width)
        topic_mx_geometry_xml.attrib['height'] = str(self.height)
        topic_mx_geometry_xml.attrib['as'] = 'geometry'

        topic_mx_cell_xml.append(topic_mx_geometry_xml)
        topic_xml.append(topic_mx_cell_xml)
        self.set_xml(XmlElementType.topic, topic_xml)

    def set_position(self, position: Position):
        self.xml(XmlElementType.topic).find("mxCell/mxGeometry").attrib['x'] = str(position.x)
        self.xml(XmlElementType.topic).find("mxCell/mxGeometry").attrib['y'] = str(position.y)

    def set_width(self, width: float):
        self.xml(XmlElementType.topic).find("mxCell/mxGeometry").attrib['width'] = str(width)

    @property
    def min_width(self):
        props = self.styles.props['service-topic']
        max_text = 0
        for txt in self.display_channel_name:
            max_text = max(len(txt), max_text)
        w, h = TextPixelSize.text_dim(self.config, txt, self.__style)
        return w + props['x_shift'] + 7

    @property
    def height(self) -> int:
        props = self.styles.props['service-topic']
        return int(props['height']) * len(self.display_channel_name)

    @property
    def display_channel_name(self) -> List[str]:
        return [self.__channel_name]
        props = self.styles.props['service-topic']
        topic_width_max = props['width_max']
        name_rows = []
        for rows_count in range(3):

            w, h = TextPixelSize.text_dim(self.config, self.__channel_name, self.__style)
            topic_width = w + props['x_shift'] + 7
            if topic_width <= topic_width_max:
                break
        return name_rows

    @property
    def geom(self) -> Geometry:
        return super()._geom(self.xml(XmlElementType.topic).find("mxCell/mxGeometry"))

    def normalize_size(self) -> Geometry:
        return self.geom
