import json
import xml.etree.ElementTree as ET
from typing import List

from core.specs.service.connector import ServiceSpecConnector, ChannelType
from core.specs.service.spec import ServiceSpec
from core.specs.specs import ServicesSpecs
from diagrams.xml.rmq.rmq_topic import XmlRabbitmqTopic
from diagrams_generator.diagrams.geometry import Position, Geometry
from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import Style, StyleSelector
from diagrams_generator.diagrams.text_pixel_size import TextPixelSize
from diagrams_generator.diagrams.xml.object import XmlObject, XmlElementType
from diagrams_generator.diagrams.xml.topic import XmlTopic


class XmlTopicsContainer(XmlObject):
    __spec: ServiceSpec

    __connector: ServiceSpecConnector

    __xml_topics_objects: List[XmlTopic]

    __style: Style

    __label_style: Style

    @property
    def service_config(self) -> dict:
        return self.config["layout"]["service"]

    @property
    def id(self) -> str:
        return self.id_by_type(XmlElementType.topics)

    @property
    def spec(self) -> ServiceSpec:
        return self.__spec

    @property
    def data_direction(self) -> str:
        return self.__connector.data_direction

    @property
    def broker_name(self) -> str:
        return self.__connector.dest.service_name

    @property
    def is_kafka_broker(self) -> bool:
        return self.__connector.dest.is_kafka_broker

    @property
    def is_mq_broker(self) -> bool:
        return self.__connector.dest.is_mq_broker

    @property
    def is_rabbitmq_broker(self) -> bool:
        return self.__connector.dest.is_rabbitmq_broker

    @property
    def direction(self) -> str:
        return self.__connector.data_direction

    def id_by_type(self, postfix: XmlElementType):
        return "s#{}#topics_container#{}#{}#postfix#{}".format(self.__spec.service_name,
                                                                     self.__connector.dest.service_name,
                                                                     self.__connector.data_direction,
                                                                     postfix.name)

    def __init__(self, config: dict,
                 styles: StyleSelector,
                 spec: ServiceSpec,
                 specs: ServicesSpecs,
                 connector: ServiceSpecConnector,
                 parent: XmlObject):
        super().__init__(config, styles, parent)
        self.__xml_topics_objects = []
        self.__spec = spec
        self.__specs = specs
        self.__connector = connector
        self.__style = self.styles.topic_container_style(self.__spec, connector)
        self.__label_style = self.styles.topic_container_label_style(self.__spec, connector)
        self.__create_xml_objects()

    @property
    def topics(self) -> List[XmlTopic]:
        return self.__xml_topics_objects

    def __create_xml_objects(self):
        props = self.styles.props['service-topics-container']
        service_xml = ET.Element('UserObject')
        service_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.topics))
        service_xml.attrib['tags'] = ID_MAP.tag("topics_container")
        service_xml.attrib['label'] = ""
        service_xml.attrib['parent'] = "0"

        if self.__connector.dest.is_broker is False:
            service_xml.attrib['link'] = "data:action/json,{}".format(json.dumps({"actions": self.link_actions}))

        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.group))
        mx_cell_xml.attrib['style'] = str(self.__style)
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = ID_MAP.id(self.parent.id)
        mx_cell_xml.attrib['connectable'] = "0"

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['width'] = str(150)
        mx_geometry_xml.attrib['height'] = str(110)
        mx_geometry_xml.attrib['as'] = "geometry"
        mx_cell_xml.append(mx_geometry_xml)
        service_xml.append(mx_cell_xml)
        self.set_xml(XmlElementType.topics, service_xml)
        self.__create_container_label()
        self.__create_topics()

    def __create_container_label(self):
        props = self.styles.props['service-topics-container']
        if self.__connector.data_direction == "rx":
            if self.__connector.dest.is_kafka_broker:
                label = "Consumer Topics"
            elif self.__connector.dest.is_celery_broker:
                label = "Consumer Tasks"
            elif self.__connector.dest.is_mq_broker:
                label = "Consumer Queues"
            elif self.__connector.dest.is_rabbitmq_broker:
                label = "Consumer Queues"

        else:
            if self.__connector.dest.is_kafka_broker:
                label = "Producer Topics"
            elif self.__connector.dest.is_celery_broker:
                label = "Producer Tasks"
            elif self.__connector.dest.is_mq_broker:
                label = "Producer Queues"
            elif self.__connector.dest.is_rabbitmq_broker:
                label = "Producer Exchanges"

        if self.__connector.channel_type == ChannelType.other:
            label = label + " ({})".format(self.__connector.dest.service_name)
        label_w, label_h = TextPixelSize.text_dim(self.config, label, self.__label_style)

        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.topics_label))
        mx_cell_xml.attrib['style'] = str(self.__label_style)
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = ID_MAP.id(self.parent.id)
        mx_cell_xml.attrib['value'] = label

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['width'] = str(label_w + 7)
        mx_geometry_xml.attrib['height'] = str(props['label_height'])
        mx_geometry_xml.attrib['as'] = "geometry"
        mx_cell_xml.append(mx_geometry_xml)
        self.set_xml(XmlElementType.topics_label, mx_cell_xml)

    def __create_topics(self):
        label_weight = float(self.xml(XmlElementType.topics_label).find("mxGeometry").attrib['width'])
        topic_width = label_weight
        for topic_name in self.__connector.channels:
            broker = self.__connector.dest
            if self.is_rabbitmq_broker:
                xml_topic = XmlRabbitmqTopic(self.config,
                                     self.styles,
                                     self.__spec,
                                     broker,
                                     self.__connector,
                                     topic_name,
                                     self.parent)
            else:
                xml_topic = XmlTopic(self.config,
                                     self.styles,
                                     self.__spec,
                                     broker,
                                     self.__connector,
                                     topic_name,
                                     self.parent)
            if topic_width < xml_topic.min_width:
                topic_width = xml_topic.min_width
            self.__xml_topics_objects.append(xml_topic)
        for xml_topic in self.__xml_topics_objects:
            xml_topic.set_width(topic_width)

    def set_position(self, position: Position):
        props = self.styles.props['service-topics-container']

        self.xml(XmlElementType.topics).find("mxCell/mxGeometry").attrib['x'] = str(position.x)
        self.xml(XmlElementType.topics).find("mxCell/mxGeometry").attrib['y'] = str(position.y)

        self.xml(XmlElementType.topics_label).find("mxGeometry").attrib['x'] = str(
            position.x + float(props['label_x_shift']))
        self.xml(XmlElementType.topics_label).find("mxGeometry").attrib['y'] = str(
            position.y + float(props['label_y_shift']))

        topic_position = Position(position.x + float(props['x_topic_shift']),
                                  position.y + float(props['y_topic_shift']))
        for xml_topic in self.__xml_topics_objects:
            xml_topic.set_position(topic_position)
            topic_position.y = topic_position.y + xml_topic.geom.h + props['h_topics_shift']

    @property
    def link_actions(self):
        toggle_tags = list()
        hide_tags = list()
        toggle_tags.append(ID_MAP.tag("s#{}#to#{}#l".format(self.spec.service_name,
                                                                  self.__connector.dest.service_name)))
        hide_tags.append(ID_MAP.tag("s#{}#interface#l".format(self.__connector.dest.service_name)))
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

    def normalize_size(self) -> Geometry:
        props = self.styles.props['service-topics-container']
        w = float(props['x_topic_shift']) * 2 + self.__xml_topics_objects[0].geom.w
        h = float(props['y_topic_shift']) + float(props['bottom_topic_shift']) + len(self.__xml_topics_objects) * (
                    self.__xml_topics_objects[0].geom.h + float(props['h_topics_shift']))
        self.xml(XmlElementType.topics).find("mxCell/mxGeometry").attrib['width'] = str(w)
        self.xml(XmlElementType.topics).find("mxCell/mxGeometry").attrib['height'] = str(h)
        return self.geom

    @property
    def geom(self) -> Geometry:
        return super()._geom(self.xml(XmlElementType.topics).find("mxCell/mxGeometry"))

    def add_to_root(self, root_xml: ET.Element):
        super().add_to_root(root_xml)
        for xml_topic in self.__xml_topics_objects:
            xml_topic.add_to_root(root_xml)
