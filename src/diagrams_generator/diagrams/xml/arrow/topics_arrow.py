from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import StyleSelector
from diagrams_generator.diagrams.xml.arrow.arrow import XmlArrow
from diagrams_generator.diagrams.xml.topic import XmlTopic


class XmlTopicsArrow(XmlArrow):
    source: XmlTopic

    dest: XmlTopic

    topics_direction: str

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 source: XmlTopic,
                 dest: XmlTopic,
                 topics_direction: str,
                 style_name='service-topics-arrow'):
        self.source = source
        self.dest = dest
        self.topics_direction = topics_direction
        style = styles.style(style_name)
        super().__init__(config, styles, style)
        if self.source.position_global.x > self.dest.position_global.x + self.dest.geom.w:
            self.set_left_side_connect_for_source()
            self.set_right_side_connect_for_destination()
        else:
            self.set_right_side_connect_for_source()
            self.set_left_side_connect_for_destination()

    @property
    def tags(self):
        if self.topics_direction == 'rx':
            tags = [ID_MAP.tag("broker#{}#topic#{}#l#rx".format(self.dest.broker_name,
                                                       self.dest.name)),
                    ID_MAP.tag("broker#{}#topic#{}#{}#l".format(self.dest.broker_name,
                                                       self.dest.name,
                                                       self.dest.service_name))
                    ]
        else:
            tags = [ID_MAP.tag("broker#{}#topic#{}#l".format(self.source.broker_name,
                                                    self.source.name))]
        return tags

    @property
    def id(self) -> str:
        return "arrow_{}_{}_{}".format(self.source.id, self.dest.id, self.topics_direction)

    @property
    def source_id(self) -> str:
        return self.source.id

    @property
    def dest_id(self) -> str:
        return self.dest.id

    @property
    def source_name(self) -> str:
        return self.source.service_name

    @property
    def dest_name(self) -> str:
        return self.dest.service_name