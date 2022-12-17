import logging
from typing import Tuple, Dict, List

from core.specs.settings import Settings
from core.specs.specs import ServicesSpecs
from core.specs.validate.service_spec_validator import ServiceSpecValidator


class SpecsValidator:
    __specs: dict
    __meta_path: str
    __logger: logging.Logger = None
    __settings: Settings

    def __init__(self, meta_path: str):
        self.__settings = Settings(meta_path)
        self.__specs = ServicesSpecs.upload_row_services_specs(meta_path, self.__settings)
        self.__meta_path = meta_path

    @property
    def logger(self) -> logging.Logger:
        if self.__logger is None:
            logger = logging.getLogger("specs.validator")
            logger.handlers.clear()
            logger.propagate = False
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '[%(levelname)-8s] %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            self.__logger = logger
        return self.__logger

    def validate(self) -> Tuple[bool, List[Dict[str, str]], List[Dict[str, str]]]:
        errors = []
        warns = []
        any_service_validator = ServiceSpecValidator(self.__meta_path, self.__specs)
        for e in self.__settings.service_categories.all:
            for service_key in self.__specs[e]:
                service_errors = []
                service_warns = []
                if e in self.__settings.service_categories.product_services:
                    service_result, service_errors, service_warns = any_service_validator.validate(service_key,
                                                                                    self.__specs[e][service_key])
                errors.extend(service_errors)
                warns.extend(service_warns)
        return len(errors) == 0, errors, warns

    def print(self, errors: List[Dict[str, str]], warns: List[Dict[str, str]]):
        for w in warns:
            self.logger.warning("[{}]: {}".format(w["service"], w["warn"]))
        self.logger.info("")
        for e in errors:
            self.logger.error("[{}]: {}".format(e["service"], e["error"]))
        if len(errors) > 0:
            self.logger.error("Errors Count: {}".format(len(errors)))
        if len(warns) > 0:
            self.logger.warning("Warnings Count: {}".format(len(warns)))

        if len(errors) > 0:
            self.logger.error("Validation Results: Failed.")
        else:
            self.logger.info("Validation Results: OK.")
