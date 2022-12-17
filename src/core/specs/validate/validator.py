import json
from enum import Enum, auto

from jsonschema import Draft3Validator

from core.specs.settings import Settings, ServiceCategoryNameWrapper


class SchemaType(Enum):
    service = auto()


class Validator:
    __meta_path: str
    __settings: Settings

    def __init__(self, meta_path: str):
        self.__meta_path = meta_path
        self.__settings = Settings(meta_path)

    def source_schema(self, schema_type: SchemaType) -> dict:
        file_name = "{}/specifications/schema/{}.json".format(self.__meta_path, schema_type.name)
        with open(file_name) as f:
            return json.load(f)

    def validator(self, schema_type: SchemaType) -> Draft3Validator:
        source_schema = self.source_schema(schema_type)
        return Draft3Validator(source_schema)

    @property
    def service_categories(self) -> ServiceCategoryNameWrapper:
        return self.__settings.service_categories
