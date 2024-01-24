import json
import logging
import os
from typing import Optional

import markdown2
from jinja2 import Template

from core.git.branch import Branch
from core.specs.service.connector import ChannelType
from core.specs.service.spec import ServiceSpec, ServiceType
from core.specs.specs import ServicesSpecs


class SpecsGenerator:
    services_specs: ServicesSpecs

    conf: dict

    __wiki_pages: list

    handbook_service_template: Template

    __branch: Branch

    def __init__(self, meta_path, app_configuration: dict, topics_info_filename: str, branch: Branch):
        self.conf = app_configuration
        self.__branch = branch
        self.services_specs = ServicesSpecs(meta_path, topics_info_filename, branch)

    def is_show_service(self, service_specs: ServiceSpec):
        if self.__branch.is_release and not service_specs.is_release_service:
            return False
        if self.__branch.is_master and not service_specs.is_master_service:
            return False
        return service_specs.is_master_service

    @staticmethod
    def html_link(link, title):
        if link is None:
            return "<p>{}</p>".format(title)
        return "<a href=\"{}\">{}</a>".format(link, title)

    def service_link(self, service_name):
        service = self.services_specs.get_service_spec(service_name)
        if service.service_module == 'external':
            link = None
        else:
            link = '{}/{}/{}'.format(
                self.services_specs.settings.confluence.link,
                self.services_specs.settings.confluence.space,
                service.wiki_name)
        return link

    def get_topics_info_from_producer(self, kafka_service_name: str, topic_name: str) -> Optional[dict]:
        for service_name in self.services_specs.available_services:
            service_specs = self.services_specs.get_service_spec(service_name)
            if service_specs.raw is None or \
                    'connect_to' not in service_specs.raw or \
                    service_specs.raw['connect_to'] is None:
                continue
            for c in service_specs.raw['connect_to']:
                if "topics" not in c or \
                        not isinstance(c["topics"], list) or \
                        c['name'] != kafka_service_name or \
                        c['data_direction'] != "tx":
                    continue
                for topic in c['topics']:
                    if topic['name'] == topic_name:
                        return topic
        return None


    def markdown2html(self, md_template_text: str) -> str:
        j2_template = Template(md_template_text)
        vars = self.services_specs.settings.markdown_template_vars
        md_text = j2_template.render(vars)
        return markdown2.markdown(md_text)

    def build_service_topics_table(self, service: ServiceSpec, direction: str):
        if service is None or len(service.connectors) == 0:
            return []
        rows = []
        for connector in service.connectors:
            if not connector.dest.is_kafka_broker:
                continue
            if connector.data_direction == direction:
                broker = connector.dest
                broker_link = self.service_link(broker.service_name)
                if connector.channel_type != ChannelType.topic:
                    continue

                for channel_name in connector.channels:
                    channel = connector.channels[channel_name]
                    topic_info = broker.topic(channel_name)
                    row = {
                        "Broker": self.html_link(broker_link, broker.service_name),
                        "Topic": channel_name,
                        "OffsetStorage": "-",
                        "Description": "",
                        "Protocol": "-",
                    }
                    if direction == "rx":
                        if connector.offset_storage is not None:
                            row['OffsetStorage'] = connector.offset_storage
                    if topic_info is not None and "desc" in topic_info and topic_info['desc'] is not None and len(
                            topic_info['desc']) > 0:
                        row["Description"] = self.markdown2html(topic_info["desc"])

                    if topic_info is not None and "protocol" in topic_info and topic_info["protocol"] is not None:
                        row["Protocol"] = self.markdown2html(topic_info["protocol"])

                    if direction == "rx":
                        producer_topic_info = self.get_topics_info_from_producer(connector.dest.service_name, channel_name)
                        if producer_topic_info is not None and \
                                "Description" not in row and \
                                "desc" in producer_topic_info and \
                                producer_topic_info['desc'] is not None and \
                                len(producer_topic_info['desc']) > 0:
                            row["Description"] = self.markdown2html(producer_topic_info["desc"])
                        if producer_topic_info is not None and \
                                "Protocol" not in row and \
                                "protocol" in producer_topic_info and \
                                producer_topic_info["protocol"] is not None:
                            row["Protocol"] = self.markdown2html(producer_topic_info["protocol"])

                    self.__producers_row(connector.dest, channel_name, row)
                    self.__consumers_row(connector.dest, channel_name, row)
                    if 'Producers' not in row:
                        row['Producers'] = "-"
                    if 'Consumers' not in row:
                        row['Consumers'] = "-"
                    rows.append(row)
        return rows

    def build_service_tasks_table(self, service: ServiceSpec, direction: str):
        if service is None or service.has_connectors is False:
            return []
        rows = []

        for connector in service.connectors:
            if connector.data_direction == direction:
                broker = connector.dest
                broker_link = self.service_link(broker.service_name)
                if connector.channel_type != ChannelType.celery_task:
                    continue
                for channel_name in connector.channels:
                    channel = connector.channels[channel_name]
                    task_info = broker.celery_task(channel_name)
                    row = {
                        "Broker": self.html_link(broker_link, broker.service_name),
                        "CeleryTask": channel_name,
                        "Description": ""
                    }
                    if channel is not None and "desc" in channel and channel['desc'] is not None and len(
                            channel['desc']) > 0:
                        row["Description"] = self.markdown2html(channel["desc"])

                    self.__producers_row(connector.dest, channel_name, row)
                    self.__consumers_row(connector.dest, channel_name, row)
                    if 'Producers' not in row:
                        row['Producers'] = "-"
                    if 'Consumers' not in row:
                        row['Consumers'] = "-"
                    rows.append(row)
        return rows

    def build_service_queues_table(self, service: ServiceSpec, direction: str):
        if service is None or service.has_connectors is False:
            return []
        rows = []

        for connector in service.connectors:
            if connector.data_direction == direction:
                broker = connector.dest
                broker_link = self.service_link(broker.service_name)
                if not broker.is_mq_broker:
                    continue
                if connector.channel_type != ChannelType.queue:
                    continue
                for channel_name in connector.channels:
                    channel = connector.channels[channel_name]
                    queue_info = broker.queue(channel_name)
                    row = {
                        "Broker": self.html_link(broker_link, broker.service_name),
                        "Queue": channel_name,
                    }
                    if channel is not None and "desc" in channel and channel['desc'] is not None and len(
                            channel['desc']) > 0:
                        row["Description"] = self.markdown2html(channel["desc"])
                    elif queue_info is  not None and "desc" in queue_info:
                        row["Description"] = self.markdown2html(queue_info["desc"])
                    self.__producers_row(connector.dest, channel_name, row)
                    self.__consumers_row(connector.dest, channel_name, row)
                    if 'Producers' not in row:
                        row['Producers'] = "-"
                    if 'Consumers' not in row:
                        row['Consumers'] = "-"
                    rows.append(row)
        return rows

    def build_service_rmq_queues_table(self, service: ServiceSpec, direction: str):
        if (service is None or
                service.has_connectors is False):
            return []
        rows = []

        for connector in service.connectors:
            broker = connector.dest
            if not broker.is_rabbitmq_broker:
                continue
            broker_link = self.service_link(broker.service_name)

            if connector.data_direction == 'rx' and direction == 'rx':
                for channel_name in connector.channels:
                    channel = connector.channels[channel_name]
                    queue_info = broker.queue(channel_name)
                    row = {
                        "Broker": self.html_link(broker_link, broker.service_name),
                        "Queue": channel_name,
                    }
                    if 'protocol' in queue_info:
                        row["Protocol"] = self.markdown2html(queue_info["protocol"])
                    if 'binding' in queue_info and queue_info['binding'] is not None:
                        binding_s = ""
                        for binding in queue_info['binding']:
                            if len(binding_s) > 0:
                                binding_s = binding_s + ", "
                            binding_s = binding_s + binding["exchange"] + "/ "
                            if "routing_key" in binding and binding["routing_key"] is not None:
                                binding_s = binding_s + binding["routing_key"]
                        row["Binding(Exchange / Routing Key)"] = binding_s

                    if channel is not None and "desc" in channel and channel['desc'] is not None and len(
                            channel['desc']) > 0:
                        row["Description"] = self.markdown2html(channel["desc"])
                    elif queue_info is not None and "desc" in queue_info:
                        row["Description"] = self.markdown2html(queue_info["desc"])
                    self.__producers_row(connector.dest, channel_name, row)
                    self.__consumers_row(connector.dest, channel_name, row)
                    if 'Producers' not in row:
                        row['Producers'] = "-"
                    if 'Consumers' not in row:
                        row['Consumers'] = "-"
                    rows.append(row)

            if connector.data_direction == 'tx' and direction == 'tx':

                for channel_name in connector.channels:
                    channel = connector.channels[channel_name]
                    exchange_s = channel["exchange"] + "/ "
                    if "routing_key" in channel and channel["routing_key"] is not None:
                        exchange_s = exchange_s + channel["routing_key"]
                    binding_queues = broker.get_binding_rabbitmq_queues(channel)
                    for queue in binding_queues:
                        queue_name = queue["name"]
                        row = {
                            "Broker": self.html_link(broker_link, broker.service_name)
                        }
                        if 'protocol' in queue:
                            row["Protocol"] = self.markdown2html(queue["protocol"])
                        row["Exchange / Routing Key"] = exchange_s
                        row["Binding Queue"] = queue_name
                        if queue is not None and "desc" in queue and queue['desc'] is not None and len(
                                queue['desc']) > 0:
                            row["Description"] = self.markdown2html(queue["desc"])
                        self.__producers_row(connector.dest, queue_name, row)
                        self.__consumers_row(connector.dest, queue_name, row)
                        if 'Producers' not in row:
                            row['Producers'] = "-"
                        if 'Consumers' not in row:
                            row['Consumers'] = "-"
                        rows.append(row)
        return rows

    def __producers_row(self, service: ServiceSpec, channel_name, output_row):
        if service.is_kafka_broker:
            channel = service.topics[channel_name]
        if service.is_celery_broker:
            channel = service.celery_tasks[channel_name]
        if service.is_mq_broker:
            channel = service.queues[channel_name]
        if service.is_rabbitmq_broker:
            channel = service.queues[channel_name]

        if channel is not None and 'tx' in channel:
            for service_name in channel['tx']:
                service_spec = self.services_specs.get_service_spec(service_name)
                if not self.is_show_service(service_spec):
                    continue
                if not service_spec.is_release_service:
                    postfix_name = "[{}]".format(service_spec.raw["status"])
                else:
                    postfix_name = ""
                html_link = self.html_link(self.service_link(service_name), postfix_name + service_spec.service_name)
                if 'Producers' not in output_row:
                    output_row['Producers'] = ""
                output_row['Producers'] = str(output_row['Producers']) + " " + html_link

    def __consumers_row(self, service: ServiceSpec, channel_name, output_row):
        if service.is_kafka_broker:
            channel = service.topics[channel_name]
        if service.is_celery_broker:
            channel = service.celery_tasks[channel_name]
        if service.is_mq_broker:
            channel = service.queues[channel_name]
        if service.is_rabbitmq_broker:
            channel = service.queues[channel_name]

        if channel is not None and 'rx' in channel:
            for service_name in channel['rx']:
                service_spec = self.services_specs.get_service_spec(service_name)
                if not self.is_show_service(service_spec):
                    continue
                if not service_spec.is_release_service:
                    postfix_name = "[{}]".format(service_spec.raw["status"])
                else:
                    postfix_name = ""
                if 'Consumers' not in output_row:
                    output_row['Consumers'] = ""
                html_link = self.html_link(self.service_link(service_name), postfix_name + service_spec.service_name)
                output_row['Consumers'] = str(output_row['Consumers']) + " " + html_link

    def build_topics_usage_table(self, service: ServiceSpec):
        rows = []
        if not service.is_kafka_broker:
            return
        for topic_name in service.topics:
            topic = service.topics[topic_name]
            row = {
                'Topic': topic_name,
            }
            self.__producers_row(service, topic_name, row)
            self.__consumers_row(service, topic_name, row)

            if 'Producers' not in row and 'Consumers' not in row:
                continue

            if topic is not None and \
                    "desc" in topic and \
                    topic['desc'] is not None and \
                    len(topic['desc']) > 0:
                row["Description"] = self.markdown2html(topic["desc"])
            if topic is not None and \
                    "protocol" in topic and \
                    topic["protocol"] is not None:
                row["Protocol"] = self.markdown2html(topic["protocol"])

            if 'Producers' not in row:
                row['Producers'] = "-"
            if 'Consumers' not in row:
                row['Consumers'] = "-"
            rows.append(row)
        return rows

    def build_queues_usage_table(self, service: ServiceSpec):
        rows = []
        if not service.is_mq_broker:
            return
        for queue_name in service.queues:
            queue = service.queues[queue_name]

            row = {
                'Queue': queue_name,
            }
            self.__producers_row(service, queue_name, row)
            self.__consumers_row(service, queue_name, row)

            if 'Producers' not in row and 'Consumers' not in row:
                continue

            if queue is not None and \
                    "desc" in queue and \
                    queue['desc'] is not None and \
                    len(queue['desc']) > 0:
                row["Description"] = self.markdown2html(queue["desc"])
            if queue is not None and \
                    "protocol" in queue and \
                    queue["protocol"] is not None:
                row["Protocol"] = self.markdown2html(queue["protocol"])

            if 'Producers' not in row:
                row['Producers'] = "-"
            if 'Consumers' not in row:
                row['Consumers'] = "-"
            rows.append(row)
        return rows

    def build_celery_tasks_usage_table(self, service: ServiceSpec):
        rows = []
        for task_name in service.celery_tasks:
            task = service.celery_tasks[task_name]
            row = {
                'Task': task_name,
            }
            self.__producers_row(service, task_name, row)
            self.__consumers_row(service, task_name, row)

            if 'Producers' not in row and 'Consumers' not in row:
                continue

            if task is not None and \
                    "desc" in task and \
                    task['desc'] is not None and \
                    len(task['desc']) > 0:
                row["Description"] = self.markdown2html(task["desc"])
            if task is not None and \
                    "protocol" in task and \
                    task["protocol"] is not None:
                row["Protocol"] = self.markdown2html(task["protocol"])

            if 'Producers' not in row:
                row['Producers'] = "-"
            if 'Consumers' not in row:
                row['Consumers'] = "-"
            rows.append(row)
        return rows

    def build_rmq_queues_usage_table(self, service: ServiceSpec):
        rows = []
        if not service.is_rabbitmq_broker:
            return

        for queue_name in service.queues:
            queue = service.queues[queue_name]

            row = {
                'Queue': queue_name,
            }
            self.__producers_row(service, queue_name, row)
            self.__consumers_row(service, queue_name, row)

            if 'binding' in queue and queue['binding'] is not None:
                binding_s = ""
                for binding in queue['binding']:
                    if len(binding_s) > 0:
                        binding_s = binding_s + ", "
                    binding_s = binding_s + binding["exchange"] + "/ "
                    if "routing_key" in binding and binding["routing_key"] is not None:
                        binding_s = binding_s + binding["routing_key"]
                row["Binding(Exchange / Routing Key)"] = binding_s
            #
            # if 'Producers' not in row and 'Consumers' not in row:
            #     continue
            #
            if queue is not None and \
                    "desc" in queue and \
                    queue['desc'] is not None and \
                    len(queue['desc']) > 0:
                row["Description"] = self.markdown2html(queue["desc"])
            if queue is not None and \
                    "protocol" in queue and \
                    queue["protocol"] is not None:
                row["Protocol"] = self.markdown2html(queue["protocol"])

            if 'Producers' not in row:
                row['Producers'] = "-"
            if 'Consumers' not in row:
                row['Consumers'] = "-"
            rows.append(row)
        return rows

    def build_service_network_table(self, service_name: str):
        service_specs = self.services_specs.get_service_spec(service_name)
        rows = []
        rx_rows_dict = {}
        tx_rows_dict = {}

        if service_specs is not None and \
                'connect_to' in service_specs.raw and \
                service_specs.raw['connect_to'] is not None:
            for c in service_specs.raw['connect_to']:
                connect_to_service = self.services_specs.get_service_spec(c['name'])
                connect_to_service_link = self.service_link(c['name'])
                protocol = c["transport"]
                if "protocol" in c:
                    protocol = "{} (transport: {})".format(c["protocol"], c["transport"])  #todo: clean
                    protocol = c["protocol"]
                row = {
                    "ServiceName": self.html_link(connect_to_service_link, connect_to_service.wiki_name),
                    "ConnectDirection": "Outbound",
                    "Protocol": protocol,
                    "Description": " "
                }
                if "desc" in c:
                    row["Description"] = c["desc"]
                rx_rows_dict[connect_to_service.service_name] = row

        for tx_service_name in self.services_specs.available_services:
            tx_service_specs = self.services_specs.get_service_spec(tx_service_name)
            if tx_service_specs is not None and \
                    'connect_to' in tx_service_specs.raw and \
                    tx_service_specs.raw['connect_to'] is not None:
                for c in tx_service_specs.raw['connect_to']:
                    if c['name'] != service_name:
                        continue
                    if tx_service_specs.service_module == 'external':
                        tx_service_link = ""
                    else:
                        wiki_link = self.services_specs.settings.confluence.link
                        wiki_space = self.services_specs.settings.confluence.space
                        tx_service_link = '{}/{}/'.format(wiki_link, wiki_space) + tx_service_specs.wiki_name
                    protocol = c["transport"]
                    if "protocol" in c:
                        protocol = c["protocol"]
                    row = {
                        "ServiceName": self.html_link(tx_service_link, tx_service_specs.wiki_name),
                        "ConnectDirection": "Inbound",
                        "Protocol": protocol,
                        "Description": " "
                    }
                    if "desc" in c:
                        row["Description"] = c["desc"]
                    tx_rows_dict[tx_service_specs.service_name] = row

        for s in rx_rows_dict:
            rows.append(rx_rows_dict[s])
        for s in tx_rows_dict:
            rows.append(tx_rows_dict[s])

        return rows

    def build_internal_storages_table(self, service_name):
        spec = self.services_specs.get_service_spec(service_name)
        rows = []
        if not spec.has_internal_storages:
            return rows
        for storage in spec.internal_storages:
            row = {
                'Storage':  storage['name']
            }
            if storage is not None and \
                    "desc" in storage and \
                    storage['desc'] is not None and \
                    len(storage['desc']) > 0:
                row["Description"] = self.markdown2html(storage["desc"])
            if 'Description' not in row:
                row['Description'] = "-"
            rows.append(row)
        return rows

    @staticmethod
    def store_as_json_file(obj, fname):
        with open(fname, 'w+', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)

    def save(self, output_path: str):
        for service_name in self.services_specs.available_services:
            service_dir = output_path + "/" + service_name
            service_specs = self.services_specs.get_service_spec(service_name)
            if not os.path.exists(service_dir):
                os.makedirs(service_dir)

            internal_storages_table = self.build_internal_storages_table(service_name)
            self.store_as_json_file(internal_storages_table, service_dir + "/internal_storages.json")

            network_table = self.build_service_network_table(service_name)
            self.store_as_json_file(network_table, service_dir + "/network.json")

            if service_specs.is_broker:
                if service_specs.celery_tasks is not None:
                    tasks_usage_table = self.build_celery_tasks_usage_table(service_specs)
                    self.store_as_json_file(tasks_usage_table, service_dir + "/celery_tasks.json")
                if service_specs.is_kafka_broker is not None:
                    topics_usage_table = self.build_topics_usage_table(service_specs)
                    self.store_as_json_file(topics_usage_table, service_dir + "/topics.json")
                if service_specs.is_mq_broker:
                    queues_usage_table = self.build_queues_usage_table(service_specs)
                    self.store_as_json_file(queues_usage_table, service_dir + "/queues.json")
                if service_specs.is_rabbitmq_broker:
                    queues_usage_table = self.build_rmq_queues_usage_table(service_specs)
                    self.store_as_json_file(queues_usage_table, service_dir + "/rmq_queues.json")
            else:
                rx_topics_table = self.build_service_topics_table(service_specs, "rx")
                self.store_as_json_file(rx_topics_table, service_dir + "/rx_topics.json")
                tx_topics_table = self.build_service_topics_table(service_specs, "tx")
                self.store_as_json_file(tx_topics_table, service_dir + "/tx_topics.json")

                rx_tasks_table = self.build_service_tasks_table(service_specs, "rx")
                self.store_as_json_file(rx_tasks_table, service_dir + "/rx_celery_tasks.json")
                tx_tasks_table = self.build_service_tasks_table(service_specs, "tx")
                self.store_as_json_file(tx_tasks_table, service_dir + "/tx_celery_tasks.json")

                rx_queues_table = self.build_service_queues_table(service_specs, "rx")
                self.store_as_json_file(rx_queues_table, service_dir + "/rx_queues.json")
                tx_queues_table = self.build_service_queues_table(service_specs, "tx")
                self.store_as_json_file(tx_queues_table, service_dir + "/tx_queues.json")

                rx_rmq_queues_table = self.build_service_rmq_queues_table(service_specs, "rx")
                self.store_as_json_file(rx_rmq_queues_table, service_dir + "/rx_rmq_queues.json")
                tx_rmq_queues_table = self.build_service_rmq_queues_table(service_specs, "tx")
                self.store_as_json_file(tx_rmq_queues_table, service_dir + "/tx_rmq_queues.json")