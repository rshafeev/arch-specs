from typing import Optional

from core.specs.service.connector import ServiceSpecConnector
from core.specs.service.spec import ServiceSpec
from diagrams_generator.diagrams.styles_wrapper import StyleSelector, StylesWrapper, Style


class ServiceStyleSelector(StyleSelector):
    service: ServiceSpec

    def __init__(self, service: ServiceSpec, styles: StylesWrapper):
        self.service = service
        super().__init__(styles)

    def service_style(self, spec: ServiceSpec) -> Optional[Style]:
        if spec.service_name == self.service.service_name:
            return self.style('service-container-selected')
        return super().service_style(spec)

    def topic_style(self, spec: ServiceSpec, connector: ServiceSpecConnector, topic_name: str) -> Optional[Style]:
        if spec.service_name == self.service.service_name:
            style_name = "service-topic-{}-selected".format(connector.data_direction)
            return self.style(style_name)
        return super().topic_style(spec, connector, topic_name)

    def topic_with_link_style(self, data_direction: str) -> Optional[Style]:
        style_name = "service-topic-{}-selected".format(data_direction)
        return self.style(style_name)

    def topic_container_style(self, spec: ServiceSpec, connector: ServiceSpecConnector) -> Optional[Style]:
        if spec.service_name == self.service.service_name:
            return self.style('service-topics-container-selected')
        return super().topic_container_style(spec, connector)

    def topic_container_label_style(self, spec: ServiceSpec, connector: ServiceSpecConnector) -> Optional[Style]:
        if spec.service_name == self.service.service_name:
            return self.style('service-topics-container-label-selected')
        return super().topic_container_label_style(spec, connector)
