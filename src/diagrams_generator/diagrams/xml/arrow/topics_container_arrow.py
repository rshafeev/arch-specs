from diagrams_generator.diagrams.id_map import ID_MAP
from diagrams_generator.diagrams.styles_wrapper import StyleSelector
from diagrams_generator.diagrams.xml.arrow.arrow import XmlArrow
from diagrams_generator.diagrams.xml.service import XmlService
from diagrams_generator.diagrams.xml.topics_container import XmlTopicsContainer


class XmlTopicsContainerArrow(XmlArrow):
    topics_container: XmlTopicsContainer

    kafka_service: XmlService

    topics_direction: str

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 topics_container: XmlTopicsContainer,
                 kafka_service: XmlService,
                 topics_direction: str,
                 style_name='service-connect-to-arrow',
                 visible=False
                 ):
        self.topics_container = topics_container
        self.kafka_service = kafka_service
        self.topics_direction = topics_direction
        style = styles.style(style_name)
        super().__init__(config, styles, style, static=False, visible=visible)
        if self.kafka_service.position_global.x > self.topics_container.position_global.x + \
                self.topics_container.geom.w:
            self.set_right_side_connect_for_destination()
            self.set_left_side_connect_for_source()

    @property
    def tags(self):
        if self.topics_direction == 'tx':
            tags = [ID_MAP.tag("container#{}#to#{}#l".format(self.topics_container.spec.service_name,
                                                           self.kafka_service.spec.service_name)),
                    ID_MAP.tag("container#{}#interface#l#tx".format(self.kafka_service.spec.service_name))
                    ]
        else:
            tags = [ID_MAP.tag("container#{}#interface#l".format(self.kafka_service.spec.service_name))]
        return tags

    @property
    def id(self) -> str:
        return "arrow_{}_{}_{}_connect_to".format(self.topics_container.id, self.kafka_service.id,
                                                  self.topics_direction)

    @property
    def source_id(self) -> str:
        return self.kafka_service.group_id

    @property
    def dest_id(self) -> str:
        return self.topics_container.id
