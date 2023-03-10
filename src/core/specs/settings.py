from typing import List

from core.yaml import read_yaml


class ServiceCategoryNameWrapper:
    __categories: List[dict]
    __external_categories: List[dict]
    __product_categories: List[dict]

    def __init__(self, categories: dict):
        self.__product_categories = categories["product"]
        self.__external_categories = categories["external"]
        self.__categories = []
        self.__categories.extend(self.__product_categories)
        self.__categories.extend(self.__external_categories)

    @property
    def product_services(self) -> List[dict]:
        return self.__product_categories

    @property
    def all(self) -> List[dict]:
        return self.__categories


class ConfluenceSettings:
    __raw: dict

    def __init__(self, raw: dict):
        self.__raw = raw

    @property
    def link(self) -> str:
        return self.__raw["link"]

    @property
    def space(self) -> str:
        return self.__raw["space"]

    @property
    def handbook_page_title(self) -> str:
        return self.__raw["handbook_page"]

    @property
    def handbook_page(self) -> str:
        return self.__raw["handbook_page"]

    @property
    def parent_system_diagram_page(self) -> str:
        return self.__raw["system_diagram_parent_page"]

    @property
    def parent_component_diagram_page(self) -> str:
        return self.__raw["component_diagram_parent_page"]

    @property
    def has_component_diagram_page(self) -> bool:
        return "component_diagram_parent_page" in self.__raw

    def module_label(self, module_name: str) -> str:
        return self.__raw["modules"][module_name]["label"]

    def module_title(self, module_name: str) -> str:
        return self.__raw["modules"][module_name]["title"]


class Settings:
    __raw: dict

    __service_categories_name: ServiceCategoryNameWrapper

    __confluence: ConfluenceSettings

    __meta_path: str

    def __init__(self, meta_path: str):
        self.__meta_path = meta_path
        self.__raw = read_yaml(meta_path + "/settings.yaml")
        self.__service_categories_name = ServiceCategoryNameWrapper(self.__raw["categories"])
        self.__confluence = ConfluenceSettings(self.__raw["confluence"])

    @property
    def service_categories(self) -> ServiceCategoryNameWrapper:
        return self.__service_categories_name

    @property
    def confluence(self) -> ConfluenceSettings:
        return self.__confluence

    @property
    def markdown_template_vars(self) -> List:
        if "markdown_template_vars" not in self.__raw:
            return []
        return self.__raw["markdown_template_vars"]

    @property
    def component_diagram_fname(self) -> str:
        return "{}/diagrams/component_diagram.xml".format(self.__meta_path)