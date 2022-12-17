from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import StyleSelector
from diagrams_generator.diagrams.xml.arrow.arrow import XmlArrow
from diagrams_generator.diagrams.xml.connector import XmlConnector
from diagrams_generator.diagrams.xml.service import XmlService


class XmlConnectToArrow(XmlArrow):
    source: XmlConnector

    dest: XmlService

    connect_direction: str

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 source: XmlConnector,
                 dest: XmlService,
                 connect_direction: str,
                 style_name='service-connect-to-arrow',
                 visible=True
                 ):
        self.source = source
        self.dest = dest
        self.connect_direction = connect_direction
        style = styles.style(style_name)
        super().__init__(config, styles, style, static=False, visible=visible)
        if self.source.position_global.x > self.dest.position_global.x + self.dest.geom.w:
            self.set_right_side_connect_for_destination()
            self.set_left_side_connect_for_source()

    @property
    def tags(self):
        if self.connect_direction == 'tx':
            tags = [ID_MAP.tag("s#{}#to#{}#l".format(self.source.service_spec.service_name,
                                                           self.dest.spec.service_name)),
                    ID_MAP.tag("s#{}#interface#l#tx".format(self.dest.spec.service_name))
                    ]
        else:
            tags = [ID_MAP.tag("s#{}#interface#l".format(self.dest.spec.service_name))]
        return tags

    @property
    def id(self) -> str:
        return "arrow_{}_{}_{}_connect_to".format(self.source_id, self.dest_id, self.connect_direction)

    @property
    def source_id(self) -> str:
        return self.source.group_id

    @property
    def dest_id(self) -> str:
        return self.dest.group_id

    @property
    def source_name(self) -> str:
        return self.source.service_spec.service_name

    @property
    def dest_name(self) -> str:
        return self.dest.spec.service_name

    @property
    def transport(self) -> str:
        return self.source.connector.transport

    @property
    def protocol(self) -> str:
        if self.source.connector.has_protocol:
            return self.source.connector.protocol
        return ""

    @property
    def description(self) -> str:
        return self.source.connector.description