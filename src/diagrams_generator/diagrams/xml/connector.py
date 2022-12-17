import json
import xml.etree.ElementTree as ET

from core.specs.service.connector import ServiceSpecConnector
from core.specs.service.spec import ServiceSpec
from diagrams_generator.diagrams.geometry import Position, Geometry
from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import StyleSelector, Style
from diagrams_generator.diagrams.text_pixel_size import TextPixelSize
from diagrams_generator.diagrams.xml.object import XmlObject, XmlElementType


class XmlConnector(XmlObject):
    service_spec: ServiceSpec

    __connector: ServiceSpecConnector

    __core_style: Style

    __ellipse_style: Style

    __arrow_style: Style

    __label_style: Style

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 spec: ServiceSpec,
                 connector: ServiceSpecConnector,
                 parent: XmlObject):
        super().__init__(config, styles, parent)
        self.service_spec = spec
        self.__connector = connector
        self.__core_style = self.styles.connector_core_style(self.service_spec, connector)
        self.__ellipse_style = self.styles.connector_ellipse_style(self.service_spec, connector)
        self.__label_style = self.styles.connector_label_style(self.service_spec, connector)
        self.__arrow_style = self.styles.connector_arrow_style(self.service_spec, connector)

        self.__create_xml_objects()

    def id_by_type(self, postfix: XmlElementType):
        return "s#{}#to#{}#{}#{}".format(self.service_spec.service_name,
                                      self.__connector.dest.service_name,
                                      self.__connector.data_direction,
                                      postfix.name)

    def __create_xml_objects(self):
        self.__create_group()
        self.__create_connector_core()
        self.__create_arrow()
        self.__create_connector_ellipse()
        self.__create_arrow_transport_label()

    def __create_group(self):
        group = ET.Element('UserObject')
        group.attrib['id'] = ID_MAP.id(self.group_id)
        group.attrib['tags'] = ID_MAP.tag("connector")
        group.attrib['label'] = ""
        group.attrib['link'] = "data:action/json,{}".format(json.dumps({"actions": self.link_actions}))
        group.attrib['Description'] = self.description
        if self.__connector.has_protocol:
            group.attrib['Protocol'] = self.__connector.protocol
        if self.__connector.has_transport:
            group.attrib['Transport'] = self.__connector.transport

        group_mxcell = ET.Element('mxCell')
        group_mxcell.attrib['parent'] = ID_MAP.id(self.parent.id)
        group_mxcell.attrib['style'] = 'group'
        group_mxcell.attrib['vertex'] = '1'
        group_mxcell.attrib['connectable'] = '0'

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['x'] = str(0)
        mx_geometry_xml.attrib['y'] = str(0)
        mx_geometry_xml.attrib['width'] = str(150)
        mx_geometry_xml.attrib['height'] = str(110)
        mx_geometry_xml.attrib['as'] = "geometry"
        group_mxcell.append(mx_geometry_xml)
        group.append(group_mxcell)
        self.set_xml(XmlElementType.connector_group, group)

    def __create_connector_core(self):
        props = self.styles.props['service-connector']
        label_w, label_h = TextPixelSize.text_dim(self.config, self.__connector.dest.service_name, self.__core_style)
        connector = ET.Element('mxCell')
        connector.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_core))
        connector.attrib['value'] = self.__connector.dest.service_name
        connector.attrib['style'] = str(self.__core_style)
        connector.attrib['vertex'] = "1"
        connector.attrib['parent'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_group))

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['x'] = str(0)
        mx_geometry_xml.attrib['y'] = str(0)
        mx_geometry_xml.attrib['width'] = str(label_w + props['label_width_append'])
        mx_geometry_xml.attrib['height'] = str(props['label_height'])
        mx_geometry_xml.attrib['as'] = "geometry"
        connector.append(mx_geometry_xml)
        self.set_xml(XmlElementType.connector_core, connector)

    def __create_connector_ellipse(self):
        props = self.styles.props['service-connector']
        ellipse = ET.Element('mxCell')
        ellipse.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_ellipse))
        ellipse.attrib['style'] = str(self.__ellipse_style)
        ellipse.attrib['vertex'] = "1"
        ellipse.attrib['parent'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_group))

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['x'] = str(0)
        mx_geometry_xml.attrib['y'] = str(0)
        mx_geometry_xml.attrib['width'] = str(props['ellipse_size'])
        mx_geometry_xml.attrib['height'] = str(props['ellipse_size'])
        mx_geometry_xml.attrib['as'] = "geometry"
        ellipse.append(mx_geometry_xml)
        self.set_xml(XmlElementType.connector_ellipse, ellipse)

    def __create_arrow(self):
        row_xml = ET.Element('object')
        row_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_arrow))
        row_xml.attrib['tags'] = ""
        row_xml.attrib['label'] = ""
        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['style'] = str(self.__arrow_style)
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_group))
        mx_cell_xml.attrib['source'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_ellipse))
        mx_cell_xml.attrib['target'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_core))
        mx_cell_xml.attrib['edge'] = "1"
        mx_cell_xml.attrib['visible'] = "1"

        _mx_geometry_xml = ET.Element('mxGeometry')
        _mx_geometry_xml.attrib['width'] = "150"
        _mx_geometry_xml.attrib['height'] = "50"
        _mx_geometry_xml.attrib['as'] = "geometry"
        _mx_geometry_xml.attrib['relative'] = "1"
        mx_cell_xml.append(_mx_geometry_xml)
        row_xml.append(mx_cell_xml)
        self.set_xml(XmlElementType.connector_arrow, row_xml)

    @property
    def protocol(self) -> str:
        if self.__connector.has_protocol:
            return self.__connector.protocol
        if self.__connector.has_transport:
            return self.__connector.transport
        return ""

    def __create_arrow_transport_label(self):
        row_xml = ET.Element('object')
        row_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_transport_label))
        row_xml.attrib['tags'] = ""
        row_xml.attrib['label'] = ""
        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['style'] = str(self.__label_style)
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = ID_MAP.id(self.id_by_type(XmlElementType.connector_arrow))
        mx_cell_xml.attrib['connectable'] = "0"
        mx_cell_xml.attrib['value'] = self.protocol

        _mx_geometry_xml = ET.Element('mxGeometry')
        _mx_geometry_xml.attrib['as'] = "geometry"
        _mx_geometry_xml.attrib['relative'] = "1"

        _mx_geometry_point_xml = ET.Element('mxPoint')
        _mx_geometry_point_xml.attrib['as'] = "offset"
        _mx_geometry_xml.append(_mx_geometry_point_xml)

        mx_cell_xml.append(_mx_geometry_xml)
        row_xml.append(mx_cell_xml)
        self.set_xml(XmlElementType.connector_transport_label, row_xml)

    @property
    def link_actions(self):
        toggle_tags = list()
        hide_tags = list()
        toggle_tags.append(ID_MAP.tag("s#{}#to#{}#l".format(self.service_spec.service_name,
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

    def disable_link(self):
        self.xml(XmlElementType.connector_group).attrib.pop('link')

    def set_position(self, position: Position):
        self.xml(XmlElementType.connector_group).find("mxCell/mxGeometry").attrib['x'] = str(position.x)
        self.xml(XmlElementType.connector_group).find("mxCell/mxGeometry").attrib['y'] = str(position.y)

    def normalize_size(self) -> Geometry:
        props = self.styles.props['service-connector']
        ellipse_w = float(self.xml(XmlElementType.connector_ellipse).find("mxGeometry").attrib['width'])
        ellipse_h = float(self.xml(XmlElementType.connector_ellipse).find("mxGeometry").attrib['height'])

        label_w, label_h = TextPixelSize.text_dim(self.config, self.protocol, self.__label_style)

        core_x = ellipse_w + 2 * float(props['transport_label_x_shift']) + label_w
        core_y = 0.0
        self.xml(XmlElementType.connector_core).find("mxGeometry").attrib['x'] = str(core_x)
        self.xml(XmlElementType.connector_core).find("mxGeometry").attrib['y'] = str(core_y)
        core_w = float(self.xml(XmlElementType.connector_core).find("mxGeometry").attrib['width'])
        core_h = float(self.xml(XmlElementType.connector_core).find("mxGeometry").attrib['height'])

        ellipse_y = (core_y + core_h / 2.0) - ellipse_h / 2.0
        self.xml(XmlElementType.connector_ellipse).find("mxGeometry").attrib['y'] = str(ellipse_y)

        w = core_x + core_w + float(props['x_shift'])
        h = float(self.xml(XmlElementType.connector_core).find("mxGeometry").attrib['height'])

        self.xml(XmlElementType.connector_group).find("mxCell/mxGeometry").attrib['width'] = str(w)
        self.xml(XmlElementType.connector_group).find("mxCell/mxGeometry").attrib['height'] = str(h)
        return self.geom

    @property
    def geom(self) -> Geometry:
        return super()._geom(self.xml(XmlElementType.connector_group).find("mxCell/mxGeometry"))

    @property
    def id(self) -> str:
        return self.group_id

    @property
    def group_id(self) -> str:
        return self.id_by_type(XmlElementType.connector_group)

    @property
    def connect_to_service(self) -> str:
        return self.__connector.dest.service_name

    @property
    def connector(self) -> ServiceSpecConnector:
        return self.__connector

    @property
    def description(self) -> str:
        return self.__connector.description
