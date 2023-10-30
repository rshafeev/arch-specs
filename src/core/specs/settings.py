from typing import List, Optional

from core.yaml import read_yaml


class ServiceCategoryNameWrapper:
    __categories: List[dict]
    __external_categories: List[dict]
    __product_categories: List[dict]

    def __init__(self, categories: dict):
        self.__product_categories = categories["product"]
        self.__external_categories = categories["external"]
        self.__categories = []
        if self.__product_categories is not None:
            self.__categories.extend(self.__product_categories)

        if self.__external_categories is not None:
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
    def service_prefix(self) -> str:
        if "service_prefix" not in self.__raw:
            return ""
        return self.__raw["service_prefix"]
    @property
    def link(self) -> str:
        return self.__raw["link"]

    @property
    def space(self) -> str:
        return self.__raw["space"]

    @property
    def clean_services(self) -> List[str]:
        if "clean" in self.__raw and "services" in self.__raw["clean"]:
            return self.__raw["clean"]["services"]
        return []

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
    def diagrams(self) -> Optional[dict]:
        if "diagrams" not in self.__raw:
            return None
        return self.__raw["diagrams"]

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
    def meta_path(self):
        return self.__meta_path

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
