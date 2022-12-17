from core.specs.service.spec import ServiceType
from core.specs.specs import ServicesSpecs
from diagrams_generator.diagrams.styles_wrapper import StyleSelector
from diagrams_generator.diagrams.xml.kafka_service import XmlKafkaService
from diagrams_generator.diagrams.xml.service import XmlService


class XmlServiceGen:
    config: dict

    services_specs: ServicesSpecs

    styles: StyleSelector

    def __init__(self,
                 config: dict,
                 styles: StyleSelector,
                 services_specs: ServicesSpecs):
        self.config = config
        self.styles = styles
        self.services_specs = services_specs

    async def generate(self, service_name: str) -> XmlService:
        service_spec = self.services_specs.get_service_spec(service_name)
        if service_spec.type == ServiceType.kafka.value:
            xml_service = XmlKafkaService(self.config, self.styles, service_spec, self.services_specs)
        else:
            xml_service = XmlService(self.config, self.styles, service_spec, self.services_specs)
        await xml_service.generate()
        return xml_service
