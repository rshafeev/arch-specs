import xml.etree.ElementTree as ET

from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import Style, StyleSelector
from diagrams_generator.diagrams.xml.object import XmlObject, XmlElementType


class XmlArrow(XmlObject):
    __style: Style

    _static: bool

    _visible: bool

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 style: Style,
                 static=False,
                 visible=False):
        super().__init__(config, styles)
        self.__style = style
        self._static = static
        self._visible = visible
        self._create_xml_objects()

    def _tags_s(self):
        tags_s = ""
        for tag in self.tags:
            tags_s = tags_s + tag + " "
        return tags_s

    @property
    def tags(self):
        return []

    @property
    def id(self) -> str:
        return ""

    @property
    def source_id(self) -> str:
        return ""

    @property
    def dest_id(self) -> str:
        return ""

    @property
    def source_name(self) -> str:
        return ""

    @property
    def dest_name(self) -> str:
        return ""

    @property
    def description(self) -> str:
        return ""

    @property
    def protocol(self) -> str:
        return ""

    @property
    def transport(self) -> str:
        return ""

    def _create_xml_objects(self):
        static_tag = ''
        if self._static is False:
            static_tag = ID_MAP.tag('arrow')
        row_xml = ET.Element('object')
        row_xml.attrib['id'] = ID_MAP.id(self.id)
        row_xml.attrib['Source'] = self.source_name
        row_xml.attrib['Dest'] = self.dest_name
        row_xml.attrib['Description'] = self.description
        if len(self.protocol) > 0:
            row_xml.attrib['Protocol'] = self.protocol
        if len(self.transport) > 0:
            row_xml.attrib['Transport'] = self.transport


        row_xml.attrib['tags'] = "{} {}".format(self._tags_s(), static_tag)

        mx_cell_xml = ET.Element('mxCell')
        mx_cell_xml.attrib['style'] = str(self.__style)
        mx_cell_xml.attrib['parent'] = "1"
        mx_cell_xml.attrib['source'] = ID_MAP.id(self.source_id)
        mx_cell_xml.attrib['target'] = ID_MAP.id(self.dest_id)
        mx_cell_xml.attrib['edge'] = "1"
        if self._visible is False:
            mx_cell_xml.attrib['visible'] = "0"
        # else:
        #     mx_cell_xml.attrib['visible'] = "1"

        _mx_geometry_xml = ET.Element('mxGeometry')
        _mx_geometry_xml.attrib['width'] = "150"
        _mx_geometry_xml.attrib['height'] = "50"
        _mx_geometry_xml.attrib['as'] = "geometry"
        _mx_geometry_xml.attrib['relative'] = "1"
        mx_cell_xml.append(_mx_geometry_xml)
        row_xml.append(mx_cell_xml)
        self.set_xml(XmlElementType.arrow_link, row_xml)

    def set_left_side_connect_for_destination(self):
        self.__style.set_value('entry-x', '0')
        self.xml(XmlElementType.arrow_link).find("mxCell").attrib['style'] = str(self.__style)

    def set_right_side_connect_for_destination(self):
        self.__style.set_value('entry-x', '1')
        self.xml(XmlElementType.arrow_link).find("mxCell").attrib['style'] = str(self.__style)

    def set_left_side_connect_for_source(self):
        self.__style.set_value('exit-x', '0')
        self.xml(XmlElementType.arrow_link).find("mxCell").attrib['style'] = str(self.__style)

    def set_right_side_connect_for_source(self):
        self.__style.set_value('exit-x', '1')
        self.xml(XmlElementType.arrow_link).find("mxCell").attrib['style'] = str(self.__style)