import xml.etree.ElementTree as ET
from enum import Enum, auto
from typing import Optional

from diagrams_generator.diagrams.geometry import Geometry, Position
from diagrams_generator.diagrams.styles_wrapper import StyleSelector


class XmlElementType(Enum):
    core = auto()
    group = auto()
    service_label = auto()
    service_status_label = auto()
    service_image = auto()
    kafka_image = auto()
    topic = auto()
    topics = auto()
    topics_label = auto()
    grpc_container = auto()
    grpc = auto()
    arrow_link = auto()
    connector_group = auto()
    connector_core = auto()
    connector_transport_label = auto()
    connector_arrow = auto()
    connector_ellipse = auto()


class XmlObject:
    styles: StyleSelector

    _xml: dict

    config: dict

    _parent: Optional['XmlObject']

    def __init__(self, config: dict, styles: StyleSelector, parent=None):
        self._xml = {}
        self.config = config
        self.styles = styles
        self._parent = parent

    def xml(self, xml_type: XmlElementType) -> ET.Element:
        return self._xml[xml_type.name]

    def set_xml(self, xml_type: XmlElementType, xml: ET.Element):
        self._xml[xml_type.name] = xml

    def add_to_root(self, root_xml: ET.Element):
        for xml_name in self._xml:
            root_xml.append(self._xml[xml_name])

    @property
    def id(self) -> str:
        return ""

    @property
    def parent(self) -> Optional['XmlObject']:
        return self._parent

    @property
    def geom(self) -> Geometry:
        return Geometry()

    @property
    def position_global(self) -> Position:
        if self._parent is None:
            return self.geom.p
        return Position(self.geom.x + self._parent.position_global.x, self.geom.y + self._parent.position_global.y)

    @staticmethod
    def _geom(xml: ET.Element) -> Geometry:
        geom = Geometry()
        geom.x = float(xml.attrib['x'])
        geom.y = float(xml.attrib['y'])
        geom.w = float(xml.attrib['width'])
        geom.h = float(xml.attrib['height'])
        return geom
