import logging
import os
from typing import Tuple, Dict, List

from core.specs.service.spec import ServiceType
from core.specs.specs import ServicesSpecs


class TopicsValidator:

    __services_specs: ServicesSpecs

    def __init__(self, services_specs: ServicesSpecs):
        self.__services_specs = services_specs

    def validate(self) -> Tuple[bool, List[Dict[str, str]], List[Dict[str, str]]]:
        errors = []
        warns = []
        for service_name in self.__services_specs.all_services:
            service_spec = self.__services_specs.get_service_spec(service_name)

            if not service_spec.is_product:
                continue
            if service_spec.type == ServiceType.kafka.value:
                for topic_name in service_spec.raw["topics"]:
                    info = service_spec.kafka_topic_info(topic_name)
                    if 'protocol' in info and info['protocol'].find("{{dash_repo_master}}") != -1:
                        path = os.path.dirname(__file__) + "/../../../../.."
                        fpath_s = info['protocol'].find('/')
                        fpath_f = info['protocol'].rfind('.proto')
                        if fpath_s >= 0 and fpath_f >= 0:
                            protocol_fname = path + info['protocol'][fpath_s:fpath_f+6]
                            if not os.path.isfile(protocol_fname):
                                errors.append({
                                    'service': service_name,
                                    'error': "[{}] topic. Could not find .proto file {} in dash!".format(topic_name, protocol_fname)
                                })

                    if ('tx' not in info or info['tx'] is None or len(info['tx']) == 0) and \
                            ('rx' not in info or info['rx'] is None or len(info['rx']) == 0):
                        warns.append({
                            'service': "kafka",
                            'warn': "[{}] topic. Wrong topic!".format(topic_name)
                        })
                    else:
                        if 'tx' not in info or info['tx'] is None or len(info['tx']) == 0:
                            warns.append({
                                'service': service_name,
                                'warn': "[{}] topic. Could not find any producers".format(topic_name)
                            })
                        if 'rx' not in info or info['rx'] is None or len(info['rx']) == 0:
                            warns.append({
                                'service': service_name,
                                'warn': "[{}] topic. Could not find any consumers".format(topic_name)
                            })
                    if "sales-demo-" not in topic_name and ('desc' not in info or info['desc'] is None or len(info['desc']) == 0):
                        warns.append({
                            'service': service_name,
                            'warn': "[{}] topic. no description".format(topic_name)
                        })
                    if "sales-demo-" not in topic_name and ('protocol' not in info or info['protocol'] is None or len(info['protocol']) == 0):
                        warns.append({
                            'service': service_name,
                            'warn': "[{}] topic. no protocol".format(topic_name)
                        })
        return len(errors) == 0, errors, warns

    @staticmethod
    def print(errors: List[Dict[str, str]], warns: List[Dict[str, str]]):
        for e in errors:
            logging.error("[{}]: {}".format(e["service"], e["error"]))

        for e in warns:
            logging.warning("[{}]: {}".format(e["service"], e["warn"]))

        if len(errors) > 0:
            logging.error("Validation Results: Failed.")
        else:
            logging.info("Validation Results: OK.")
