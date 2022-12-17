from enum import Enum, auto
from typing import Dict

from jinja2 import Template


class HtmlComponentTemplateName(Enum):
    service_properties = auto()
    include_page = auto()
    expand = auto()
    info = auto()

    @property
    def dir(self):
        return "component"


class HtmlPageTemplateName(Enum):
    component_branch_diagram = auto()
    system_network_branch_diagram = auto()
    network_basic = auto()
    service = auto()
    service_kafka = auto()
    network_branch = auto()
    network_branch_kafka = auto()
    network_branch_diagram = auto()
    network_branch_links = auto()
    network_branch_broker_network_links = auto()
    network_current = auto()
    network_current_kafka = auto()
    network_current_diagram = auto()
    network_current_links = auto()

    @property
    def dir(self):
        return "page"


class HtmlTemplatesStorage:
    __templates: Dict[str, Template]

    def __init__(self, templates_path: str):
        self.__templates = {}
        self.__load_templates(templates_path)

    def __load_templates(self, templates_path):
        for t in [HtmlComponentTemplateName, HtmlPageTemplateName]:
            for e in t:
                template_file_name = "{}/handbook/{}/{}.jinja2.html".format(templates_path, e.dir, e.name)
                key = "{}_{}".format(e.name, e.dir)
                self.__templates[key] = self.load_template(template_file_name)

    @staticmethod
    def load_template(fname):
        with open(fname) as file_:
            return Template(file_.read(), enable_async=True)

    def get_page(self, e: HtmlPageTemplateName) -> Template:
        key = "{}_{}".format(e.name, e.dir)
        return self.__templates[key]

    def get_component(self, e: HtmlComponentTemplateName) -> Template:
        key = "{}_{}".format(e.name, e.dir)
        return self.__templates[key]
