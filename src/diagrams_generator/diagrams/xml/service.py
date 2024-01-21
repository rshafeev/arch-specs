import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

from core.specs.service.spec import ServiceSpec, ServiceStatus, ServiceType
from core.specs.specs import ServicesSpecs
from diagrams_generator.diagrams.geometry import Position, Geometry
from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import Style, StyleSelector
from diagrams_generator.diagrams.text_pixel_size import TextPixelSize
from diagrams_generator.diagrams.xml.connector import XmlConnector
from diagrams_generator.diagrams.xml.object import XmlObject, XmlElementType
from diagrams_generator.diagrams.xml.topics_container import XmlTopicsContainer


class XmlService(XmlObject):
    spec: ServiceSpec

    specs: ServicesSpecs

    topics_containers: Dict[str, XmlTopicsContainer]

    __style: Style

    __label_style: Style

    __connectors: list

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 spec: ServiceSpec,
                 specs: ServicesSpecs):
        super().__init__(config, styles)
        self.spec = spec
        self.specs = specs
        self.topics_containers = {}
        self.__connectors = []
        self.__style = self.styles.service_style(spec)
        self.__label_style = self.styles.service_label_style(spec)
        self.__status_label_style = self.styles.service_status_label_style(spec)

    async def generate(self):
        await self.__init_group_container()
        await self.__init_xml_service_object()
        await self.__create_connectors()
        await self.__create_container_label()
        await self.__create_status_label()
        await self.__create_image()


    def topics(self, container_id: str) -> XmlTopicsContainer:
        return self.topics_containers[container_id]

    def add_to_root(self, root_xml: ET.Element):
        for xml_name in self._xml:
            root_xml.append(self._xml[xml_name])
        for container_id in self.topics_containers:
            self.topics(container_id).add_to_root(root_xml)
        for connector in self.__connectors:
            connector.add_to_root(root_xml)

    def set_position(self, position: Position):
        self.xml(XmlElementType.group).find("mxGeometry").attrib['x'] = str(position.x)
        self.xml(XmlElementType.group).find("mxGeometry").attrib['y'] = str(position.y)

    def normalize_size(self):
        current_service_core_width = float(self.xml(XmlElementType.group).find("mxGeometry").attrib['width'])
        current_service_core_height = float(self.xml(XmlElementType.group).find("mxGeometry").attrib['height'])
        label_font_size_w, label_font_size_h = TextPixelSize.text_dim(self.config, self.spec.service_name, self.__style)

        topics_container_props = self.styles.props['service-topics-container']
        x = topics_container_props['x_shift']
        y = topics_container_props['y_shift']

        if self.spec.service_module in self.styles.props['service-core']['add_images_by_service_module']:
            if 'y_image_shift' in self.styles.props['service-core']:
                y = y + self.styles.props['service-core']['y_image_shift']

        if label_font_size_w > current_service_core_width - 25:
            y = y + 5 + label_font_size_h * 2
        else:
            y = y + 5 + label_font_size_h
        topics_geom = Geometry(x, y, 0, 0)
        topics_h_max = 0.0
        topics_w_max = 0.0

        for container_id in self.topics_containers:
            container = self.topics_containers[container_id]
            if container.data_direction != "rx":
                continue
            container.set_position(topics_geom.p)
            container_geom = container.normalize_size()
            topics_h_max = topics_h_max + container_geom.h + topics_container_props['x_between']
            topics_w_max = max(topics_w_max, container_geom.w)
            topics_geom.p.y = topics_geom.p.y + container_geom.h + topics_container_props['x_between']

        topics_geom = Geometry(x, y, topics_w_max, 0)
        for container_id in self.topics_containers:
            container = self.topics_containers[container_id]
            if container.data_direction != "tx":
                continue
            topics_geom.x = topics_geom.x + int(topics_container_props['x_between']) + topics_geom.w
            container.set_position(topics_geom.p)
            topics_geom = container.normalize_size()
            topics_h_max = max(topics_h_max, topics_geom.h)

        service_connector_props = self.styles.props['service-connector']
        connector_x = service_connector_props['x_shift']
        connector_y = max(y, topics_geom.y) + topics_h_max + topics_container_props['bottom_shift']
        connector_w_max = 0
        connectors_sum_h = 0
        for connector in self.__connectors:
            connector.set_position(Position(connector_x, connector_y))
            connector_geom = connector.normalize_size()
            connector_y = connector_y + connector_geom.h + service_connector_props['y_between']
            connector_w_max = max(connector_w_max, connector_geom.w)
            connectors_sum_h = connector_geom.h + service_connector_props['y_between']

        w = topics_geom.x + max(connector_w_max, topics_geom.w) + topics_container_props['x_shift']
        h = connector_y + connectors_sum_h + service_connector_props['bottom_shift']

        if w > current_service_core_width:
            self.xml(XmlElementType.core).find("mxCell/mxGeometry").attrib['width'] = str(w)
            self.xml(XmlElementType.group).find("mxGeometry").attrib['width'] = str(w)
        self.xml(XmlElementType.service_label).find("mxCell/mxGeometry").attrib['width'] = \
            self.xml(XmlElementType.core).find("mxCell/mxGeometry").attrib['width']

        if h > current_service_core_height:
            self.xml(XmlElementType.core).find("mxCell/mxGeometry").attrib['height'] = str(h)
            self.xml(XmlElementType.group).find("mxGeometry").attrib['height'] = str(h)

        return self.geom

    async def __init_group_container(self):
        service_core_props = self.styles.props['service-core']
        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.group))
        mx_cell_xml.attrib['style'] = "group"
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = "1"
        mx_cell_xml.attrib['connectable'] = "0"

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['x'] = str(0)
        mx_geometry_xml.attrib['y'] = str(0)
        mx_geometry_xml.attrib['width'] = str(service_core_props['width_min'])
        mx_geometry_xml.attrib['height'] = str(service_core_props['height_min'])
        mx_geometry_xml.attrib['as'] = "geometry"
        mx_cell_xml.append(mx_geometry_xml)
        self.set_xml(XmlElementType.group, mx_cell_xml)

    @property
    def label_link(self) -> Optional[str]:
        space = self.specs.settings.confluence.space
        link = self.specs.settings.confluence.link
        if self.spec.is_product:
            return "{}/{}/{}".format(link, space, self.spec.wiki_name)
        return None

    @property
    def link_actions(self):
        toggle_tags = list()
        hide_tags = list()

        toggle_tags.append(ID_MAP.tag("s#{}#interface#l".format(self.spec.service_name)))
        hide_tags.append(ID_MAP.tag("s#{}#interface#l#tx".format(self.spec.service_name)))
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

    async def __create_image(self):
        props = self.styles.props['service-core']
        if self.spec.service_module not in props['add_images_by_service_module']:
            return
        style = self.styles.service_image_style(self.spec)
        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['style'] = str(style)
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = ID_MAP.id(self.id)

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['width'] = str(30)
        mx_geometry_xml.attrib['height'] = str(35)
        mx_geometry_xml.attrib['x'] = str(10)
        mx_geometry_xml.attrib['y'] = str(10)
        mx_geometry_xml.attrib['as'] = "geometry"
        mx_cell_xml.append(mx_geometry_xml)
        self.set_xml(XmlElementType.service_image, mx_cell_xml)

    async def __create_container_label(self):
        props = self.styles.props['service-core']
        label = self.spec.full_name
        label_w, label_h = TextPixelSize.text_dim(self.config, label, self.__label_style)

        xml = ET.Element('UserObject')
        xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.service_label))
        xml.attrib['label'] = label
        if self.label_link:
            xml.attrib['link'] = self.label_link

        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['style'] = str(self.__label_style)
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = ID_MAP.id(self.id)

        if 'service_name' in self.spec.raw:
            mx_cell_xml.attrib['name'] = self.spec.service_name
        if 'desc' in self.spec.raw and self.spec.raw['desc'] is not None:
            mx_cell_xml.attrib['Description'] = self.spec.raw['desc']
        if 'owner' in self.spec.raw and self.spec.raw['owner'] is not None:
            mx_cell_xml.attrib['Owners'] = self.spec.raw['owner']

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['width'] = str(label_w + 7)
        mx_geometry_xml.attrib['height'] = str(props['label_height'])
        mx_geometry_xml.attrib['y'] = str(12)
        mx_geometry_xml.attrib['as'] = "geometry"
        mx_cell_xml.append(mx_geometry_xml)
        xml.append(mx_cell_xml)
        self.set_xml(XmlElementType.service_label, xml)

    async def __create_status_label(self):
        if self.spec.status == ServiceStatus.ready:
            return
        props = self.styles.props['service-core']
        label = str(self.spec.status.name)
        label_w, label_h = TextPixelSize.text_dim(self.config, label, self.__status_label_style)

        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.service_status_label))
        mx_cell_xml.attrib['style'] = str(self.__status_label_style)
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = ID_MAP.id(self.id)
        mx_cell_xml.attrib['value'] = str(label)

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['width'] = str(label_w + 7)
        mx_geometry_xml.attrib['height'] = str(props['status_label_height'])
        mx_geometry_xml.attrib['y'] = str(1)
        mx_geometry_xml.attrib['as'] = "geometry"
        mx_cell_xml.append(mx_geometry_xml)
        self.set_xml(XmlElementType.service_status_label, mx_cell_xml)

    async def __init_xml_service_object(self):
        service_core_props = self.styles.props['service-core']

        service_xml = ET.Element('UserObject')
        service_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.core))
        service_xml.attrib['module'] = self.spec.service_module
        service_xml.attrib['link'] = "data:action/json,{}".format(json.dumps({"actions": self.link_actions}))
        if 'service_name' in self.spec.raw:
            service_xml.attrib['name'] = self.spec.service_name
        if 'desc' in self.spec.raw and self.spec.raw['desc'] is not None:
            service_xml.attrib['Description'] = self.spec.raw['desc']
        if 'owner' in self.spec.raw and self.spec.raw['owner'] is not None:
            service_xml.attrib['Owners'] = self.spec.raw['owner']
        if 'type' in self.spec.raw and self.spec.raw['type'] is not None:
            service_xml.attrib['type'] = self.spec.raw['type']
        if 'language' in self.spec.raw and self.spec.raw['language'] is not None:
            service_xml.attrib['language'] = self.spec.raw['language']

        service_mx_cell_xml = ET.Element('mxCell')
        service_mx_cell_xml.attrib['style'] = str(self.__style)
        service_mx_cell_xml.attrib['vertex'] = "1"
        service_mx_cell_xml.attrib['parent'] = ID_MAP.id(self.group_id)

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['x'] = str(0)
        mx_geometry_xml.attrib['y'] = str(0)
        mx_geometry_xml.attrib['width'] = str(service_core_props['width_min'])
        mx_geometry_xml.attrib['height'] = str(service_core_props['height_min'])
        mx_geometry_xml.attrib['as'] = "geometry"
        service_mx_cell_xml.append(mx_geometry_xml)
        service_xml.append(service_mx_cell_xml)
        self.set_xml(XmlElementType.core, service_xml)

    async def __create_connectors(self):
        if self.spec.has_connectors is False:
            return

        props = self.styles.props['service-topics-container']['hide_topics_for_services']
        if self.spec.service_name not in props:
            for connector in self.spec.connectors:
                if connector.has_channels == False:
                    continue
                topics_container = XmlTopicsContainer(self.config, self.styles, self.spec, self.specs, connector, self)
                self.topics_containers[topics_container.id] = topics_container

        xml_connectors = {}
        for connector in self.spec.connectors:
            if connector.dest.service_name in xml_connectors:
                continue
            xml_connectors[connector.dest.service_name] = {}
            xml_connector = XmlConnector(self.config, self.styles, self.spec, connector, self)
            self.__connectors.append(xml_connector)

    @property
    def id(self) -> str:
        return self.id_by_type(XmlElementType.group)

    def id_by_type(self, postfix: XmlElementType):
        return "s#{}#{}".format(self.spec.service_name, postfix.name)

    @property
    def group_id(self) -> str:
        return ID_MAP.id_s(self.xml(XmlElementType.group).attrib['id'])

    @property
    def connectors(self) -> List[XmlConnector]:
        return self.__connectors

    @property
    def geom(self) -> Geometry:
        return super()._geom(self.xml(XmlElementType.group).find("mxGeometry"))
