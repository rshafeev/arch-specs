import os
import xml
import xml.etree.ElementTree as ET
from typing import Optional

from aiofile import AIOFile

from core.git.branch import Branch
from core.specs.specs import ServicesSpecs
from diagrams_generator.diagrams.geometry import Position
from diagrams_generator.diagrams.styles_wrapper import StyleSelector
from diagrams_generator.diagrams.template import XmlTemplate
from diagrams_generator.diagrams.xml.arrow.connect_to_arrow import XmlConnectToArrow
from diagrams_generator.diagrams.xml.arrow.topics_arrow import XmlTopicsArrow
from diagrams_generator.diagrams.xml.arrow.topics_container_arrow import XmlTopicsContainerArrow
from diagrams_generator.diagrams.xml.service import XmlService
from diagrams_generator.diagrams.xml_service_gen import XmlServiceGen


class Generator:
    services_specs: ServicesSpecs

    node_topics: dict

    xml_root: ET.Element

    diagram_root_xml: ET.Element

    template_meta: dict

    xml_services: dict

    config: dict

    styles: StyleSelector

    service_gen: XmlServiceGen

    current_branch: Branch

    show_connect_to_arrow: bool

    template: XmlTemplate

    def __init__(self,
                 config: dict,
                 services_specs: ServicesSpecs,
                 template: XmlTemplate,
                 styles: StyleSelector,
                 current_branch: Branch,
                 show_connect_to_arrow=False):
        self.node_topics = {}
        self.xml_services = {}
        self.config = config
        self.services_specs = services_specs
        self.current_branch = current_branch
        self.show_connect_to_arrow = show_connect_to_arrow
        self.styles = styles
        self.service_gen = XmlServiceGen(self.config, self.styles, self.services_specs)
        self.template = template

    async def generate(self):
        await self.__generate()

    def xml_service(self, service_name: str) -> Optional[XmlService]:
        if service_name in self.xml_services:
            return self.xml_services[service_name]
        return None

    def available_services(self):
        return self.services_specs.available_services

    async def _generate_xml_service(self, service_name) -> XmlService:
        return await self.service_gen.generate(service_name)

    async def generate_xml_services(self, root_xml: ET.Element):
        xml_services = []

        for service_name in self.available_services():
            if service_name in self.xml_services:
                continue
            xml_service = await self._generate_xml_service(service_name)
            xml_services.append(xml_service)
            self.xml_services[service_name] = xml_service

        for xml_service in xml_services:
            xml_service.add_to_root(root_xml)

        self.set_position()

    def set_position(self):
        service_categories_seq = self.services_specs.service_categories.all
        column_services_h = 0
        column_services_cnt = 0
        column_services_h_max = 1200
        column_services_cnt_max = self.styles.props["system"]["column_services_cnt_max"]
        max_column_w = 0
        x = 0
        y = 0
        for service_category in service_categories_seq:
            for service_name in self.xml_services:
                specs = self.services_specs.get_service_spec(service_name)
                if specs.category != service_category:
                    continue
                xml_service = self.xml_services[service_name]
                xml_service.set_position(Position(x, y))
                geom = xml_service.normalize_size()
                max_column_w = max(max_column_w, geom.w)
                column_services_h = column_services_h + geom.h + 20
                column_services_cnt = column_services_cnt + 1
                if column_services_h > column_services_h_max or \
                        column_services_cnt >= column_services_cnt_max:
                    column_services_h = 0
                    x = x + max_column_w + 50
                    y = 0
                    max_column_w = 0
                    column_services_cnt = 0
                else:
                    y = y + geom.h + 10

    async def generate_xml_topic_container_arrows(self, root_xml: ET.Element, broker_name="kafka"):
        arrows = []
        for service_name in self.xml_services:
            xml_service = self.xml_service(service_name)
            for direction in xml_service.topics_containers:
                topics_container = xml_service.topics(direction)
                if topics_container.broker_name == broker_name:
                    continue
                kafka_service = self.xml_service(topics_container.broker_name)
                if kafka_service is None:
                    continue

                arrow = XmlTopicsContainerArrow(self.config, self.styles, topics_container, kafka_service,
                                                topics_direction="tx",
                                                style_name='service-topics-arrow')
                arrows.append(arrow)
                arrow = XmlTopicsContainerArrow(self.config, self.styles, topics_container, kafka_service,
                                                topics_direction="rx",
                                                style_name='service-topics-arrow')
                arrows.append(arrow)

        for arrow in arrows:
            arrow.add_to_root(root_xml)

    async def generate_xml_topic_arrows(self, root_xml: ET.Element, kafka_name='kafka'):
        arrows = []
        topics = {}
        for service_name in self.xml_services:
            xml_service = self.xml_service(service_name)
            for direction in xml_service.topics_containers:
                topics_container = xml_service.topics(direction)
                for topic in topics_container.topics:
                    # if topic.broker_name != kafka_name:
                    #     continue
                    if topic.name not in topics:
                        topics[topic.name] = {
                            'tx': [],
                            'rx': []
                        }
                    topics[topic.name][topic.direction].append(topic)

        for topic_name in topics:
            if len(topics[topic_name]['tx']) == 0 or len(topics[topic_name]['tx']) == 0:
                for topic_tx in topics[topic_name]['tx']:
                    topic_tx.disable_link()
                for topic_rx in topics[topic_name]['rx']:
                    topic_rx.disable_link()

            for topic_tx in topics[topic_name]['tx']:
                for topic_rx in topics[topic_name]['rx']:
                    topic_rx.set_producer_name(topic_tx.service_name)
                    if not topic_rx.has_link_destination or not topic_tx.has_link_destination:
                        continue
                    if topic_tx.service_name == topic_rx.service_name:
                        continue
                    arrow = XmlTopicsArrow(self.config, self.styles, topic_tx, topic_rx, topics_direction="tx",
                                           style_name='service-topics-arrow')
                    arrows.append(arrow)
                    arrow = XmlTopicsArrow(self.config, self.styles, topic_tx, topic_rx, topics_direction="rx",
                                           style_name='service-topics-arrow')
                    arrows.append(arrow)

        for arrow in arrows:
            arrow.add_to_root(root_xml)

    async def generate_xml_connect_to_arrows(self, root_xml: ET.Element):
        arrows = []
        for service_name in self.xml_services:
            xml_service = self.xml_service(service_name)
            for connector in xml_service.connectors:
                connect_to_service = self.xml_service(connector.connect_to_service)
                if connect_to_service is None:
                    connector.disable_link()
                    continue
                arrow = XmlConnectToArrow(self.config, self.styles, connector, connect_to_service,
                                          connect_direction="tx", visible=self.show_connect_to_arrow)
                arrows.append(arrow)
                arrow.add_to_root(root_xml)

                arrow = XmlConnectToArrow(self.config, self.styles, connector, connect_to_service,
                                          connect_direction="rx", visible=self.show_connect_to_arrow)
                arrows.append(arrow)
                arrow.add_to_root(root_xml)

    async def __add_xml_objects(self):
        await self.generate_xml_services(self.diagram_root_xml)
        await self.generate_xml_topic_arrows(self.diagram_root_xml)
        await self.generate_xml_topic_container_arrows(self.diagram_root_xml)
        await self.generate_xml_connect_to_arrows(self.diagram_root_xml)

    async def __generate(self):
        self.xml_root = self.template.parse()
        self.diagram_root_xml = self.xml_root.findall('diagram/mxGraphModel/root')[0]
        await self.__add_xml_objects()

    async def save(self, output_xml_path: str):
        if not os.path.exists(output_xml_path):
            os.makedirs(output_xml_path)
        xmlstr = xml.etree.ElementTree.tostring(self.xml_root, encoding='utf8', method='xml')
        async with AIOFile(output_xml_path + '/system_arch_diagram.xml', "w+") as out:
            await out.write(xmlstr.decode("utf8"))
