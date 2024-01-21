import os
import xml
from typing import Optional
from xml.etree.ElementTree import ElementTree

from aiofile import AIOFile
import xml.etree.ElementTree as ET
from core.git.branch import Branch
from core.specs.service.connector import ChannelType
from core.specs.service.spec import ServiceSpec
from core.specs.specs import ServicesSpecs
from diagrams_generator.diagrams.geometry import Position, Geometry
from diagrams_generator.diagrams.template import XmlTemplate
from diagrams_generator.diagrams.xml.service import XmlService
from diagrams_generator.generator.generator import Generator
from diagrams_generator.generator.service.service_style_selector import ServiceStyleSelector


class ServiceNetworkGenerator(Generator):
    service: ServiceSpec

    styles_: ServiceStyleSelector

    def __init__(self,
                 service_name: str,
                 config: dict,
                 services_specs: ServicesSpecs,
                 template: XmlTemplate,
                 styles: ServiceStyleSelector,
                 current_branch: Branch,
                 show_connect_to_arrow: bool):
        self.service = services_specs.get_service_spec(service_name)
        self.styles_ = styles
        super().__init__(config, services_specs, template, styles, current_branch, show_connect_to_arrow)

    async def save(self, output_xml_path: str):
        diagram_dir = output_xml_path + "/specs/" + self.service.service_name
        if not os.path.exists(diagram_dir):
            os.makedirs(diagram_dir)
        xmlstr = xml.etree.ElementTree.tostring(self.xml_root, encoding='utf8', method='xml')
        async with AIOFile(diagram_dir + '/network_diagram.xml', "w+") as out:
            await out.write(xmlstr.decode("utf8"))

    async def __highlight_topics(self):
        selected_service_topics = {}
        selected_xml_service = self.xml_service(self.service.service_name)
        for direction in selected_xml_service.topics_containers:
            topics_container = selected_xml_service.topics(direction)
            for topic in topics_container.topics:
                selected_service_topics[topic.name] = {}

        for service_name in self.xml_services:
            xml_service = self.xml_service(service_name)
            for direction in xml_service.topics_containers:
                topics_container = xml_service.topics(direction)
                for topic in topics_container.topics:
                    if topic.has_link and topic.name in selected_service_topics:
                        style = self.styles_.topic_with_link_style(topic.direction)
                        topic.set_style(style)

    async def generate(self):
        await super().generate()
        await self.__highlight_topics()

    def available_services(self):
        services_list = []
        producers_list = []
        consumers_list = []
        connectors = []
        if self.service.has_connectors:
            for connector in self.service.connectors:
                services_list.append(connector.dest.service_name)
                if connector.has_channels is False:
                    continue
                broker = connector.dest
                for channel_name in connector.channels:
                    if connector.channel_type == ChannelType.celery_task:
                        channel = broker.celery_task(channel_name)
                    elif connector.channel_type == ChannelType.topic:
                        channel = broker.topic(channel_name)
                    else:
                        continue
                    if channel is not None and connector.data_direction == 'rx' and 'tx' in channel:
                        for producer_name in channel['tx']:
                            producers_list.append(producer_name)
                    if channel is not None and connector.data_direction == 'tx' and 'rx' in channel:
                        for producer_name in channel['rx']:
                            producers_list.append(producer_name)

        for service_name in self.services_specs.available_services:
            spec = self.services_specs.get_service_spec(service_name)
            if 'connect_to' in spec.raw and spec.raw['connect_to'] is not None:
                for connect_to in spec.raw["connect_to"]:
                    if connect_to['name'] == self.service.service_name:
                        connectors.append(service_name)
        services_list.extend(producers_list)
        services_list.append(self.service.service_name)
        services_list.extend(consumers_list)
        services_list.extend(connectors)
        return services_list

    def set_position(self):
        service_categories_seq = self.services_specs.service_categories.all
        column_services_h = 0
        max_column_w = 0
        x = 0
        y = 0
        columns = [[], [], []]
        all_services = []
        for service_category in service_categories_seq:
            for service_name in self.xml_services:
                if service_name == self.service.service_name:
                    continue
                specs = self.services_specs.get_service_spec(service_name)
                if specs.category != service_category:
                    continue
                all_services.append(service_name)
        columns[1].append(self.service.service_name)
        if len(all_services) > 0:
            left_h = 0
            right_h = 0
            for service in all_services:
                xml_service = self.xml_services[service_name]

                if left_h <= right_h:
                    columns[0].append(service)
                    left_h = left_h + xml_service.geom.h
                else:
                    columns[2].append(service)
                    right_h = right_h + xml_service.geom.h
        if len(columns[0]) + len(columns[2]) != len(all_services):
            raise Exception("Logic Error!")

        column_h_max = 0.0
        for column in columns:
            for service_name in column:
                xml_service = self.xml_services[service_name]
                xml_service.set_position(Position(x, y))
                geom = xml_service.normalize_size()
                max_column_w = max(max_column_w, geom.w)
                column_services_h = column_services_h + geom.h + 20
                y = y + geom.h + 10
            column_h_max = max(column_h_max, column_services_h)
            column_services_h = 0.0
            x = x + max_column_w + 190
            y = 0
            max_column_w = 0

        selected_xml_service = self.xml_services[self.service.service_name]
        geom = selected_xml_service.geom
        y = max(column_h_max / 2 - geom.w / 2, 110)
        selected_xml_service.set_position(Position(geom.x, y))
        selected_service_geom = selected_xml_service.normalize_size()
        self.__set_control_panel_position(selected_service_geom)

    def __set_control_panel_position(self, selected_service_geom: Geometry):
        control_panel = self.__control_panel_group()
        control_panel_w = float(control_panel.find("mxGeometry").attrib['width'])
        control_panel.find("mxGeometry").attrib['x'] = str(selected_service_geom.x + (selected_service_geom.w - control_panel_w) / 2)
        control_panel.find("mxGeometry").attrib['y'] = str(-30)

    def __control_panel_group(self) -> Optional[ET.Element]:
        for e in self.diagram_root_xml.findall("mxCell"):
            if e.attrib['id'] == "control#panel#group":
                return e
        return None

    async def _generate_xml_service(self, service_name) -> XmlService:
        if service_name != self.service.service_name:
            return await self.service_gen.generate(service_name)
        return await self.service_gen.generate(service_name)
