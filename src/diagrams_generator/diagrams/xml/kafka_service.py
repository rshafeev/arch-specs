import xml.etree.ElementTree as ET

from core.specs.service.spec import ServiceSpec
from core.specs.specs import ServicesSpecs
from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import Style, StyleSelector
from diagrams_generator.diagrams.xml.object import XmlElementType
from diagrams_generator.diagrams.xml.service import XmlService


class XmlKafkaService(XmlService):
    __kafka_image_style: Style

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 spec: ServiceSpec,
                 specs: ServicesSpecs):
        super().__init__(config, styles, spec, specs)
        self.__kafka_image_style = self.styles.kafka_image_style()

    async def generate(self):
        await super().generate()
        await self.__generate_kafka_image()

    def add_to_root(self, root_xml: ET.Element):
        super().add_to_root(root_xml)

    async def __generate_kafka_image(self):
        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['id'] = ID_MAP.id(self.id_by_type(XmlElementType.kafka_image))
        mx_cell_xml.attrib['style'] = str(self.__kafka_image_style)
        mx_cell_xml.attrib['vertex'] = "1"
        mx_cell_xml.attrib['parent'] = ID_MAP.id(self.id)

        mx_geometry_xml = ET.Element('mxGeometry')
        mx_geometry_xml.attrib['width'] = str(70)
        mx_geometry_xml.attrib['height'] = str(70)
        mx_geometry_xml.attrib['y'] = str(5)
        mx_geometry_xml.attrib['x'] = str(10)
        mx_geometry_xml.attrib['as'] = "geometry"
        mx_cell_xml.append(mx_geometry_xml)
        self.set_xml(XmlElementType.kafka_image, mx_cell_xml)

    def normalize_size(self):
        geom = super().normalize_size()
        h = float(self.geom.h) + 20
        self.xml(XmlElementType.core).find("mxCell/mxGeometry").attrib['height'] = str(h)
        self.xml(XmlElementType.group).find("mxGeometry").attrib['height'] = str(h)
        return self.geom

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
